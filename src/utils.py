import re

def safe_filename(name: str):
    return re.sub(r'[\\/:"*?<>|]+', "_", name)

def normalize_bbox(bbox, w, h):
    x, y, bw, bh = bbox
    return [(x + bw/2)/w, (y + bh/2)/h, bw/w, bh/h]
