import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_PATH = os.path.join(PROJECT_DIR, "logs", "vbdsd")

image_names = list(sorted([f for f in os.listdir(IMG_PATH) if f.endswith(".jpg")]))
kept_times = {}

for n in image_names:
    if int(n[11:13]) % 2 == 1:
        continue
    if n[:13] in kept_times:
        continue
    kept_times[n[:13]] = n.replace("-raw.jpg", "").replace("-processed.jpg", "")

delete_count = 0

for n in image_names:
    if (n[:13] not in kept_times) or (not n.startswith(kept_times[n[:13]])):
        os.remove(os.path.join(IMG_PATH, n))
        delete_count += 1

print(f"deleted {delete_count} images")
print(f"kept {len(image_names) - delete_count} images")
