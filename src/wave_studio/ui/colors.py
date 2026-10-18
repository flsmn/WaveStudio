"""Color maps shared by both image panes and their color bars."""
from functools import lru_cache
import pyqtgraph as pg


@lru_cache(maxsize=9)
def color_map(view, scheme):
    if view == 'Field':
        colors = {
            'Classic': ['#3684d6', '#101925', '#f0bd74'],
            'Blue / Red': ['#2166ac', '#f7f7f7', '#b2182b'],
            'Purple / Green': ['#762a83', '#f7f7f7', '#1b7837'],
            'Grayscale': ['#000000', '#808080', '#ffffff'],
        }[scheme]
        return pg.ColorMap([0, .5, 1], colors)
    if scheme in ('Viridis', 'Inferno', 'Plasma'):
        return pg.colormap.get(scheme.lower())
    colors = {'Classic': ['#101925', '#f0ca78'],
              'Grayscale': ['#000000', '#ffffff']}[scheme]
    return pg.ColorMap([0, 1], colors)
