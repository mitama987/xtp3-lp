# XToolsPro3 公式 LP

X(Twitter)自動投稿ツール **XToolsPro3** の販売 LP です。素の HTML/CSS/JS だけで構成されており、GitHub Pages で即公開できます。

公開予定 URL: `https://mitama987.github.io/xtp3-lp/`

## ローカルプレビュー

```powershell
# Python が入っていれば
python -m http.server 5500
# → http://localhost:5500 を開く
```

VSCode の Live Server 拡張でも OK。

## デプロイ（GitHub Pages）

1. GitHub に `xtp3-lp` リポジトリを作成（Public）
2. `git push origin main` で本リポを上げる
3. リポの **Settings → Pages → Source = `main` branch / `(root)`** を選択
4. 数十秒で `https://<username>.github.io/xtp3-lp/` が公開される

カスタムドメインを使うときは、ルートに `CNAME` ファイル（中身はドメイン名 1 行）を追加するだけです。

## ファイル構成

```
.
├── index.html                          # 本体
├── assets/
│   ├── css/style.css                   # 全スタイル（CSS Variables）
│   ├── js/faq.js                       # FAQ アコーディオン＋fade-in
│   └── images/
│       ├── feature_map.webp            # ヒーロー右
│       ├── random_flow.webp            # 機能 #1
│       ├── proxy_protection.webp       # 機能 #2
│       ├── community_branch.webp       # 機能 #3
│       ├── auto_dm_flow.webp           # 機能 #4
│       ├── amazon_flow.webp            # 機能 #5
│       └── developer_profile.webp      # 開発者セクション
├── _resize_images.py                   # Obsidian の diagram_*.png を再書き出しするスクリプト
└── README.md
```

## 画像の差し替え

新しい diagram を Obsidian 側で更新したら、

```powershell
python _resize_images.py
```

を実行すると `assets/images/*.webp` が 1200px / quality 82 で書き出されます。差分だけ commit してください。

## デザインの考え方

- 紙白ベース（`#FCFAF5`）+ くすみオレンジ（`#E8632B`）+ 深緑（`#0F4C3A`）の 3 色
- 見出し: `Noto Serif JP` Bold（明朝で重厚さ）
- 本文: `Inter` + `Noto Sans JP`
- **ガラスモーフ／紫×青グラデ／ネオングロー／ダークモード**は意図的に不採用（"いかにも生成 AI" を避ける）
- スマホファースト・ビルドツール不要・JS は約 30 行のみ

## 編集のヒント

- 価格を変えたい → `index.html` の `<!-- ============ PRICING ============ -->` 配下、`.plan-price` を直接編集
- アドオンを増減 → `<!-- ============ ADDONS ============ -->` の `<article class="addon">` を増減
- お客様の声を追加 → `assets/images/reviews/` に画像を置き、`<!-- ============ REVIEWS ============ -->` の `<figure>` を追記
- FAQ を追加 → `<!-- ============ FAQ ============ -->` の `<details class="qa">` をコピーして追記

## ライセンス

© 2026 Youパパ. All rights reserved.
