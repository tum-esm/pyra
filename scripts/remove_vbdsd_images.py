import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_PATH = os.path.join(PROJECT_DIR, "logs", "vbdsd")

image_names = list(sorted([f for f in os.listdir(IMG_PATH) if f.endswith(".jpg")]))

delete_count = 0

for n in image_names:
    os.remove(os.path.join(IMG_PATH, n))
    delete_count += 1

print(f"deleted {delete_count} images")
