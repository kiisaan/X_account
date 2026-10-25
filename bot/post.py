"""募集ツイートを作成して X に投稿する。

使い方:
  python -m bot.post            # 投稿する（要 X API キー）
  python -m bot.post --dry-run  # 文面と画像を作るだけ
"""

import argparse
import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path

import requests
import yaml
from requests_oauthlib import OAuth1

from .compose import JST, compose, x_weighted_length
from .image import render

ROOT = Path(__file__).resolve().parent.parent
HISTORY = ROOT / "state" / "history.json"
API = "https://api.x.com/2"


def load_history() -> list:
    if HISTORY.exists():
        return json.loads(HISTORY.read_text(encoding="utf-8"))
    return []


def save_history(history: list) -> None:
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps(history[-200:], ensure_ascii=False, indent=2), encoding="utf-8")


def auth() -> OAuth1:
    keys = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]
    missing = [k for k in keys if not os.environ.get(k)]
    if missing:
        sys.exit(f"環境変数が未設定です: {', '.join(missing)}")
    return OAuth1(*(os.environ[k] for k in keys))


def upload_image(oauth: OAuth1, path: Path) -> str | None:
    with path.open("rb") as f:
        r = requests.post(f"{API}/media/upload", auth=oauth, timeout=60,
                          files={"media": f}, data={"media_category": "tweet_image"})
    if r.ok:
        return r.json()["data"]["id"]
    print(f"画像アップロード失敗（テキストのみで投稿します）: {r.status_code} {r.text}", file=sys.stderr)
    return None


def post_tweet(oauth: OAuth1, text: str, media_id: str | None) -> str:
    payload = {"text": text}
    if media_id:
        payload["media"] = {"media_ids": [media_id]}
    r = requests.post(f"{API}/tweets", auth=oauth, json=payload, timeout=30)
    if not r.ok:
        sys.exit(f"投稿失敗: {r.status_code} {r.text}")
    return r.json()["data"]["id"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--config", default=str(ROOT / "config.yaml"))
    args = ap.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    now = datetime.now(JST)
    rng = random.Random()
    history = load_history()

    # 新規アカウントの立ち上げ期間は1日1投稿まで（いきなり多投するとスパム判定されやすい）
    warmup = cfg.get("warmup") or {}
    if warmup.get("until") and now.date() < datetime.fromisoformat(str(warmup["until"])).date():
        today = now.date().isoformat()
        posted_today = sum(1 for h in history if h["at"].startswith(today))
        if posted_today >= warmup.get("max_per_day", 1) and not args.dry_run:
            print(f"立ち上げ期間中（{warmup['until']}まで）のため本日の投稿はスキップします")
            return

    recent = [h["key"] for h in history[-cfg.get("avoid_recent", 20):]]

    text, key = compose(cfg, recent, now, rng)
    print(text)
    print(f"--- {x_weighted_length(text)}/280")

    image_path = None
    if cfg["image"]["enabled"]:
        image_path = render(cfg, now, ROOT / "out" / "card.png", rng)
        print(f"画像: {image_path}")

    if args.dry_run:
        return

    oauth = auth()
    media_id = upload_image(oauth, image_path) if image_path else None
    tweet_id = post_tweet(oauth, text, media_id)
    print(f"投稿しました: https://x.com/i/web/status/{tweet_id}")

    history.append({"at": now.isoformat(timespec="seconds"), "key": key, "id": tweet_id})
    save_history(history)


if __name__ == "__main__":
    main()
