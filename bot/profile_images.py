"""プロフィール用のアイコン・ヘッダー画像を生成する。

  python -m bot.profile_images   # assets/profile/ に icon.png, header.png を作成
"""

from pathlib import Path

import yaml
from PIL import Image, ImageDraw

from .image import _font

ROOT = Path(__file__).resolve().parent.parent
BG, ACCENT = "#1E1B4B", "#F472B6"


def _center_text(d, box, text, font, fill):
    x0, y0, x1, y1 = box
    l, t, r, b = d.textbbox((0, 0), text, font=font)
    d.text((x0 + (x1 - x0 - (r - l)) / 2 - l, y0 + (y1 - y0 - (b - t)) / 2 - t), text, font=font, fill=fill)


def icon(out: Path) -> None:
    # X のアイコンは円形に切り抜かれるので、中央に収める
    s = 400
    img = Image.new("RGB", (s, s), BG)
    d = ImageDraw.Draw(img)
    d.ellipse([28, 28, s - 28, s - 28], outline=ACCENT, width=10)
    _center_text(d, (0, 70, s, 230), "チケ発", _font(88), "#FFFFFF")
    _center_text(d, (0, 225, s, 315), "当日OK", _font(52), ACCENT)
    img.save(out)


def header(cfg: dict, out: Path) -> None:
    w, h = 1500, 500
    p = cfg["pricing"]
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, h - 16, w, h], fill=ACCENT)
    # 左下はアイコンと重なるので、文字は右寄せ気味に配置
    x = 470
    d.text((x, 70), "ライブポケット / チケットダイブ", font=_font(44), fill="#E5E7EB")
    d.text((x, 130), "チケ発代行", font=_font(130), fill="#FFFFFF")
    d.text((x, 300), f"当日依頼OK ・ 手数料{p['base_fee']}円〜 ・ チケットは定価",
           font=_font(40), fill=ACCENT)
    d.text((x, 370), f"ご依頼は{cfg['contact']['method']}へ｜{cfg['contact']['hours']}",
           font=_font(36), fill="#E5E7EB")
    img.save(out)


def main() -> None:
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
    out = ROOT / "assets" / "profile"
    out.mkdir(parents=True, exist_ok=True)
    icon(out / "icon.png")
    header(cfg, out / "header.png")
    print(f"作成しました: {out / 'icon.png'}, {out / 'header.png'}")


if __name__ == "__main__":
    main()
