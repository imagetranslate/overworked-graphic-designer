import os
import io
import json
import random
import uuid
from collections import defaultdict, Counter
from annoy import AnnoyIndex
from tqdm import tqdm
from itertools import product
import wcag_contrast_ratio as contrast
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from scipy.stats import mode
from pprint import pprint
import base64
from io import BytesIO

ASSETS_DIR = "assets"

BACKGROUNDS = []
FONTS = defaultdict(list) # Script names are keys
WORDS = defaultdict(list) # Script names are keys
COLOR_INDEX = AnnoyIndex(3, metric="euclidean")
COLOR_COMBINATIONS = {}

GENERATED_IMAGES_DIR = "generated_images"
SAVE_IMAGES_TO_DISK = False

# Just create the directory if it doesn't exist
if not os.path.exists(GENERATED_IMAGES_DIR):
    os.mkdir(GENERATED_IMAGES_DIR)


def load_assets():    
    print("Loading assets")
    print("-"*80)
    global ASSETS_DIR

    # Load all backgrounds

    print("Loading backgrounds")
    global BACKGROUNDS
    BACKGROUNDS_DIR = os.path.join(ASSETS_DIR, "backgrounds")
    
    for bg_filename in tqdm(os.listdir(BACKGROUNDS_DIR)):
        filepath = os.path.join(BACKGROUNDS_DIR, bg_filename)
        BACKGROUNDS.append(filepath)
    print("{} backgrounds loaded\n\n".format(len(BACKGROUNDS)))

    # Load all fonts

    print("Loading fonts")
    global FONTS
    FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

    fonts_json_file_path = os.path.join(FONTS_DIR, "google-fonts.json")
    with io.open(fonts_json_file_path, encoding="utf-8") as f:
        fonts_json = json.load(f)
    
    total_fonts = 0
    for font_info in tqdm(fonts_json["info"]):
        for script in font_info["subsets"]:
            for font in font_info["fonts"]:
                font["font_path"] = os.path.join(FONTS_DIR, font_info["files_path"], font["filename"])
                font["category"] = font_info["category"]
                FONTS[script].append(font)
                total_fonts += 1
    print("Loaded {} fonts across {} scripts\n\n".format(total_fonts, len(FONTS)))

    # Load all words

    print("Loading words")
    global WORDS
    SCRIPTS_DIR = os.path.join(ASSETS_DIR, "scripts")
    total_words = 0

    for script_filename in tqdm(os.listdir(SCRIPTS_DIR)):
        script_filepath = os.path.join(SCRIPTS_DIR, script_filename)
        WORDS[script_filename] = {}

        for lang_filename in os.listdir(script_filepath):
            WORDS[script_filename][lang_filename] = []
            lang_filepath = os.path.join(script_filepath, lang_filename)
            
            with io.open(lang_filepath) as f:
                for word in f:
                    word = word.strip()
                    if len(word) == 0 or len(word) > 30:
                        continue
                    WORDS[script_filename][lang_filename].append(word)
                    total_words += 1
    print("Loaded {} words across {} scripts\n\n".format(total_words, len(WORDS)))

    # Load all colors and color combinations

    print("Loading color and combinations")

    global COLOR_COMBINATIONS
    PALETTES_DIR = os.path.join(ASSETS_DIR, "palettes")
    colors = set()

    for palette_filename in os.listdir(PALETTES_DIR):
        palette_filepath = os.path.join(PALETTES_DIR, palette_filename)
        with io.open(palette_filepath) as f:
            for palette in tqdm(f):
                # Read pallette as Hex
                palette = palette.strip().split(",")
                # Get good combinations as RGB pairs
                color_combinations = get_good_contrast_combinations(palette)
                for combination in color_combinations:
                    color_1, color_2 = combination
                    colors.add(color_1)
                    colors.add(color_2)
                    color_1, color_2 = rgb_to_hex(color_1), rgb_to_hex(color_2)
                    COLOR_COMBINATIONS[color_1] = color_2
                    COLOR_COMBINATIONS[color_2] = color_1
    
    global COLOR_INDEX
    for i, color in enumerate(colors):
        COLOR_INDEX.add_item(i, color)
    
    COLOR_INDEX.build(10)
    print("Loaded {} colors\n\n".format(len(COLOR_COMBINATIONS)))

    print("-"*80)

def hex_to_rgb(color):
        color = color.lstrip("#")
        return tuple(int(color[i:i+2], 16)/255 for i in (0, 2 ,4))

def get_good_contrast_combinations(palette):
  
    
    # palette.append("#ffffff")
    # palette.append("#000000")
    palette = set(palette)

    colors = [hex_to_rgb(color) for color in palette]
    valid_color_combinations = []
    for combination in product(colors, colors):
        color_1 = combination[0]
        color_2 = combination[1]
        if contrast.passes_AA(contrast.rgb(color_1, color_2)):
            valid_color_combinations.append((color_1, color_2))

    return valid_color_combinations

def shuffle_assets():
    global BACKGROUNDS
    random.Random().shuffle(BACKGROUNDS)

    global FONTS
    for script in FONTS:
        random.Random().shuffle(FONTS[script])
    
    global WORDS
    for script in WORDS:
        for language in WORDS[script]:
            random.Random().shuffle(WORDS[script][language])

def generate_random_payload(filters={}):
    payload = {}

    # Pick a random background
    payload["background_path"] = random.choice(BACKGROUNDS)

    # Pick a random script and a random language in it
    
    # Filter scripts if any
    available_scripts = filters.get("scripts", ["latin", "devanagari", "arabic", "cyrillic", "korean"])
    payload["script"] = random.choice(available_scripts)

    available_languages = [x for x in WORDS[payload["script"]].keys()]
    
    # Filter languages if any
    # available_languages = filters.get("languages", available_languages)
    payload["language"] = random.choice(available_languages)
    
    # Pick a random font with given filters
    available_fonts = []
    for font in FONTS[payload["script"]]:
        # Filter weights if specified
        if "weights" in filters and font["weight"] not in filters["weights"]:
            continue

        # Filter category if specified
        if "categories" in filters and font["category"] not in filters["categories"]:
            continue
        
        # Filter italicization if required
        if "styles" in filters and font["style"] not in filters["styles"]:
            continue

        available_fonts.append(font)

    payload["font"] = random.choice(available_fonts)

    # Pick a random word
    payload["word"] = random.choice(WORDS[payload["script"]][payload["language"]])
    
    # Add more words followed by new line or space with 50% probability
    while(random.choice([0,1]) == 0):
        payload["word"] += random.choice([" ", "\n"]) + random.choice(WORDS[payload["script"]][payload["language"]])
    
    return payload

def get_suitable_text_color(image, mask):

    # Find the most common color in the image which this text is covering
    image_np = np.array(image)
    mask_np = np.array(mask)
    text_overlay_np = image_np & mask_np

    useful_pixel_locations = np.nonzero(text_overlay_np)
    pixel_values = image_np[useful_pixel_locations[:-1]]//4*4 # Smoothing

    color = mode(pixel_values).mode[0]
    color = tuple([x/255 for x in color])


    # width, height = image.size
    
    # # Make this smaller to reduce calculations
    # smaller_image = image.resize((300, int(height/(width/300))))

    # # Reduce total colors to simplify common color calculations
    # color_quantized_image = smaller_image.convert("P", palette=Image.ADAPTIVE, colors=256).convert("RGB")
    
    # # Get top 3 most common colors
    # color_counter = Counter(color_quantized_image.getdata())
    # colors = [x[0] for x in color_counter.most_common(3)]

    # # Pick a random color
    # color = random.choice(colors)
    # color = tuple([x/255 for x in color])
    
    # See which 10 colors are closest to this color from the palettes we have.
    global COLOR_INDEX
    closest_colors_from_palettes = COLOR_INDEX.get_nns_by_vector(color, 10)
    closest_colors = [COLOR_INDEX.get_item_vector(x) for x in closest_colors_from_palettes]

    # Get text colors for each of them and choose the one with the highest contrast
    text_colors = [COLOR_COMBINATIONS[rgb_to_hex(x)] for x in closest_colors]
    text_color = text_colors[np.argmax([contrast.rgb(color,hex_to_rgb(x)) for x in text_colors])]
    
    return text_color

def rgb_to_hex(color):
    color = [int(x*255) for x in color]
    return "#{0:02x}".format(color[0]) + "{0:02x}".format(color[1]) + "{0:02x}".format(color[2])

def generate_image_from_payload(payload):

    background = Image.open(payload["background_path"]).convert('RGB')
    width, height = background.size
    padding = min(50, width/10)

    # Choose a font size. Reduce till text box is likely to fit in the background
    divisor = random.choice([5,7,10])
    padding = 30
    while(True):
        font_size = height//divisor
        font_object = ImageFont.truetype(payload["font"]["font_path"], font_size)
        text_width, text_height = font_object.getsize_multiline(payload["word"])
        roi_width = text_width + padding*2
        roi_height = text_height + padding*2

        if roi_height < height and roi_width < width:
            break
        divisor += 1

    # Get a random (left, top)
    random_top = random.randint(0, height - roi_height -1)
    random_left = random.randint(0, width - roi_width - 1)

    # Crop with random box values
    roi = background.crop((random_left, random_top, random_left + roi_width, random_top + roi_height))

    # Draw onto black image as a mask
    mask = Image.new('RGB', (roi.width, roi.height), color="#000000")
    draw_pad = ImageDraw.Draw(mask)
    draw_pad.text((padding, padding/4), payload["word"], font=font_object, fill="#FFFFFF")

    # Get suitable text color
    text_color = get_suitable_text_color(roi, mask)
    
    # Draw onto image
    draw_pad = ImageDraw.Draw(roi)
    draw_pad.text((padding, padding/4), payload["word"], font=font_object, fill=text_color)

    global SAVE_IMAGES_TO_DISK
    if SAVE_IMAGES_TO_DISK:
        filename = "%s.png" % (uuid.uuid4())
        filepath = os.path.join(GENERATED_IMAGES_DIR, filename)
        roi.save(filepath)
    
        mask_filepath = "{}-mask.png".format(filepath[:-4])
        mask.save(mask_filepath)
    else:
        filepath = None
        mask_filepath = None

    roi_buffered = BytesIO()
    roi.save(roi_buffered, format="PNG")

    mask_buffered = BytesIO()
    mask.save(mask_buffered, format="PNG")

    return {
        "text_color": text_color,
        "image": base64.b64encode(roi_buffered.getvalue()),
        "mask": base64.b64encode(mask_buffered.getvalue()),
        "image_filepath": filepath,
        "mask_filepath": mask_filepath
    }    

def generate_data(filters):

    try:
        payload = generate_random_payload(filters)
    except Exception:
        output = {
            "message": "Please check your filters"
        }
        return output

    try:
        image = generate_image_from_payload(payload)

        output = {
            "image": image["image"],
            "mask": image["mask"],
            "text": payload["word"],
            "text_color": image["text_color"],
            "font_face": payload["font"]["full_name"],
            "category": payload["font"]["category"],
            "italicization": payload["font"]["style"] == "italic",
            "weight": int(payload["font"]["weight"]),
            "script": payload["script"],
            "language": payload["language"],

            "image_filepath": image["image_filepath"],
            "mask_filepath": image["mask_filepath"]
        }

    except Exception:
        return generate_data(filters)
    
    return output
    

if __name__ == "__main__":
    
    load_assets()
    shuffle_assets()

    SAVE_IMAGES_TO_DISK = True
    
    filters = {}
    filters = {
        # "scripts": ["korean"],
        # "weights": ["800"]
        # "style": ["italic"]
    }

    while(True):
        output = generate_data(filters)
        if "message" in output:
            print(output)
        else:
            print("Generated: ", output["image_filepath"])
