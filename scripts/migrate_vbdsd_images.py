import os
import re
from tqdm import tqdm

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

img_pattern = re.compile("^\d{8}\-\d{6}\.jpg$")
for img_name in tqdm(os.listdir(os.path.join(PROJECT_DIR, "logs", "vbdsd"))):
    if not img_pattern.match(img_name):
        continue
    date = img_name[:8]
    dst_dir = os.path.join(PROJECT_DIR, "logs", "helios", date)
    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir)

    os.rename(
        os.path.join(PROJECT_DIR, "logs", "vbdsd", img_name), os.path.join(dst_dir, img_name)
    )
