"""募集ツイートに添付する料金カード画像を生成する。"""

import random
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .compose import WEEKDAYS

FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
]

W, H = 1200, 675  # X のタイムラインで切れない 16:9


def _font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    raise RuntimeError("日本語フォントが見つかりません（fonts-noto-cjk を入れてください）")


def _center(draw, y, text, font, fill):
    w = draw.textlength(text, font=font)
    draw.text(((W - w) / 2, y), text, font=font, fill=fill)


def render(cfg: dict, now: datetime, out: Path, rng: random.Random | None = None) -> Path:
    rng = rng or random.Random()
    bg, accent = rng.choice(cfg["image"]["palettes"])
    p = cfg["pricing"]
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, W, 14], fill=accent)
    d.rectangle([0, H - 14, W, H], fill=accent)

    _center(d, 50, f"{now.month}/{now.day}({WEEKDAYS[now.weekday()]}) 当日受付中", _font(44), accent)
    _center(d, 120, "チケ発代行", _font(120), "#FFFFFF")
    _center(d, 275, " / ".join(cfg["platforms"]) + " 対応", _font(40), "#E5E7EB")

    # 料金ボックス
    box = [150, 350, W - 150, 560]
    d.rounded_rectangle(box, radius=28, outline=accent, width=5)
    f_label, f_price = _font(36), _font(64)
    cols = [
        ("通常", f"{p['base_fee']}{p['currency']}"),
        ("当日", f"{p['same_day_fee']}{p['currency']}"),
    ]
    col_w = (box[2] - box[0]) / len(cols)
    for i, (label, price) in enumerate(cols):
        cx = box[0] + col_w * i + col_w / 2
        lw = d.textlength(label, font=f_label)
        pw = d.textlength(price, font=f_price)
        d.text((cx - lw / 2, 380), label, font=f_label, fill="#E5E7EB")
        d.text((cx - pw / 2, 440), price, font=f_price, fill="#FFFFFF")
    d.line([box[0] + col_w, 380, box[0] + col_w, 530], fill=accent, width=3)

    _center(d, 585, f"チケット代は定価のまま｜1枚あたりの手数料｜2枚以上 1枚{p['multi_discount']}円引き",
            _font(28), "#E5E7EB")

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG")
    return out
