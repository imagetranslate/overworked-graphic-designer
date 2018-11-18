import requests
from bs4 import BeautifulSoup
import re
import time
from tqdm import tqdm
import io
import random

USER_AGENTS = [x.strip() for x in io.open("user-agents.txt").readlines()]

def get_palettes(url):

    palettes = []
    headers = requests.utils.default_headers()
    headers.update(
    {
        'User-Agent': random.choice(USER_AGENTS),
    }
)
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, features="html.parser")
        
        for x in soup.findAll("a", {"class": "palette"}): 
            palette = []
            for a in x.findAll("div", {"class": "c"}): 
                color = re.findall(r"#[^;]+;", str(a))[0][:-1]
                palette.append(color)
            palettes.append(palette)   
    
    return palettes


if __name__ == "__main__":

    base_url = "https://www.colourlovers.com/palettes/most-comments/all-time/meta?page="

    for page in tqdm(range(5000)):
        time.sleep(0.5)
        url = "https://www.colourlovers.com/ajax/browse-palettes/_page_{}?section=most-comments&period=all-time&view=meta&channelID=0".format(page)
        
        with open("colourlovers.csv", "a") as f:

            for palette in get_palettes(url):
                f.write(",".join(palette) + "\n")


