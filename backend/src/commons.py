import io

import albumentations as alb
import numpy as np
import torch
from albumentations.pytorch import ToTensorV2
from PIL import Image
from transformers import BeitFeatureExtractor, BeitModel

from ImgTagLitModule import BeiTNet

IMG_SIZE = 224


def get_model(class_num):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # set up model
    beit_model = BeitModel.from_pretrained(
        "microsoft/beit-base-patch16-224-pt22k-ft22k"
    )
    model = BeiTNet(beit_model, class_num).to(device)
    model.load_state_dict(torch.load("../models/scenery_beit_model.pt"))
    model.eval()
    return model


def transform_image(image_bytes):
    beit_feature_extractor = BeitFeatureExtractor.from_pretrained(
        "microsoft/beit-base-patch16-224-pt22k-ft22k"
    )
    augmentation = alb.Compose(
        [
            alb.Resize(height=IMG_SIZE, width=IMG_SIZE),
            ToTensorV2(),
        ]
    )
    image = Image.open(io.BytesIO(image_bytes))
    image = augmentation(image=np.squeeze(image))["image"]
    image = beit_feature_extractor(images=image, return_tensors="pt")[
        "pixel_values"
    ].squeeze(0)
    image = np.clip(image, 0, 1)
    return image.unsqueeze(0)
