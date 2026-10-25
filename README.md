# X_account

ライブポケット・チケットダイブの **当日チケ発代行** 募集ツイートを、毎日自動で投稿するボットです。

- 毎日 **8:07 / 12:37 / 17:07（JST）** の3回投稿（`.github/workflows/post.yml`）
- 文面は見出し・本文・料金・信頼性・CTA・ハッシュタグをランダムに組み合わせ、**直近20件と同じ文面は使いません**（日付は毎回当日に自動更新）
- 新規アカウント向けに、`config.yaml` の `warmup` の日付までは1日1件に制限
- 当日の日付と料金を入れた画像（1200×675）を毎回添付し、配色も毎回変わります

## セットアップ

アカウントのプロフィール・各種設定・最初の手動投稿は [ACCOUNT_SETUP.md](ACCOUNT_SETUP.md) を参照。

1. [X Developer Portal](https://developer.x.com/) でアプリを作り、権限を **Read and write** にしてから以下の4つを発行
2. GitHub のリポジトリ → Settings → Secrets and variables → Actions に登録
   - `X_API_KEY` / `X_API_SECRET` / `X_ACCESS_TOKEN` / `X_ACCESS_TOKEN_SECRET`
3. `config.yaml` の料金・連絡先・支払い方法・実績件数を自分の内容に変更
4. Actions タブ →「チケ発募集ツイート」→ Run workflow（`dry_run` にチェック）で文面を確認

## ローカルで確認

```sh
pip install -r requirements.txt
python -m bot.post --dry-run   # 文面を表示し out/card.png を生成（投稿しない）
```

## 料金（初期値・`config.yaml` で変更）

| 区分 | 手数料（1枚） |
| --- | --- |
| 通常（前日まで） | 300円 |
| 当日 | 500円 |
| 2枚以上 | 1枚あたり100円引き |

チケット代は定価のまま受け取り、上乗せは代行手数料のみです。
