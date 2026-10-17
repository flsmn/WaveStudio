from wave_sim2d.config import Grid, Material, Source, Wall
from wave_sim2d.geometry import prepare_scene
from wave_studio.domain.project import MaterialObject, SourceObject, WallObject


def compile_project(project):
    project.validate()
    s = project.settings
    grid = Grid(round(s.width/s.dx),round(s.height/s.dx),s.dx,s.dx*s.courant,s.border_width,s.border_rate)
    materials, walls, sources = [], [], []
    for obj in project.objects:
        if isinstance(obj,MaterialObject):
            materials.append(Material(obj.vertices,obj.refractive_index,obj.damping_rate))
        elif isinstance(obj,WallObject):
            walls.append(Wall(obj.x,obj.y,obj.width,obj.height))
        elif isinstance(obj,SourceObject):
            sources.append(Source(obj.start,obj.end,obj.wavelength,obj.amplitude,obj.phase))
    return prepare_scene(grid,materials,walls,sources)
