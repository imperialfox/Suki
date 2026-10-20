"""Make the iOS launch images in splash/ from icon-512.png (light and dark, for recent iPhones and iPads).

    python tools/splash.py        writes splash/*.png and prints the <link> tags for index.html

iOS shows these the moment the Home Screen app opens, before the page loads. They match the in-page launch screen:
the icon, 112 points wide with rounded corners, centred on the light or dark background.
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# (device width, device height, pixel ratio) in points, as iOS reports them
DEVICES = [(440, 956, 3), (420, 912, 3), (402, 874, 3), (430, 932, 3), (393, 852, 3), (428, 926, 3), (390, 844, 3),
           (414, 896, 3), (375, 812, 3), (414, 896, 2), (375, 667, 2), (1032, 1376, 2), (1024, 1366, 2), (834, 1210, 2),
           (834, 1194, 2), (820, 1180, 2), (810, 1080, 2), (744, 1133, 2)]
BG = {'light': (242, 242, 247), 'dark': (0, 0, 0)}

def icon(px):
    im = Image.open(os.path.join(ROOT, 'icon-512.png')).convert('RGBA').resize((px, px), Image.LANCZOS)
    m = Image.new('L', (px * 4, px * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, px * 4 - 1, px * 4 - 1], radius=int(px * 4 * 26 / 112), fill=255)
    im.putalpha(m.resize((px, px), Image.LANCZOS))
    return im

def main():
    os.makedirs(os.path.join(ROOT, 'splash'), exist_ok=True)
    tags = []
    for w, h, r in DEVICES:
        ic = icon(112 * r)
        for orient, (W, H) in (('portrait', (w * r, h * r)), ('landscape', (h * r, w * r))):
            if orient == 'landscape' and w < 700: continue  # iPhones open Home Screen apps upright
            for scheme, bg in BG.items():
                name = f'launch-{W}x{H}-{scheme}.png'
                im = Image.new('RGB', (W, H), bg)
                im.paste(ic, ((W - ic.width) // 2, (H - ic.height) // 2), ic)
                im.save(os.path.join(ROOT, 'splash', name), optimize=True)
                tags.append(f'<link rel="apple-touch-startup-image" href="splash/{name}" media="(device-width: {w}px) and (device-height: {h}px) and (-webkit-device-pixel-ratio: {r}) and (orientation: {orient}) and (prefers-color-scheme: {scheme})">')
    print('\n'.join(tags))

if __name__ == '__main__':
    main()
