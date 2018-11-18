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

Every image in the dataset has this schema

```json
{
    "image": "path-to-image",
    "text_value": "hello",
    "text_color": "#13EEF0",
    "font_face": "Helvetica Neue",
    "category": "SANS-SERIF",
    "italicization": false,
    "weight": 400,
    "script": "Latin",
    "language": "English",
    "text_mask": "path-to-text-mask"
}
```

Details of each attribute:

- `image` holds path to the actual data file
- `text_value` holds the text rendered.
- `text_color` is color as hex string.
- `font_face` holds font-face as Google Fonts names it
- `category` can be one of `SERIF`, `SANS-SERIF`, `HANDWRITING`, `DISPLAY`, `MONOSPACE`
- `italicization` is obvious
- `weight` is as reported by Google Fonts. We need to quantize it later.
- `script` should be one from the scripts of languages we support
- `languages` should be be one from the languages we support
- `text_mask` holds path to image where only the text is stored in white on black background.


TODO

- Add proper assets
- Add API interface