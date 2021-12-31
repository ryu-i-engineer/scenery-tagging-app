import json

from commons import get_model, transform_image, device
from ImgTagDataset import convert_onehot_string_labels_multi

json_path = "../class_labels/scenery_labels.json"
json_arr = None
with open(json_path, 'r', encoding='utf-8') as file:
    json_arr = json.load(file)

model = get_model(len(json_arr['English']))


def get_prediction(image_byte: bytes):
    try:
        tensor = transform_image(image_byte).to(device)
        pred = model.forward(tensor)

        pred[pred > 0.5] = 1
        pred[pred <= 0.5] = 0

        labels = convert_onehot_string_labels_multi(json_arr, pred)
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        return None

    return json.loads(labels)
