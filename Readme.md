# Overworked Graphic Designer

## What purpose will this serve

In images with text, besides recognizing it (which is what OCR does), there are other interesting things one can do. 

Say:
- Identify character boundaries
- Identify font used, it's weight, italicization etc
- Identify text color
- Train a GAN to remove text
- Still do OCR if you wish to

At ImageTranslate(https://www.imagetranslate.com?ref=github), we need such datasets often and that too in different languages and scripts.
Obviously gathering such a dataset isn't easy. But we *can* create one.

## Something like this
Each of these were generated

![collage](https://i.imgur.com/gYYVovp.png)

## Dataset creation

Dataset should have diverse:

1. Backgrounds : Gathered from Unsplash
2. Foreground/Text color: Gathered from user-generated palletes
3. Scripts: Gathered words from wordlists
4. Fonts: Gathered from Google Fonts

## Initial setup

You will need a sample [assets.tar](https://drive.google.com/file/d/14zzjid989dSKFLcLVOZuoj-K0IV1mwN_/view?usp=sharing) like this. Unzip it in your project folder.
The assets folder has subdirectories to which you can add your own backgrounds, palettes and wordlists.

Google fonts are excluded from the tar as it is a huge repo in itself.
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

## Directly using in you program without API

- Clone this repo and copy `work.py` to your codebase.


```python
from work import load_assets, shuffle_assets, generate_data

# Initialize assets
load_assets()
shuffle_assets()

# Generate some data and decode as PIL images 
output = generate_data()
image = Image.open(BytesIO(base64.b64decode(response["image"])))
mask = Image.open(BytesIO(base64.b64decode(response["mask"])))
```

## What is happening behind the scenes

- Lot of python random
- Trasformations with the elegant PIL library
- Euclidean space calculations for colors

The code is rather simple to understand and annotated with ample comments if you're interested.