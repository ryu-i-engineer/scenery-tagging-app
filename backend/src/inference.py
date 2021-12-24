import json

import torch

from commons import get_model, transform_image
from ImgTagDataset import convert_onehot_string_labels_multi

json_path = "../class_labels/scenery_labels.json"
# json_path = "./static/screw_class_name.json"
json_arr = None
with open(json_path, 'r', encoding='utf-8') as file:
    json_arr = json.load(file)

model = get_model(len(json_arr['English']))


def get_prediction(image_byte):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    try:
        tensor = transform_image(image_byte).to(device)
        preds = model.forward(tensor)
    except Exception:
        return 0, 'error'

    pred = preds[0]
    pred[pred > 0.5] = 1
    pred[pred <= 0.5] = 0

    labels = convert_onehot_string_labels_multi(json_arr, pred)

    return json.loads(labels)
