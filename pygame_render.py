import pygame as pg
from pygame import gfxdraw

pg.init()


def button(surface, msg, x, y, w, h, ic, ac, action=None, font=pg.font.SysFont("comicsans.ttf", 40)):
    mouse = pg.mouse.get_pos()

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        aa_round_rect(surface, (x, y, w, h), ac)
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN and action is not None:
                action()
            else:
                pg.event.post(event)
    else:
        aa_round_rect(surface, (x, y, w, h), ic)
    text_surf = font.render(msg, True, (0, 0, 0))
    text_rect = text_surf.get_rect()
    text_rect.center = ((x + (w / 2)), (y + (h / 2)))
    surface.blit(text_surf, text_rect)


def label(surface, text, pos, font=None):
    if font is None:
        font = pg.font.SysFont("comicsans.ttf", 40)
    surface.blit(font.render(text, True, (0, 0, 0)), pos)


def aa_rounded_rect_with_text(text, surface, rect, color, rad=20, border=0, inside=(0, 0, 0),
                              font=pg.font.SysFont("comicsans.ttf", 40)):
    aa_round_rect(surface, rect, color, rad, border, inside)
    text_surf = font.render(text, True, (0, 0, 0))
    text_rect = text_surf.get_rect()
    text_rect.center = ((rect[0] + (rect[2] / 2)), (rect[1] + (rect[3] / 2)))
    surface.blit(text_surf, text_rect)


def aa_round_rect(surface, rect, color, rad=20, border=0, inside=(0, 0, 0)):
    """
    Draw an antialiased rounded rect on the target surface.  Alpha is not
    supported in this implementation but other than that usage is identical to
    round_rect.
    """
    rect = pg.Rect(rect)
    _aa_render_region(surface, rect, color, rad)
    if border:
        rect.inflate_ip(-2 * border, -2 * border)
        _aa_render_region(surface, rect, inside, rad)


def _aa_render_region(image, rect, color, rad):
    """Helper function for aa_round_rect."""
    corners = rect.inflate(-2 * rad - 1, -2 * rad - 1)
    for attribute in ("topleft", "topright", "bottomleft", "bottomright"):
        x, y = getattr(corners, attribute)
        gfxdraw.aacircle(image, x, y, rad, color)
        gfxdraw.filled_circle(image, x, y, rad, color)
    image.fill(color, rect.inflate(-2 * rad, 0))
    image.fill(color, rect.inflate(0, -2 * rad))
