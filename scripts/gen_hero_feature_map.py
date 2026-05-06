"""Generate the Hero feature-map keyvisual via OpenAI gpt-image-2 in brand tone.

中央放射型マインドマップ図。紙白×インク黒×くすみオレンジ。
1536x1024 (16:9) で生成し、PNG + WebP を assets/images/ に出力。

Usage:
    uv run --with pillow python scripts/gen_hero_feature_map.py [--force]
"""
from __future__ import annotations

import base64
import json
import sys
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image

DATA_JSON = Path(
    r"C:\Users\mitam\Desktop\work\50_ブログ\.obsidian\plugins\buzzblog-generator\data.json"
)
OUT_DIR = Path(__file__).resolve().parent.parent / "assets" / "images"
OUT_PNG = OUT_DIR / "feature_map.png"
OUT_WEBP = OUT_DIR / "feature_map.webp"

PROMPT = """日本のSaaS LP用 "機能マップ" 中央放射型マインドマップ図、横長 1536x1024 (16:9)。

世界観: ブランド既存トーン厳守。
- 背景: 紙白 (#FCFAF5) のフラットマット紙質。極々淡いドットテクスチャを薄く敷くだけ。グラデネオン・3D・グラスモーフィズム・絵文字・ノイズはNG。
- フォント: モダン日本語サンセリフ極太 (Noto Sans JP / Inter ベース)。明朝NG。日本語を正確に描画、誤字・ローマ字混入NG。
- トーン: Notion / Stripe / Linear に近い品の良いミニマル LP 図解。
- 接続線: 細い 2px のグレー曲線 (#D4CDBA)、矢印は控えめ。
- 四辺に 64px セーフエリア。

中央ハブ:
- 画面中央に黒 (#1A1A1A) 角丸長方形 (角丸 12px、約 360×130px)。
- 中に白の極太大文字「XToolsPro3」(48–56pt)、すぐ下に白70%の小文字「API不要・ブラウザ自動化」(20pt)。

中央コア機能 (中央ハブ周囲、紙白の角丸長方形 200×52px、薄い 1px 枠線 #E8E2D4、黒の極太文字 22pt):
- 中央左側: 「定期投稿」「予約投稿」「画像投稿」「設定」を縦に並べ、矢印で中央に接続。
- 中央右側: 「ダッシュボード」「分析機能」「メール通知」「アカウント管理」を縦に並べ、矢印で中央に接続。

外周クラスタ (4 グループ):
- 左上: 親ハブ「AI生成パック」(紙白カード、薄枠線、黒太字)。葉ノードとして「ランダム投稿」「AIモード」「スプシ取込」「画像プール」の 4 つを左に小さい角丸タグで配置、親ハブから矢印で接続。
- 右上: 親ハブ「エンゲージメントパック」。葉ノード「自動いいね」「自動フォロー」「自動リプライ」「自動DM」を右に配置。
- 左下: 親ハブ「Amazon在庫復活パック」。葉ノード「Keepa連携」「在庫監視」「自動投稿」を左に配置。
- 右下: 親ハブ「コミュニティパック」。葉ノード「マルチアカウント」「コミュニティ自動投稿」を右に配置。

カラー強調 (1 つだけオレンジで主力強調):
- 「AI生成パック」の親ハブだけ、くすみオレンジ (#E8632B) 塗り＋白文字でハイライト。他の 3 親ハブは紙白＋黒文字。
- 葉ノードのタグは全て紙白 (#F5F1E6) 背景、薄い枠線、黒の極太文字 18pt。色違いの塗りはNG。

中央ハブを基準に、左右上下に均等に放射状配置。中央コア機能と外周クラスタの間は十分な余白で読みやすく。葉ノードどうしは縦に揃え、行間を一定に。"""


def main() -> int:
    force = "--force" in sys.argv[1:]
    if OUT_WEBP.exists() and not force:
        print(f"Already exists: {OUT_WEBP}. Use --force to overwrite.", file=sys.stderr)
        return 0

    cfg = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    api_key = cfg["openaiApiKey"]
    model = cfg.get("openaiImageModel", "gpt-image-2")

    payload = json.dumps(
        {"model": model, "prompt": PROMPT, "size": "1536x1024", "n": 1}
    ).encode()

    print(f"Generating Hero feature map with {model} 1536x1024 ...", file=sys.stderr)
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTPError {e.code}: {body[:1500]}", file=sys.stderr)
        raise

    item = result["data"][0]
    if "b64_json" in item:
        png_bytes = base64.b64decode(item["b64_json"])
    else:
        with urllib.request.urlopen(item["url"], timeout=120) as r:
            png_bytes = r.read()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_PNG.write_bytes(png_bytes)
    Image.open(BytesIO(png_bytes)).convert("RGB").save(
        OUT_WEBP, "WEBP", quality=86, method=6
    )
    print(f"Wrote {OUT_PNG.name} + {OUT_WEBP.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
