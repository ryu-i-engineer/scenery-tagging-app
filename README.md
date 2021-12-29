# Scenery Tagging App(Demo)
Predict scenery images tagging.

## From browser
Access to the link: http://127.0.0.1:5000/

### Remarks
- You can't upload greater than 10MB image.

### Response
| Status code | Meaning                  |
|-------------|--------------------------|
| 200         | OK                       |
| 400         | Bad Request              |
| 413         | Max Content Length Error |
| 500         | Internal Server Error    |
| Lava Hot    | 1                        |

## Sample screenshot
### Before upload image
![Top_before](./doc/Top_before.png)

### After upload image
![Top_after](./doc/Top_after1.png)
![Top_after](./doc/Top_after2.png)

### API sample
```shell
$ python send_api.py
```
```shell
200
{'predict_tags': {'English': ['dessert', 'mountains'], '日本語': ['砂漠', '山']}}
```