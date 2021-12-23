import json
import os

import albumentations as alb
import numpy as np
import pandas as pd
import pytorch_lightning as pl
import torch
from albumentations.pytorch import ToTensorV2
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from torch.utils.data import DataLoader, Dataset
from transformers import BeitFeatureExtractor

beit_feature_extractor = BeitFeatureExtractor.from_pretrained(
    "microsoft/beit-base-patch16-224-pt22k-ft22k"
)


def binarize_df(label_path):
    df = pd.read_csv(label_path)
    df = df.dropna(axis=1, how="all")  # save memory and process usage
    df = df.fillna("None")  # to avoid error

    mlb = MultiLabelBinarizer()
    result = mlb.fit_transform(
        df.drop(columns=["filenames"]).values
    )  # drop not tagging cols

    bin_df = pd.DataFrame(result, columns=mlb.classes_)  # drop non-useless col.
    if "None" in bin_df.columns:
        bin_df = bin_df.drop("None", axis=1)

    return df.drop(df.columns[1:], axis=1).join(bin_df)


def convert_onehot_string_labels(label_string, label_onehot):
    labels = []
    for i, label in enumerate(label_string):
        if label_onehot[i]:
            labels.append(label)
    if len(labels) == 0:
        labels.append("NONE")
    return labels


def convert_onehot_string_labels_multi(label_string_arr, label_onehot):
    label_dict = {}
    for language in label_string_arr:
        label_dict[language] = convert_onehot_string_labels(
            label_string_arr[language], label_onehot
        )

    return json.dumps(label_dict, ensure_ascii=False).encode("utf-8")


class ImgTagDataset(Dataset):
    """
    Create dataset for multi-label classification.

    Parameters
    ----------------
    df : pd.DataFrame
        Pandas DataFrame object.
        It must be contained "filename", and multi-binarized encoded columns.

    root_dir: str
        Root directory of Datasets
    """

    def __init__(self, df: pd.DataFrame, root_dir, transform):
        self.df = df
        self.root_dir = root_dir
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, index):
        d = self.df.iloc[index]
        image = Image.open(
            os.path.join(self.root_dir, "images", d["filenames"])
        ).convert("RGB")
        image = self.transform(image=np.squeeze(image))["image"]
        image = beit_feature_extractor(images=image, return_tensors="pt")[
            "pixel_values"
        ].squeeze(0)
        # image = np.clip(image, 0, 1)
        label = torch.tensor(d[1:].tolist(), dtype=torch.float32)
        return image, label


class ImgTagDataModule(pl.LightningDataModule):
    def __init__(
        self,
        root_dir: str,
        train_val_df: pd.DataFrame,
        test_df: pd.DataFrame = None,
        batch_size=32,
        img_size=224,
        mean=(0.5, 0.5, 0.5),
        std=(0.5, 0.5, 0.5),
    ):

        super().__init__()
        self.root_dir = root_dir
        self.train_val_df = train_val_df
        self.test_df = test_df
        self.batch_size = batch_size

        self.train_ds = None
        self.val_ds = None
        self.test_ds = None

        # pre-processing
        self.train_augmentation = alb.Compose(
            [
                alb.RandomResizedCrop(
                    width=img_size, height=img_size, scale=(0.5, 1.0)
                ),
                alb.SafeRotate(),
                alb.RandomBrightnessContrast(
                    brightness_limit=0.1, contrast_limit=0.2, p=0.5
                ),
                alb.ImageCompression(quality_lower=90, quality_upper=100, p=0.5),
                alb.GaussianBlur(blur_limit=(1, 3)),
                # alb.CLAHE(clip_limit=6.0, tile_grid_size=(8, 8), p=1),
                alb.HorizontalFlip(),
                # alb.Normalize(mean, std),
                ToTensorV2(),
            ]
        )

        self.test_val_augmentation = alb.Compose(
            [
                alb.Resize(height=img_size, width=img_size),
                # alb.Normalize(mean=mean, std=std),
                ToTensorV2(),
            ]
        )

    def prepare_data(self):
        pass

    # Trainer.fit()ではtrain/valのDatasetを、Trainer.test()ではtestのDatasetを生成
    def setup(self, stage=None):
        if stage == "fit" or stage is None:
            train_df, val_df = train_test_split(self.train_val_df, test_size=0.2)

            self.train_ds = ImgTagDataset(
                train_df, self.root_dir, self.train_augmentation
            )
            self.val_ds = ImgTagDataset(
                val_df, self.root_dir, self.test_val_augmentation
            )

        if stage == "test" or stage is None:
            self.test_ds = ImgTagDataset(
                self.test_df, self.root_dir, self.test_val_augmentation
            )

    def train_dataloader(self):
        return DataLoader(
            self.train_ds,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=0,
            pin_memory=True,
        )

    def val_dataloader(self):
        return DataLoader(
            self.val_ds, batch_size=self.batch_size, num_workers=0, pin_memory=True
        )

    def test_dataloader(self):
        return DataLoader(
            self.test_ds, batch_size=self.batch_size, num_workers=0, pin_memory=True
        )
