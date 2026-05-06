"""Generate the PAIN section keyvisual via OpenAI gpt-image-2.

Brand tone (paper white + ink black + dusky orange + sans-serif) を維持して
"こんな悩み、毎日続いていませんか？" 4項目を 2x2 集約した 16:9 キービジュアルを生成する。

Usage:
    uv run python scripts/gen_pain_image.py
"""
from __future__ import annotations

import base64
import json
import sys
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image

DATA_JSON = Path(
    r"C:\Users\mitam\Desktop\work\50_ブログ\.obsidian\plugins\buzzblog-generator\data.json"
)
OUT_DIR = Path(__file__).resolve().parent.parent / "assets" / "images"
OUT_PNG = OUT_DIR / "pain_keyvisual.png"
OUT_WEBP = OUT_DIR / "pain_keyvisual.webp"

PROMPT = """日本のSaaS LP用の "悩み訴求セクション" を 1 枚に統合した、横長 16:9 (1536x1024) のキービジュアル画像。

世界観: ブランド既存トーンを厳守。
- 背景: 紙白 (#F5F1E6) のフラットマット紙質。極々淡い罫線・ドット模様のテクスチャを薄く敷くだけ。グラデネオン・3D・グラスモーフィズム・絵文字・ノイズはNG。
- 主インク色: 深い黒 (#1A1A1A)。
- アクセント色: くすみオレンジ (#E8632B) を要所のみ（数字・キーワード・小アイコンの線色）。
- フォント: モダンな日本語サンセリフ（Noto Sans JP / Inter ベース、太字）。明朝NG。

レイアウト:
- 2x2 グリッド。各セルの中央上部にミニマル線画アイコン、左上に小さい "01〜04" のオレンジ数字、その下に黒の極太見出し（日本語）と、さらに小さい補足文（黒70%）。
- 4セル間に薄い 1px の分割線（#D4CDBA）。
- 各セルに余白 56px、テキストは中央寄せ。

セル内容（日本語を正確に描画。ローマ字混入NG・誤字NG）:
- 01: アイコン=止まった砂時計の線画 / 見出し=「毎回手動で投稿するのが面倒。」 / 補足=「続かない。」
- 02: アイコン=札束の上に "$200" の小タグ / 見出し=「X APIに月 $200 は払えない。」 / 補足= なし
- 03: アイコン=連鎖した鎖アイコン+赤橙のヒビ / 見出し=「同じIPで運用していて、芋づる凍結が怖い。」 / 補足= なし
- 04: アイコン=未読バッジ付きDMアイコン / 見出し=「DM返信が追いつかず、機会損失している。」 / 補足= なし

トーン: Notion / Stripe / Linear に近い品の良いミニマル LP イラスト。情報密度は低めで、読みやすさ重視。フォトリアルNG、ベクター線画+タイポグラフィ表現。
余白を十分とり、四辺に 80px 程度のセーフエリアを確保。
"""


def main() -> int:
    cfg = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    api_key = cfg["openaiApiKey"]
    model = cfg.get("openaiImageModel", "gpt-image-2")

    payload = json.dumps(
        {
            "model": model,
            "prompt": PROMPT,
            "size": "1536x1024",
            "n": 1,
        }
    ).encode()

    print(f"Generating PAIN keyvisual with model={model} size=1536x1024 ...", file=sys.stderr)
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
        return 1

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
    print(f"Wrote {OUT_PNG} and {OUT_WEBP}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
