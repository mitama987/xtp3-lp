"""Generate per-item LP card images via OpenAI gpt-image-2 in the brand tone.

紙白×インク黒×くすみオレンジ+モダンサンセリフを継承し、各セクションを
1024x1024 の正方形カード画像に分解生成する。

Usage:
    uv run --with pillow python scripts/gen_section_keyvisuals.py
    uv run --with pillow python scripts/gen_section_keyvisuals.py pain
    uv run --with pillow python scripts/gen_section_keyvisuals.py pain.01
    uv run --with pillow python scripts/gen_section_keyvisuals.py pain.manual
    uv run --with pillow python scripts/gen_section_keyvisuals.py pain.01 metrics.01 --force

引数なしで全 21 枚を順次生成。section 単独で当該セクション全枚、`section.NN` で
インデックス完全一致、`section.<token>` で slug 部分一致。`--force` で既存上書き。
"""
from __future__ import annotations

import base64
import json
import sys
import time
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image

DATA_JSON = Path(
    r"C:\Users\mitam\Desktop\work\50_ブログ\.obsidian\plugins\buzzblog-generator\data.json"
)
OUT_DIR = Path(__file__).resolve().parent.parent / "assets" / "images" / "items"

SHARED_TONE = """世界観: ブランド既存トーン厳守。
- 背景: 紙白 (#F5F1E6) のフラットマット紙質。極々淡い罫線/ドットを薄く敷くだけ。グラデネオン・3D・グラスモーフィズム・絵文字・ノイズはNG。
- 主インク色: 深い黒 (#1A1A1A)。
- アクセント色: くすみオレンジ (#E8632B)。重要キーワードや小アイコンの線色のみに使う。
- フォント: モダンな日本語サンセリフ (Noto Sans JP / Inter ベース、極太)。明朝NG。
- トーン: Notion / Stripe / Linear に近い品の良いミニマル LP イラスト。フォトリアルNG、ベクター線画+タイポグラフィ表現。
- 日本語を正確に描画。ローマ字混入NG・誤字NG。
- 1024x1024 正方形。四辺に 64px のセーフエリア確保。カード自身の枠線・影は描かない (HTML 側で付与)。"""


def standard_prompt(item: dict, index_label: str) -> str:
    accent = item.get("accent")
    accent_note = (
        f"見出しのうち「{accent}」だけはオレンジ #E8632B で強調。それ以外は黒。"
        if accent
        else "見出しは黒。"
    )
    return f"""日本のSaaS LP用カード 1 枚 (1024x1024)。

{SHARED_TONE}

レイアウト (中央寄せ縦組み):
- 左上に小さなオレンジの 2 桁インデックス「{index_label}」(80pt 程度)。
- 上 1/3 中央: ミニマル線画アイコン「{item['icon']}」(オレンジ単色 #E8632B、ストローク 6–8px、塗り無し)。
- 中央: 黒の極太見出し 1 行「{item['title']}」(60–80pt 相当)。{accent_note}
- 下 1/4 中央: 黒70%の補足文 1〜2 行「{item['note']}」(28–34pt 相当、line-height 1.5)。"""


def metrics_prompt(item: dict, index_label: str) -> str:
    return f"""日本のSaaS LP用 "実績メトリクスカード" 1 枚 (1024x1024)。

{SHARED_TONE}

レイアウト (中央寄せ縦組み):
- 左上に小さなオレンジの 2 桁インデックス「{index_label}」(80pt 程度)。
- 上 1/4 中央: 関連する小さめのミニマル線画アイコン「{item['icon']}」(オレンジ単色)。
- 中央: 巨大なオレンジ #E8632B 極太数字「{item['big']}」(画像高の 40% 程度、340–420pt 相当)。
- 下 1/4 中央: 黒の補足文 2 行「{item['note']}」(28–34pt 相当、line-height 1.5)。重要語「{item.get('accent', '')}」は黒の極太で。"""


def addon_prompt(item: dict, index_label: str) -> str:
    return f"""日本のSaaS LP用 "アドオンパックカード" 1 枚 (1024x1024)。

{SHARED_TONE}

レイアウト (中央寄せ縦組み):
- 左上に小さなオレンジの 2 桁インデックス「{index_label}」(80pt 程度)。
- 上 1/3 中央: ミニマル線画アイコン「{item['icon']}」(オレンジ単色 #E8632B)。
- 中央上段: 黒の極太でパック名「{item['name']}」(54–62pt 相当、line-height 1.2)。
- 中央下段: オレンジ #E8632B の極太価格「{item['price']}」(72–80pt 相当)。
- 下 1/4 中央: 黒70%の補足文 1 行「{item['note']}」(26–32pt 相当)。"""


SECTIONS: dict[str, dict] = {
    "pain": {
        "filename_prefix": "pain",
        "template": "standard",
        "items": [
            {
                "slug": "manual",
                "icon": "カレンダーと疲れた砂時計の組み合わせ線画",
                "title": "毎日の手動投稿、もう限界。",
                "note": "24時間気を張り続けても、伸びない。",
                "accent": "もう限界",
            },
            {
                "slug": "api_cost",
                "icon": "札束の上に大きな『$200』タグが乗ったAPI線画",
                "title": "X API は月 200 ドル。",
                "note": "個人で払い続けるには重すぎる。",
                "accent": "200 ドル",
            },
            {
                "slug": "freeze",
                "icon": "鎖でつながれた3つのアカウントカードに赤橙のヒビが入った線画",
                "title": "同 IP で芋づる凍結。",
                "note": "資産アカウントが一晩で消える恐怖。",
                "accent": "芋づる凍結",
            },
            {
                "slug": "dm_late",
                "icon": "未読バッジ付きDM受信箱と砂時計の線画",
                "title": "DM 返信が、間に合わない。",
                "note": "アクティブ時間にしか返せず、機会損失。",
                "accent": "間に合わない",
            },
        ],
    },
    "why": {
        "filename_prefix": "why",
        "template": "standard",
        "items": [
            {
                "slug": "no_api",
                "icon": "Xのロゴと鍵の線画",
                "title": "API 不要、ID とパスだけ。",
                "note": "面倒な API 申請ゼロ。すぐ始まる。",
                "accent": "API 不要",
            },
            {
                "slug": "random_x25",
                "icon": "ランダムな時刻に散らばる4枚の投稿カードの線画",
                "title": "ランダム投稿で 2.5 倍。",
                "note": "100 件プールから人間らしい間隔で配信。",
                "accent": "2.5 倍",
            },
            {
                "slug": "one_time",
                "icon": "¥0 と書かれた永続バッジの線画",
                "title": "全プラン 買い切り、月額ゼロ。",
                "note": "サブスクなし、永続ライセンス。",
                "accent": "買い切り",
            },
        ],
    },
    "features": {
        "filename_prefix": "features",
        "template": "standard",
        "items": [
            {
                "slug": "random_engine",
                "icon": "シャッフル矢印が交差した線画",
                "title": "ランダム投稿エンジン",
                "note": "100件プール × 重複防止 × 時間ランダマイザー。",
                "accent": "ランダム",
            },
            {
                "slug": "proxy",
                "icon": "中央ノードから3本のIP分岐が伸びる線画",
                "title": "アカウント別プロキシ",
                "note": "連鎖凍結を防ぐ多重 IP 分散。",
                "accent": "多重 IP 分散",
            },
            {
                "slug": "community",
                "icon": "同心円で結ばれたコミュニティのアイコン線画",
                "title": "コミュニティ自動投稿",
                "note": "X コミュニティの濃いユーザーへ届ける。",
                "accent": "コミュニティ",
            },
            {
                "slug": "auto_dm",
                "icon": "吹き出しと自動矢印マークの線画",
                "title": "自動 DM 返信",
                "note": "受信 DM ＋リクエスト承認をテンプレ化。",
                "accent": "テンプレ化",
            },
            {
                "slug": "amazon",
                "icon": "段ボール箱と復活マークの線画",
                "title": "Amazon 在庫復活アラート",
                "note": "Keepa 連携で復活瞬間に自動投稿。",
                "accent": "Keepa 連携",
            },
            {
                "slug": "ai_post",
                "icon": "スパークル付きペンの線画",
                "title": "AI 投稿生成",
                "note": "GPT-4o & Gemini で投稿文を量産。",
                "accent": "AI",
            },
        ],
    },
    "metrics": {
        "filename_prefix": "metrics",
        "template": "metrics",
        "items": [
            {
                "slug": "sales_3",
                "icon": "受注ベルの線画",
                "big": "3 件",
                "note": "フォロワー31人のサブ垢で、1日3件成約 (合計¥15,000)。",
                "accent": "3件成約",
            },
            {
                "slug": "growth_900",
                "icon": "急上昇する折れ線グラフの線画",
                "big": "+900%",
                "note": "1日150ポストを2ヶ月で、プロフアクセス9倍。",
                "accent": "9倍",
            },
            {
                "slug": "clicks_18",
                "icon": "クリックする指の線画",
                "big": "18 回/日",
                "note": "ファン化長文＋note誘導戦略で、過去最大のプロフクリック数。",
                "accent": "過去最大",
            },
        ],
    },
    "addons": {
        "filename_prefix": "addons",
        "template": "addon",
        "items": [
            {
                "slug": "ai",
                "icon": "スパークル＋ペンの線画",
                "name": "AI 生成パック",
                "price": "¥4,000",
                "note": "ランダム投稿+AI+スプシ取込。",
            },
            {
                "slug": "engagement",
                "icon": "ハートと曲線矢印の線画",
                "name": "エンゲージメントパック",
                "price": "¥4,000",
                "note": "自動いいね+フォロー+リプライ。",
            },
            {
                "slug": "multi",
                "icon": "重なった複数のアカウントカードの線画",
                "name": "マルチアカウントパック",
                "price": "¥5,000",
                "note": "プロキシ+一括登録+共通設定。",
            },
            {
                "slug": "community",
                "icon": "同心円のコミュニティ線画",
                "name": "コミュニティパック",
                "price": "¥4,000",
                "note": "コミュニティ自動投稿。",
            },
            {
                "slug": "amazon",
                "icon": "段ボール箱と復活マークの線画",
                "name": "Amazon 在庫復活パック",
                "price": "¥6,000",
                "note": "Keepa 連携+在庫監視+自動投稿。",
            },
        ],
    },
}


def build_prompt(section: str, item: dict, idx: int) -> str:
    template = SECTIONS[section]["template"]
    index_label = f"{idx + 1:02d}"
    if template == "metrics":
        return metrics_prompt(item, index_label)
    if template == "addon":
        return addon_prompt(item, index_label)
    return standard_prompt(item, index_label)


def output_paths(section: str, idx: int, item: dict) -> tuple[Path, Path]:
    prefix = SECTIONS[section]["filename_prefix"]
    base = f"{prefix}_{idx + 1:02d}_{item['slug']}"
    return OUT_DIR / f"{base}.png", OUT_DIR / f"{base}.webp"


def post_image(api_key: str, model: str, prompt: str) -> bytes:
    payload = json.dumps(
        {"model": model, "prompt": prompt, "size": "1024x1024", "n": 1}
    ).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        result = json.loads(resp.read())
    item = result["data"][0]
    if "b64_json" in item:
        return base64.b64decode(item["b64_json"])
    with urllib.request.urlopen(item["url"], timeout=120) as r:
        return r.read()


def generate(section: str, idx: int, item: dict, api_key: str, model: str, force: bool) -> str:
    out_png, out_webp = output_paths(section, idx, item)
    label = f"{section}.{idx + 1:02d} {item['slug']}"
    if out_png.exists() and out_webp.exists() and not force:
        print(f"[{label}] skip (already exists, use --force to overwrite)", file=sys.stderr)
        return "skip"

    prompt = build_prompt(section, item, idx)
    delays = [0, 2, 4, 8]
    last_err: Exception | None = None
    for attempt, delay in enumerate(delays):
        if delay:
            time.sleep(delay)
        try:
            print(f"[{label}] generating with {model} 1024x1024 (attempt {attempt + 1})...", file=sys.stderr)
            png_bytes = post_image(api_key, model, prompt)
            break
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"[{label}] HTTPError {e.code}: {body[:600]}", file=sys.stderr)
            last_err = e
            if e.code not in (429, 500, 502, 503, 504):
                raise
        except urllib.error.URLError as e:
            print(f"[{label}] URLError: {e}", file=sys.stderr)
            last_err = e
    else:
        print(f"[{label}] failed after retries", file=sys.stderr)
        raise last_err if last_err else RuntimeError(f"{label}: unknown error")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_png.write_bytes(png_bytes)
    Image.open(BytesIO(png_bytes)).convert("RGB").save(
        out_webp, "WEBP", quality=86, method=6
    )
    print(f"[{label}] wrote {out_png.name} + {out_webp.name}")
    return "ok"


def expand_targets(args: list[str]) -> list[tuple[str, int, dict]]:
    if not args:
        targets: list[tuple[str, int, dict]] = []
        for section, cfg in SECTIONS.items():
            for idx, item in enumerate(cfg["items"]):
                targets.append((section, idx, item))
        return targets

    targets = []
    for raw in args:
        if "." in raw:
            section, token = raw.split(".", 1)
        else:
            section, token = raw, None
        if section not in SECTIONS:
            print(f"unknown section: {section} (valid: {list(SECTIONS)})", file=sys.stderr)
            sys.exit(2)
        items = SECTIONS[section]["items"]
        if token is None:
            for idx, item in enumerate(items):
                targets.append((section, idx, item))
            continue
        if token.isdigit():
            i = int(token) - 1
            if not (0 <= i < len(items)):
                print(f"index out of range: {raw}", file=sys.stderr)
                sys.exit(2)
            targets.append((section, i, items[i]))
        else:
            matched = [(idx, it) for idx, it in enumerate(items) if token in it["slug"]]
            if not matched:
                print(f"no slug matched: {raw}", file=sys.stderr)
                sys.exit(2)
            for idx, item in matched:
                targets.append((section, idx, item))
    return targets


def main() -> int:
    raw = sys.argv[1:]
    force = "--force" in raw
    args = [a for a in raw if a != "--force"]

    cfg = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    api_key = cfg["openaiApiKey"]
    model = cfg.get("openaiImageModel", "gpt-image-2")

    targets = expand_targets(args)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    failures: list[str] = []
    for section, idx, item in targets:
        try:
            generate(section, idx, item, api_key, model, force)
        except Exception as e:  # noqa: BLE001
            failures.append(f"{section}.{idx + 1:02d} {item['slug']}: {e}")

    if failures:
        print("\nFAILED:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
