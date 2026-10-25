"""募集ツイートの文面を組み立てる。"""

import hashlib
import random
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=9))
WEEKDAYS = "月火水木金土日"
MAX_WEIGHT = 280


def x_weighted_length(text: str) -> int:
    """X の文字数カウント（日本語・絵文字は2、英数字は1）。"""
    total = 0
    for ch in text:
        cp = ord(ch)
        if (
            cp <= 0x10FF
            or 0x2000 <= cp <= 0x200D
            or 0x2010 <= cp <= 0x201F
            or 0x2032 <= cp <= 0x2037
        ):
            total += 1
        else:
            total += 2
    return total


def _fill(template: str, values: dict) -> str:
    return template.format(**values)


def build_values(cfg: dict, now: datetime) -> dict:
    p = cfg["pricing"]
    c = cfg["contact"]
    return {
        "date": f"{now.month}/{now.day}",
        "weekday": WEEKDAYS[now.weekday()],
        "platforms": "・".join(cfg["platforms"]),
        "base_fee": p["base_fee"],
        "same_day_fee": p["same_day_fee"],
        "multi_discount": p["multi_discount"],
        "contact": c["method"],
        "hours": c["hours"],
        "payment": c["payment"],
        "total": cfg.get("track_record", {}).get("total_count", ""),
    }


def _usable(parts: list, values: dict) -> list:
    # 実績数が未設定なら実績文は使わない
    if not values["total"]:
        parts = [t for t in parts if "{total}" not in t]
    return parts


def compose(cfg: dict, recent_hashes: list, now: datetime | None = None,
            rng: random.Random | None = None) -> tuple[str, str]:
    """(本文, 組み合わせハッシュ) を返す。直近と同じ組み合わせは避ける。"""
    now = now or datetime.now(JST)
    rng = rng or random.Random()
    values = build_values(cfg, now)
    t = cfg["templates"]
    tags_cfg = cfg["hashtags"]

    fallback = None
    for _ in range(200):
        lines = [
            _fill(rng.choice(_usable(t["headline"], values)), values),
            _fill(rng.choice(_usable(t["body"], values)), values),
        ]
        price = _fill(rng.choice(_usable(t["price"], values)), values)
        trust = _fill(rng.choice(_usable(t["trust"], values)), values)
        extras = [price, trust]
        rng.shuffle(extras)
        cta = _fill(rng.choice(_usable(t["cta"], values)), values)
        tags = " ".join(list(tags_cfg["always"]) + rng.sample(
            tags_cfg["pool"], min(tags_cfg["pick"], len(tags_cfg["pool"]))))

        # 収まらなければ信頼性の一文を外して再判定（料金は必ず残す）
        text = None
        for middle in (extras, [price]):
            candidate = "\n".join(lines) + "\n\n" + "\n".join(middle + [cta]) + "\n\n" + tags
            if x_weighted_length(candidate) <= MAX_WEIGHT:
                text = candidate
                break
        if text is None:
            continue
        # 日付を除いた文面で重複判定（日付だけ違う同文を避ける）
        key = hashlib.sha1(text.replace(values["date"], "").encode()).hexdigest()[:12]
        if key not in recent_hashes:
            return text, key
        fallback = fallback or (text, key)

    if fallback:
        return fallback
    raise RuntimeError("280文字以内の文面を作れませんでした。テンプレートを短くしてください。")
