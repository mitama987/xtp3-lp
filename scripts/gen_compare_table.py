"""Generate the plan-comparison table image via OpenAI gpt-image-2 in brand tone.

紙白×インク黒×くすみオレンジで、4 列 × 10 行のミニマルな比較表を 1536x1024 で生成。

Usage:
    uv run --with pillow python scripts/gen_compare_table.py [--force]
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
OUT_PNG = OUT_DIR / "compare_table.png"
OUT_WEBP = OUT_DIR / "compare_table.webp"

PROMPT = """日本のSaaS LP用 "プラン比較表" 図、横長 1536x1024 (16:9)。

世界観: ブランド既存トーン厳守。
- 背景: 紙白 (#FCFAF5) 全面マット紙質。極淡いドット薄く敷く程度。グラデネオン・3D・グラスモーフィズム・絵文字・ノイズ・写実NG。
- フォント: モダン日本語サンセリフ極太 (Noto Sans JP / Inter ベース)。明朝NG。日本語正確、誤字NG、ローマ字混入NG。
- Notion / Stripe / Linear に近い品の良いミニマル LP 図解。

構造: 中央寄せの 4 列 × 10 行のテーブル。表全体の角は 12px 角丸、外周に薄い 1px 枠線 (#E8E2D4)。各行間は薄いグレー (#E8E2D4) の 1px 横罫線。表のセル内余白は 18px。

ヘッダー行 (1 行目、黒背景 #1A1A1A、白文字、極太 26pt):
- 1 列目: (空欄)
- 2 列目: 「無料」
- 3 列目: 「買い切り＋アドオン」(他より少しだけ幅広)
- 4 列目: 「フル買切り」

データ行 (各行 紙白背景、黒文字 22pt、1 列目は左寄せ・他は中央寄せ):
- 価格 / ¥0 / ¥2,980〜 / ¥19,800
- 定期投稿 / ○ / ○ / ○
- 予約投稿 / — / ○ / ○
- ランダム投稿 / — / ○ / ○
- 複数アカウント / 1つまで / 無制限 / 無制限
- AIクレジット / — / 1,000pt / 1,000pt
- アドオン / — / 1つ同梱＋追加可 / 全5種同梱
- 新機能の即時利用 / — / 基本機能のみ / ○
- サポート / — / ○ / ○

色強調:
- 3 列目「買い切り＋アドオン」だけ、データセル全部の背景を極淡いオレンジ (#FFE9DC) に。文字は黒のまま。
- ヘッダーの 3 列目セルは黒背景の中で右上に小さなオレンジ円 + 白文字「人気」のミニバッジを配置。
- 「○」記号はくすみオレンジ (#E8632B) の細いストロークのチェックマーク (Lucide / Heroicons 風の ✓)。
- 「—」記号は薄グレー (#9A958A) のダッシュ。

四辺に 80px のセーフエリア。タイトルや凡例は描かない (HTML 側で配置するため)。"""


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

    print(f"Generating compare-table with {model} 1536x1024 ...", file=sys.stderr)
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
