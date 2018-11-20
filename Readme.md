# Overworked Graphic Designer

## What purpose will this serve

In images with text, besides recognizing it (which is what OCR does), there are other interesting things one can do. 

Say:
- Identify character boundaries
- Identify font used, it's weight, italicization etc
- Identify text color
- Still do OCR if you wish to

Obviously gathering such a dataset isn't easy. But we *can* create one.

## Something like this
Each of these were generated
![collage](https://i.imgur.com/gYYVovp.png)

## Dataset creation

Dataset should have diverse:

1. Backgrounds : Gather from Unsplash
2. Foreground/Text color: Gather from user-generated palletes
3. Scripts: Gather words from wordlists
4. Fonts: Gather from Google Fonts

## Initial setup

The assets folder has subdirectories to which you can add your own backgrounds, palettes and wordlists.

For Google Fonts, clone their repo and copy the folder so that final folder structure looks like:

- assets 
    - fonts
        - google-fonts
            - apache
            - ufl
            - ofl

And of course, do the obvious `pip install -r requirements.txt`

## Schema

API response for `/generate` endpoint

```json
{
    "image": "base64-encoded-png",
    "mask": "base64-encoded-png",
    "text_value": "hello",
    "text_color": "#13EEF0",
    "font_face": "Helvetica Neue",
    "category": "SANS-SERIF",
    "italicization": false,
    "weight": 400,
    "script": "Latin",
    "language": "English"
}
```

Details of each attribute:

- `image` holds base64 string of the image PNG.
- `mask` holds base64 string of the mask PNG.
- `text` holds the text rendered.
- `text_color` is color as hex string.
- `font_face` holds font-face as Google Fonts names it
- `category` can be one of `SERIF`, `SANS-SERIF`, `HANDWRITING`, `DISPLAY`, `MONOSPACE`
- `italicization` is obvious
- `weight` is as reported by Google Fonts. We need to quantize it later.
- `script` should be one from the scripts of languages we support
- `language` should be be one from the languages we support


## How to run

If you just want to create a lot of such images
```sh
python work.py
```

If you want to serve it as an API
```sh
python api.py
```

## How to decode API response on client side

```python
import requests
import base64
from io import BytesIO
from PIL import Image

response = requests.get("http://localhost:8000/generate")

if response.status_code == 200:
    response = response.json()
    image = Image.open(BytesIO(base64.b64decode(response["image"])))
    mask = Image.open(BytesIO(base64.b64decode(response["mask"])))


```