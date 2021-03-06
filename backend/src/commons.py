import io

import torch
from PIL import Image
from transformers import BeitFeatureExtractor, BeitModel

from ImgTagLitModule import BeiTNet

IMG_SIZE = 224
beit_model = BeitModel.from_pretrained("microsoft/beit-base-patch16-224-pt22k-ft22k")
beit_feature_extractor = BeitFeatureExtractor.from_pretrained("microsoft/beit-base-patch16-224-pt22k-ft22k")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def get_model(class_num):
    # set up model
    model = BeiTNet(beit_model, class_num).to(device)
    model.load_state_dict(torch.load("../models/scenery_beit_model.pt"))
    model.eval()
    return model


def transform_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    image = beit_feature_extractor(images=image, return_tensors="pt")[
        "pixel_values"
    ]
    return image
