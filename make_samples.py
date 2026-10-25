"""Generate SYNTHETIC demo images (not patient data) to exercise the pipeline."""
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import json, os, random

W, H = 640, 420
S = 2  # supersample
CARD = (430, 300, 610, 400)


def radial(size, inner, outer):
    w, h = size
    im = Image.new("RGB", size)
    px = im.load()
    cx, cy = w / 2, h / 2
    for y in range(h):
        for x in range(w):
            d = min(1.0, (((x - cx) / cx) ** 2 + ((y - cy) / cy) ** 2) ** 0.5)
            px[x, y] = tuple(int(inner[i] * (1 - d) + outer[i] * d) for i in range(3))
    return im


def eye(conj_rgb, cast=(1.0, 1.0, 1.0), blur=0, name="", seed=1):
    random.seed(seed)
    w, h = W * S, H * S
    im = radial((w, h), (214, 170, 146), (168, 122, 100))  # skin
    d = ImageDraw.Draw(im)
    # lower lid pulled down: conjunctiva crescent with a soft gradient
    conj = radial((300 * S, 200 * S), conj_rgb, tuple(max(0, c - 28) for c in conj_rgb))
    mask = Image.new("L", conj.size, 0)
    ImageDraw.Draw(mask).chord((0, 0, 300 * S, 200 * S), 0, 180, fill=255)
    vd = ImageDraw.Draw(conj)
    for _ in range(14):  # small vessels
        x0, y0 = random.randint(30, 270) * S, random.randint(110, 180) * S
        vd.line([(x0, y0), (x0 + random.randint(-40, 40) * S, y0 + random.randint(-15, 10) * S)],
                fill=tuple(max(0, c - 45) for c in conj_rgb), width=S)
    im.paste(conj, (100 * S, 130 * S), mask.filter(ImageFilter.GaussianBlur(3 * S)))
    # sclera + iris + pupil
    sc = Image.new("L", (w, h), 0)
    ImageDraw.Draw(sc).ellipse((90 * S, 60 * S, 410 * S, 232 * S), fill=255)
    im.paste(radial((w, h), (250, 248, 244), (222, 214, 206)), (0, 0), sc.filter(ImageFilter.GaussianBlur(2 * S)))
    iris = radial((112 * S, 140 * S), (120, 84, 52), (48, 30, 18))
    im_mask = Image.new("L", iris.size, 0)
    ImageDraw.Draw(im_mask).ellipse((0, 0, 112 * S, 140 * S), fill=255)
    im.paste(iris, (194 * S, 76 * S), im_mask)
    d = ImageDraw.Draw(im)
    d.ellipse((232 * S, 118 * S, 268 * S, 172 * S), fill=(12, 8, 6))
    d.ellipse((255 * S, 122 * S, 268 * S, 136 * S), fill=(250, 250, 250))  # catchlight
    # upper lid line + lashes
    d.arc((86 * S, 52 * S, 414 * S, 240 * S), 190, 350, fill=(70, 40, 30), width=5 * S)
    for i in range(22):
        a = 195 + i * 7
        import math
        cx, cy, rx, ry = 250 * S, 146 * S, 164 * S, 94 * S
        x, y = cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a))
        d.line([(x, y), (x + (x - cx) * 0.12, y - 22 * S)], fill=(40, 25, 20), width=2 * S)
    # colour card
    d.rounded_rectangle([c * S for c in CARD], radius=8 * S, fill=(28, 28, 32))
    for i, c in enumerate([(255, 255, 255), (128, 128, 128), (200, 40, 40), (230, 190, 180)]):
        x = CARD[0] + 8 + i * 43
        d.rectangle(((x) * S, (CARD[1] + 15) * S, (x + 35) * S, (CARD[3] - 15) * S), fill=c)
    im = im.resize((W, H), Image.LANCZOS)
    ImageDraw.Draw(im).text((10, 400), "SYNTHETIC DEMO IMAGE - not patient data", fill=(60, 30, 30))
    if cast != (1.0, 1.0, 1.0):
        r, g, b = im.split()
        im = Image.merge("RGB", [ch.point(lambda v, k=k: min(255, int(v * k))) for ch, k in zip((r, g, b), cast)])
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    im.save(f"samples/{name}.jpg", quality=93)


specs = {
    "healthy_daylight": dict(conj_rgb=(205, 70, 78)),
    "anaemic_daylight": dict(conj_rgb=(236, 180, 176)),
    "borderline_daylight": dict(conj_rgb=(222, 124, 124)),
    "healthy_warm_tubelight": dict(conj_rgb=(205, 70, 78), cast=(1.0, 0.75, 0.6)),
    "anaemic_warm_tubelight": dict(conj_rgb=(236, 180, 176), cast=(1.0, 0.75, 0.6)),
    "blurry_retake": dict(conj_rgb=(212, 96, 100), blur=6),
}
os.makedirs("samples", exist_ok=True)
for n, s in specs.items():
    eye(name=n, **s)
meta = {"roi": [170, 255, 330, 295], "white": [CARD[0] + 12, CARD[1] + 25, CARD[0] + 39, CARD[3] - 25]}
json.dump({n: meta for n in specs}, open("samples/regions.json", "w"), indent=1)
print("ok")
