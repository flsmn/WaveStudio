"""Exact pixel dimensions with automatic square-cell spacing and time stepping."""
from dataclasses import replace
from .quality import PRESET_AXIS_CELLS
from .resources import MAX_AXIS_CELLS

AUTO_COURANT=.5


def pixel_dimensions(settings):
    return round(settings.width/settings.dx),round(settings.height/settings.dx)


def pixel_settings(settings,width,height):
    for name,value in (('Width',width),('Height',height)):
        if type(value) is not int or not 8<=value<=MAX_AXIS_CELLS:
            raise ValueError(f'{name} must be a whole number between 8 and {MAX_AXIS_CELLS} pixels.')
    # Preserve object coordinates and cover the old domain when aspect changes.
    spacing=max(settings.width/width,settings.height/height)
    return replace(settings,width=width*spacing,height=height*spacing,dx=spacing,
                   courant=AUTO_COURANT,quality='Custom')


def resolution_preset(width,height,name):
    factor=PRESET_AXIS_CELLS[name]/max(width,height)
    return max(8,round(width*factor)),max(8,round(height*factor))


def preset_name(width,height):
    return next((name for name,axis in PRESET_AXIS_CELLS.items() if max(width,height)==axis),'Custom')
