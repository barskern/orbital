from pathlib import Path
import os
from bs4 import BeautifulSoup
from requests import get  # type: ignore
from tqdm import tqdm
from glob import glob
import re

output_dir = "orbital_book"
processed_dir = "orbital_book_p"
base_url = "https://orbital-mechanics.space"

res = get(f"{base_url}/intro.html")

soup = BeautifulSoup(res.text, features="lxml")

# Get html documents
nav = soup.find('nav')
links = nav.find_all('a')
for link in tqdm(links, unit='page'):
    try:
        href = link['href']
        if 'html' in href:
            file_path = Path(f"{output_dir}/{href}")
            if not file_path.exists():
                res = get(f"{base_url}/{href}")
                if res.ok:
                    os.makedirs(file_path.parent, exist_ok=True)
                    with open(file_path, 'w') as f:
                        f.write(res.text)
    except Exception as e:
        print(f"Error: {e}")


for path_s in tqdm(glob(f"{output_dir}/**/*.html"), unit='file'):
    data = None
    path = Path(path_s)
    with open(path, 'r') as f:
        data = BeautifulSoup(f.read(), features='lxml')

    uri_folder = f"{'/'.join(path.parent.parts[1:])}"

    main = data.find(id='main-content')

    elements = data.find_all(href=re.compile('.*'))
    for element in elements:
        href = element.get('href', str())
        if href.startswith('#') or href.startswith('http'):
            continue
        new_href = f"{base_url}/{uri_folder}/{href}"
        # print(f"{href}")
        # print(f"{href} -> {new_href}")
        element['href'] = new_href

    elements = data.find_all(src=re.compile('.*'))
    for element in elements:
        src = element.get('src', str())
        if src.startswith('#') or src.startswith('http'):
            continue
        new_src = f"{base_url}/{uri_folder}/{src}"
        # print(f"{src}")
        # print(f"{src} -> {new_src}")
        element['src'] = new_src

    new_path = Path(f"{processed_dir}/{'/'.join(path.parts[1:])}")
    os.makedirs(new_path.parent, exist_ok=True)
    with open(new_path, 'w') as f:
        f.write(str(data))

    break
