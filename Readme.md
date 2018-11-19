# Overworked Graphic Designer - OGD

For our business objectives, we need to solve the following problems related to text in images.

## Problems

Given an image with text in it:
1. Identify text color
2. Identify
    - Font-face
    - Italicization
    - Weight
3. Inpainting
4. Recognize the text (we'll use OCR APIs for now)


## Diversity of input

We should be able to handle input that has diverse:

1. Backgrounds
2. Foregrounds / Text colors
3. Scripts
4. Fonts


## Dataset creation

We can create a common dataset to train models for each of the problems above.

It should have diverse:

1. Backgrounds : Gather from Unsplash
2. Foreground/Text color: Gather from user-generated palletes
3. Scripts: Gather words from dictionaries
4. Fonts: Gather from Google Fonts

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


## How to decode base 64 on client side

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