"""Resize source diagrams from Obsidian _attachments into 82_xtp3-lp/assets/images.
Outputs WebP (quality 82) which keeps screenshots crisp at ~1/4 the PNG size.
Run once: python _resize_images.py
"""
from pathlib import Path
from PIL import Image

SRC = Path(r"C:\Users\mitam\Desktop\work\50_ブログ\02_note\01_XToolsPro3\01_LP・販売記事\_attachments")
DST = Path(__file__).parent / "assets" / "images"
DST.mkdir(parents=True, exist_ok=True)

MAP = {
    "diagram_07_feature_map.png":     "feature_map.webp",
    "diagram_02_random_vs_regular.png": "random_flow.webp",
    "diagram_03_proxy_protection.png":  "proxy_protection.webp",
    "diagram_05_amazon_flow.png":       "amazon_flow.webp",
    "diagram_08_community_branch.png":  "community_branch.webp",
    "diagram_09_auto_dm_flow.png":      "auto_dm_flow.webp",
    "diagram_11_developer_profile.png": "developer_profile.webp",
    "diagram_15_buyer_benefits.png":    "buyer_benefits.webp",
}

MAX_W = 1200

for src_name, dst_name in MAP.items():
    src = SRC / src_name
    if not src.exists():
        print(f"[skip] {src} not found")
        continue
    img = Image.open(src)
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (252, 250, 245))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    if img.width > MAX_W:
        h = int(img.height * MAX_W / img.width)
        img = img.resize((MAX_W, h), Image.LANCZOS)
    out = DST / dst_name
    img.save(out, "WEBP", quality=82, method=6)
    kb = out.stat().st_size // 1024
    print(f"[ok] {dst_name}  {img.width}x{img.height}  {kb} KB")

# remove old PNGs from previous run if any
for old in DST.glob("*.png"):
    old.unlink()
    print(f"[clean] removed {old.name}")
print("done.")
