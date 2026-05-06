"""Generate 5 LP section keyvisuals via OpenAI gpt-image-2 in the existing brand tone.

紙白×インク黒×くすみオレンジ+モダンサンセリフを継承して、各セクションを 16:9 (1536x1024)
の集合キービジュアルに統合する。

Usage:
    uv run --with pillow python scripts/gen_section_keyvisuals.py [section ...]

引数なしの場合は全セクションを順に生成。引数で `why features metrics addons pricing` を
個別指定すれば部分生成・再生成が可能。
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

SHARED_TONE = """世界観: ブランド既存トーンを厳守。
- 背景: 紙白 (#F5F1E6) のフラットマット紙質。極々淡いドット/罫線テクスチャを薄く敷くだけ。グラデネオン・3D・グラスモーフィズム・絵文字・ノイズはNG。
- 主インク色: 深い黒 (#1A1A1A)。
- アクセント色: くすみオレンジ (#E8632B) を要所のみ（数字/キーワード/ミニマル線画アイコン）。
- フォント: モダンな日本語サンセリフ (Noto Sans JP / Inter ベース、極太)。明朝NG。
- トーン: Notion / Stripe / Linear に近い品の良いミニマル LP イラスト。フォトリアルNG、ベクター線画+タイポグラフィ表現。
- 四辺に 80px 程度のセーフエリア確保。
- 日本語を正確に描画。ローマ字混入NG・誤字NG。"""

SECTIONS = {
    "why": {
        "filename": "why_keyvisual",
        "prompt": f"""日本のSaaS LP用 "選ばれる3つの理由" を 1 枚に統合した、横長 16:9 (1536x1024) のキービジュアル画像。

{SHARED_TONE}

レイアウト:
- 上部中央に小さな "Why XToolsPro3" 系のオレンジeyebrowラベル
- 1行3カラム。各カラムは中央寄せ、各カラム間は薄い 1px 縦罫線 (#D4CDBA)。
- 各カラム上部にミニマル線画アイコン、左上に "01"〜"03" のオレンジ数字、その下に黒の極太見出し、最下部に小さい補足文 (黒70%)。

カラム内容（日本語を正確に）:
- 01: アイコン=Xロゴ+鍵 / 見出し=「API不要、IDとパスだけ。」 / 補足=「面倒なAPI申請ゼロ」
- 02: アイコン=複数ポストカードがランダム時刻で散らばる線画 / 見出し=「ランダム投稿で エンゲージメント 2.5倍。」（"2.5倍" だけオレンジで強調） / 補足=「100件プールから人間らしい間隔で配信」
- 03: アイコン=¥0永続バッジ / 見出し=「全プラン 買い切り、月額ゼロ。」（"買い切り" だけオレンジ強調） / 補足=「サブスクなし・永続ライセンス」
""",
    },
    "features": {
        "filename": "features_keyvisual",
        "prompt": f"""日本のSaaS LP用 "主要機能" を 1 枚に統合した、横長 16:9 (1536x1024) のキービジュアル画像。

{SHARED_TONE}

レイアウト:
- 上部中央に "主要機能 / Features" の小さなオレンジeyebrow。
- 3列 × 2行のグリッド (合計6セル)。各セル間に薄い 1px 仕切り線 (#D4CDBA)。
- 各セル: 上部にミニマル線画アイコン、その下に黒の極太見出し1行、さらに下に1〜2行の小さな補足文 (黒70%)。

セル内容（日本語を正確に。"機能名:補足" の形式で）:
- ランダム投稿エンジン / 100件プール × 重複防止 × 時間ランダマイザー
- アカウント別プロキシ / 連鎖凍結を防ぐ多重IP分散
- コミュニティ自動投稿 / Xコミュニティへ濃いユーザーへ届ける
- 自動DM返信 / 受信DM＋リクエスト承認をテンプレ自動化
- Amazon在庫復活アラート / Keepa連携で復活瞬間に自動投稿
- AI投稿生成 / GPT-4o & Gemini で投稿文を量産
""",
    },
    "metrics": {
        "filename": "metrics_keyvisual",
        "prompt": f"""日本のSaaS LP用 "実績ハイライト" を 1 枚に統合した、横長 16:9 (1536x1024) のキービジュアル画像。

{SHARED_TONE}

レイアウト:
- 上部中央に "実績ハイライト / Achievements" の小さなオレンジeyebrow。
- 横並び3カラム。各カラム中央に巨大な数字 (黒・極太、もしくはアクセントオレンジ)、その下に小さい補足文 (黒)。
- カラム間は薄い 1px 縦罫線 (#D4CDBA)。

カラム内容（日本語を正確に）:
- 01: 巨大な「3件」 / 補足=「フォロワー31人のサブ垢で、1日で3件成約 (合計¥15,000)」
- 02: 巨大な「+900%」 / 補足=「1日150ポストを2ヶ月で、プロフィールアクセス9倍」
- 03: 巨大な「18回/日」 / 補足=「ファン化長文+note誘導戦略で、過去最大のプロフクリック数」

数字部分はオレンジ (#E8632B) で表示し視線を引く。
""",
    },
    "addons": {
        "filename": "addons_keyvisual",
        "prompt": f"""日本のSaaS LP用 "アドオンパック5種" を 1 枚に統合した、横長 16:9 (1536x1024) のキービジュアル画像。

{SHARED_TONE}

レイアウト:
- 上部中央に "アドオンパック / Add-ons" の小さなオレンジeyebrow と、メイン見出し「必要な機能だけ、あとから足せる。」 (黒・極太)。
- 5カラム横並び。各カラムは紙白カード調、薄い 1px 枠線 (#D4CDBA)、角丸8px。
- 各カラム: 上部にミニマル線画アイコン、その下にパック名 (黒・極太)、価格 (オレンジ・極太)、最下部に1行の概要 (黒70%)。

カラム内容（日本語を正確に。絵文字は使わず線画で）:
- AI生成パック / ¥4,000 / ランダム投稿+AI+スプシ取込
- エンゲージメントパック / ¥4,000 / 自動いいね+フォロー+リプライ
- マルチアカウントパック / ¥5,000 / プロキシ+一括登録+共通設定
- コミュニティパック / ¥4,000 / コミュニティ自動投稿
- Amazon在庫復活パック / ¥6,000 / Keepa連携+在庫監視+自動投稿
""",
    },
    "pricing": {
        "filename": "pricing_keyvisual",
        "prompt": f"""日本のSaaS LP用 "3プラン横並び" を 1 枚に統合した、横長 16:9 (1536x1024) のキービジュアル画像。

{SHARED_TONE}

レイアウト:
- 上部中央に "料金プラン / Pricing" の小さなオレンジeyebrow。
- 3カラム横並びの "比較カード"。中央の "買い切り＋アドオン" カードは黒背景+白文字でひときわ目立つ (人気No.1 のオレンジ丸バッジを上端中央)。両脇は紙白背景。
- 各カードは: 上部にプラン名 (小)、その下に巨大な価格 (極太)、その下に5〜6行の特徴箇条書き (チェックはオレンジ、非対応は薄グレーのダッシュ)。
- 最下部に小さなボタン風の長方形 (テキスト1行) がカード幅で1つずつ。

カード内容（日本語を正確に）:
- 左: 無料版 / ¥0 (永続) / 定期投稿(基本)・1アカウント限定・期間制限なし・AI機能なし(×)・複数アカウント非対応(×) / ボタン風: 無料で始める
- 中央 (黒背景・人気No.1バッジ): 買い切り＋アドオン / ¥2,980〜 (一括) / 全基本機能 無制限・複数アカウント対応・AIクレジット 1,000pt・アドオン1つ同梱・アドオン追加購入OK・永続ライセンス / ボタン風: このプランを購入
- 右: フル買切り / ¥19,800 (一括) / 全機能+全5アドオン同梱・単品計¥23,000相当・¥3,200お得・AIクレジット 1,000pt・新機能の即時利用・永続ライセンス / ボタン風: フル装備で買う
""",
    },
}


def generate(name: str, cfg: dict, api_key: str, model: str) -> None:
    prompt = SECTIONS[name]["prompt"]
    fname = SECTIONS[name]["filename"]
    out_png = OUT_DIR / f"{fname}.png"
    out_webp = OUT_DIR / f"{fname}.webp"

    payload = json.dumps(
        {"model": model, "prompt": prompt, "size": "1536x1024", "n": 1}
    ).encode()

    print(f"[{name}] generating with {model} 1536x1024 ...", file=sys.stderr)
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
        print(f"[{name}] HTTPError {e.code}: {body[:1500]}", file=sys.stderr)
        raise

    item = result["data"][0]
    if "b64_json" in item:
        png_bytes = base64.b64decode(item["b64_json"])
    else:
        with urllib.request.urlopen(item["url"], timeout=120) as r:
            png_bytes = r.read()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_png.write_bytes(png_bytes)
    Image.open(BytesIO(png_bytes)).convert("RGB").save(
        out_webp, "WEBP", quality=86, method=6
    )
    print(f"[{name}] wrote {out_png.name} + {out_webp.name}")


def main() -> int:
    cfg = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    api_key = cfg["openaiApiKey"]
    model = cfg.get("openaiImageModel", "gpt-image-2")

    targets = sys.argv[1:] if len(sys.argv) > 1 else list(SECTIONS.keys())
    unknown = [t for t in targets if t not in SECTIONS]
    if unknown:
        print(f"Unknown sections: {unknown}. Valid: {list(SECTIONS)}", file=sys.stderr)
        return 2

    for name in targets:
        generate(name, cfg, api_key, model)
    return 0


if __name__ == "__main__":
    sys.exit(main())
