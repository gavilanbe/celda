from pathlib import Path
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "pokered-ready" / "gfx"

WHITE = 255
LIGHT = 170
DARK = 85
BLACK = 0


FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01111", "10000", "10000", "10011", "10001", "10001", "01110"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "10010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "01010", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "01010", "00100", "00100", "00100", "01010", "10001"],
    "Y": ["10001", "01010", "00100", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
}


def canvas(size):
    return Image.new("L", size, WHITE)


def save(img, rel):
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def line(draw, points, fill=BLACK, width=1):
    draw.line(points, fill=fill, width=width, joint="curve")


def qpoly(draw, points, fill, outline=BLACK):
    draw.polygon(points, fill=fill)
    draw.line(points + [points[0]], fill=outline, width=1)


def qellipse(draw, box, fill, outline=BLACK):
    draw.ellipse(box, fill=fill, outline=outline, width=1)


def draw_text(draw, text, x, y, scale=1, fill=BLACK):
    cursor = x
    for char in text.upper():
        glyph = FONT.get(char, FONT[" "])
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    draw.rectangle(
                        [
                            cursor + gx * scale,
                            y + gy * scale,
                            cursor + (gx + 1) * scale - 1,
                            y + (gy + 1) * scale - 1,
                        ],
                        fill=fill,
                    )
        cursor += 6 * scale


def musgin_front():
    img = canvas((40, 40))
    d = ImageDraw.Draw(img)
    qellipse(d, (7, 13, 29, 34), LIGHT)
    qellipse(d, (9, 10, 27, 27), LIGHT)
    qpoly(d, [(20, 8), (22, 1), (25, 8)], LIGHT)
    qpoly(d, [(18, 8), (16, 1), (14, 9)], LIGHT)
    qpoly(d, [(5, 20), (1, 17), (5, 25)], LIGHT)
    qpoly(d, [(27, 20), (34, 16), (30, 26)], LIGHT)
    qpoly(d, [(27, 29), (37, 32), (28, 34)], DARK)
    qellipse(d, (11, 17, 16, 24), WHITE)
    qellipse(d, (13, 19, 16, 24), BLACK)
    qellipse(d, (22, 16, 27, 23), WHITE)
    qellipse(d, (23, 18, 26, 23), BLACK)
    line(d, [(14, 26), (17, 27), (20, 26)], BLACK)
    qpoly(d, [(10, 29), (15, 31), (12, 36)], DARK)
    qpoly(d, [(22, 30), (27, 31), (27, 36)], DARK)
    qpoly(d, [(13, 35), (6, 38), (16, 38)], BLACK, BLACK)
    qpoly(d, [(25, 35), (20, 38), (31, 38)], BLACK, BLACK)
    d.point([(12, 14), (25, 14), (17, 31), (19, 31)], fill=WHITE)
    return img


def musgin_back():
    img = canvas((32, 32))
    d = ImageDraw.Draw(img)
    qellipse(d, (8, 11, 24, 28), LIGHT)
    qpoly(d, [(16, 9), (13, 2), (19, 8)], LIGHT)
    qpoly(d, [(18, 9), (24, 4), (22, 12)], LIGHT)
    qpoly(d, [(7, 18), (2, 16), (6, 23)], DARK)
    qpoly(d, [(24, 18), (30, 15), (27, 24)], DARK)
    qpoly(d, [(22, 24), (30, 27), (22, 28)], DARK)
    d.rectangle((10, 24, 13, 29), fill=DARK, outline=BLACK)
    d.rectangle((19, 24, 22, 29), fill=DARK, outline=BLACK)
    line(d, [(8, 17), (24, 17)], DARK)
    d.point([(14, 6), (20, 9), (12, 14), (21, 14)], fill=WHITE)
    return img


def ascun_front():
    img = canvas((40, 40))
    d = ImageDraw.Draw(img)
    qellipse(d, (10, 17, 31, 35), DARK)
    qellipse(d, (10, 8, 29, 27), LIGHT)
    qpoly(d, [(11, 10), (7, 1), (16, 7)], DARK)
    qpoly(d, [(26, 9), (33, 1), (32, 13)], DARK)
    qellipse(d, (17, 8, 25, 14), WHITE)
    qellipse(d, (13, 16, 18, 24), WHITE)
    qellipse(d, (14, 18, 17, 24), BLACK)
    qellipse(d, (23, 15, 28, 23), WHITE)
    qellipse(d, (24, 17, 27, 23), BLACK)
    qpoly(d, [(29, 29), (37, 31), (32, 35)], DARK)
    qpoly(d, [(35, 28), (39, 24), (38, 32)], BLACK)
    qellipse(d, (18, 27, 25, 34), WHITE)
    line(d, [(18, 25), (20, 26), (23, 25)], BLACK)
    d.rectangle((10, 32, 14, 38), fill=BLACK)
    d.rectangle((25, 31, 29, 38), fill=BLACK)
    qellipse(d, (8, 26, 13, 31), LIGHT)
    qellipse(d, (28, 25, 33, 30), LIGHT)
    d.point([(10, 7), (31, 7), (16, 12), (26, 12), (20, 30)], fill=WHITE)
    return img


def ascun_back():
    img = canvas((32, 32))
    d = ImageDraw.Draw(img)
    qellipse(d, (8, 13, 24, 29), DARK)
    qellipse(d, (8, 7, 24, 23), DARK)
    qpoly(d, [(9, 9), (5, 2), (14, 7)], BLACK)
    qpoly(d, [(23, 9), (27, 2), (18, 7)], BLACK)
    qpoly(d, [(22, 23), (30, 24), (26, 29)], BLACK)
    qellipse(d, (12, 6, 20, 12), LIGHT)
    d.rectangle((10, 25, 13, 31), fill=BLACK)
    d.rectangle((20, 25, 23, 31), fill=BLACK)
    d.point([(13, 8), (18, 8), (11, 14), (21, 14)], fill=LIGHT)
    return img


def gotren_front():
    img = canvas((40, 40))
    d = ImageDraw.Draw(img)
    qellipse(d, (9, 13, 29, 34), DARK)
    qellipse(d, (10, 7, 29, 26), LIGHT)
    qpoly(d, [(7, 18), (1, 14), (4, 24)], WHITE)
    qpoly(d, [(29, 17), (38, 12), (34, 25)], WHITE)
    qpoly(d, [(13, 26), (20, 33), (25, 26)], WHITE)
    qpoly(d, [(20, 27), (17, 34), (23, 34)], LIGHT)
    qellipse(d, (13, 14, 18, 22), WHITE)
    qellipse(d, (14, 16, 17, 22), BLACK)
    qellipse(d, (23, 13, 28, 21), WHITE)
    qellipse(d, (24, 15, 27, 21), BLACK)
    line(d, [(17, 23), (20, 24), (23, 23)], BLACK)
    qpoly(d, [(29, 28), (38, 31), (28, 35)], DARK)
    d.rectangle((11, 32, 16, 38), fill=BLACK)
    d.rectangle((23, 31, 28, 38), fill=BLACK)
    d.point([(16, 9), (26, 9), (13, 28), (24, 28)], fill=WHITE)
    return img


def gotren_back():
    img = canvas((32, 32))
    d = ImageDraw.Draw(img)
    qellipse(d, (8, 10, 25, 28), DARK)
    qellipse(d, (8, 5, 24, 21), LIGHT)
    qpoly(d, [(6, 16), (1, 13), (4, 22)], WHITE)
    qpoly(d, [(24, 16), (31, 12), (28, 23)], WHITE)
    qpoly(d, [(21, 23), (31, 26), (22, 28)], DARK)
    line(d, [(9, 21), (24, 21)], BLACK)
    d.rectangle((11, 25, 14, 31), fill=BLACK)
    d.rectangle((21, 25, 24, 31), fill=BLACK)
    d.point([(13, 7), (21, 7), (12, 15), (23, 15)], fill=WHITE)
    return img


def nico_front(size=(56, 56)):
    img = canvas(size)
    d = ImageDraw.Draw(img)
    ox = (size[0] - 56) // 2
    qellipse(d, (ox + 20, 9, ox + 35, 25), LIGHT)
    d.rectangle((ox + 17, 9, ox + 38, 14), fill=WHITE, outline=BLACK)
    d.rectangle((ox + 15, 14, ox + 40, 17), fill=DARK, outline=BLACK)
    qpoly(d, [(ox + 23, 20), (ox + 16, 28), (ox + 16, 42), (ox + 39, 42), (ox + 39, 28), (ox + 32, 20)], DARK)
    d.rectangle((ox + 23, 23, ox + 32, 42), fill=BLACK)
    qpoly(d, [(ox + 15, 28), (ox + 10, 40), (ox + 14, 43), (ox + 19, 31)], LIGHT)
    qpoly(d, [(ox + 39, 29), (ox + 45, 38), (ox + 42, 43), (ox + 36, 32)], LIGHT)
    d.rectangle((ox + 19, 42, ox + 26, 51), fill=DARK, outline=BLACK)
    d.rectangle((ox + 30, 42, ox + 37, 51), fill=DARK, outline=BLACK)
    d.rectangle((ox + 17, 51, ox + 27, 54), fill=BLACK)
    d.rectangle((ox + 29, 51, ox + 40, 54), fill=BLACK)
    d.rectangle((ox + 23, 16, ox + 25, 21), fill=BLACK)
    d.rectangle((ox + 31, 16, ox + 33, 21), fill=BLACK)
    line(d, [(ox + 25, 23), (ox + 28, 24), (ox + 31, 23)], BLACK)
    d.point([(ox + 21, 11), (ox + 34, 11), (ox + 19, 31), (ox + 37, 31)], fill=WHITE)
    return img


def nico_back():
    img = canvas((32, 32))
    d = ImageDraw.Draw(img)
    qellipse(d, (10, 4, 22, 15), LIGHT)
    d.rectangle((8, 4, 24, 8), fill=WHITE, outline=BLACK)
    d.rectangle((7, 8, 25, 11), fill=DARK, outline=BLACK)
    qpoly(d, [(10, 13), (22, 13), (25, 25), (7, 25)], DARK)
    d.rectangle((11, 14, 21, 24), fill=LIGHT, outline=BLACK)
    d.rectangle((9, 24, 13, 31), fill=DARK, outline=BLACK)
    d.rectangle((19, 24, 23, 31), fill=DARK, outline=BLACK)
    d.rectangle((7, 29, 14, 31), fill=BLACK)
    d.rectangle((18, 29, 25, 31), fill=BLACK)
    d.rectangle((6, 15, 9, 25), fill=LIGHT, outline=BLACK)
    d.rectangle((23, 15, 26, 25), fill=LIGHT, outline=BLACK)
    return img


def nico_title():
    img = canvas((40, 56))
    d = ImageDraw.Draw(img)
    qellipse(d, (14, 6, 29, 22), LIGHT)
    d.rectangle((11, 6, 31, 11), fill=WHITE, outline=BLACK)
    d.rectangle((9, 11, 34, 14), fill=DARK, outline=BLACK)
    qpoly(d, [(16, 20), (8, 33), (11, 50), (31, 49), (34, 33), (27, 20)], DARK)
    d.rectangle((16, 24, 25, 48), fill=BLACK)
    qpoly(d, [(8, 30), (0, 23), (3, 19), (13, 30)], LIGHT)
    qpoly(d, [(31, 31), (39, 25), (38, 21), (27, 29)], LIGHT)
    d.rectangle((12, 48, 18, 55), fill=BLACK)
    d.rectangle((25, 48, 31, 55), fill=BLACK)
    d.rectangle((17, 14, 19, 19), fill=BLACK)
    d.rectangle((26, 14, 28, 19), fill=BLACK)
    line(d, [(19, 21), (22, 22), (25, 21)], BLACK)
    d.point([(15, 8), (28, 8), (11, 33), (30, 33)], fill=WHITE)
    return img


def title_logo():
    img = canvas((128, 56))
    d = ImageDraw.Draw(img)
    draw_text(d, "TORMUX", 12, 11, scale=3, fill=BLACK)
    draw_text(d, "TORMUX", 15, 14, scale=3, fill=DARK)
    draw_text(d, "TORMUX", 12, 11, scale=3, fill=BLACK)
    line(d, [(98, 9), (112, 2), (106, 18), (121, 13), (107, 30)], BLACK, 2)
    line(d, [(98, 10), (111, 4), (105, 18), (119, 14), (106, 28)], LIGHT, 1)
    return img


def version(text, size):
    img = canvas(size)
    d = ImageDraw.Draw(img)
    draw_text(d, text, 2, 1, scale=1, fill=BLACK)
    return img


def overworld_red():
    img = canvas((16, 96))
    d = ImageDraw.Draw(img)
    for i in range(6):
        y = i * 16
        qellipse(d, (5, y + 1, 11, y + 7), LIGHT)
        d.rectangle((3, y + 2, 13, y + 4), fill=DARK, outline=BLACK)
        qpoly(d, [(5, y + 7), (11, y + 7), (13, y + 13), (3, y + 13)], DARK)
        d.rectangle((5, y + 13, 7, y + 15), fill=BLACK)
        d.rectangle((9, y + 13, 11, y + 15), fill=BLACK)
        if i in (0, 1):
            d.rectangle((2, y + 9, 4, y + 13), fill=LIGHT, outline=BLACK)
            d.rectangle((12, y + 9, 14, y + 13), fill=LIGHT, outline=BLACK)
        elif i in (2, 3):
            d.rectangle((4, y + 8, 6, y + 13), fill=LIGHT, outline=BLACK)
            d.rectangle((10, y + 8, 12, y + 13), fill=LIGHT, outline=BLACK)
        elif i == 4:
            d.rectangle((1, y + 8, 4, y + 12), fill=LIGHT, outline=BLACK)
            d.rectangle((12, y + 9, 14, y + 13), fill=BLACK)
        else:
            d.rectangle((12, y + 8, 15, y + 12), fill=LIGHT, outline=BLACK)
            d.rectangle((2, y + 9, 4, y + 13), fill=BLACK)
        d.point([(6, y + 3), (10, y + 3), (7, y + 8)], fill=WHITE)
    return img


def create_all():
    save(musgin_front(), "pokemon/front/bulbasaur.png")
    save(musgin_back(), "pokemon/back/bulbasaurb.png")
    save(ascun_front(), "pokemon/front/charmander.png")
    save(ascun_back(), "pokemon/back/charmanderb.png")
    save(gotren_front(), "pokemon/front/squirtle.png")
    save(gotren_back(), "pokemon/back/squirtleb.png")
    save(nico_front(), "player/red.png")
    save(nico_back(), "player/redb.png")
    save(nico_title(), "title/player.png")
    save(title_logo(), "title/pokemon_logo.png")
    save(version("DUSK VERSION", (80, 8)), "title/red_version.png")
    save(version("DAWN VER", (64, 8)), "title/blue_version.png")
    save(overworld_red(), "sprites/red.png")
    save(nico_front(), "trainers/rival1.png")


if __name__ == "__main__":
    create_all()
