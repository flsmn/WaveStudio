from wave_sim2d.config import Grid, Material, Source, Wall
from wave_sim2d.geometry import prepare_scene, lens_vertices
from wave_sim2d.measurements import Detector
from wave_studio.domain.project import MaterialObject, SourceObject, WallObject, LensObject


def compile_project(project):
    project.validate()
    s = project.settings
    if s.quality!='Custom':
        from wave_studio.domain.quality import estimate,PRESETS,wall_cell_ties
        e=estimate(project,s.quality,s.dx);wave_cells,feature_cells,budget=PRESETS[s.quality]
        if not e.supported:raise ValueError(e.reason)
        if wall_cell_ties(project,s.dx) or e.cells_per_wavelength<wave_cells-1e-7 or e.cells_per_feature is not None and e.cells_per_feature<feature_cells-1e-7 or e.phase_radians>budget+1e-7:
            raise ValueError('This grid no longer meets the selected quality. Reapply the preset or choose Custom.')
    grid = Grid(round(s.width/s.dx),round(s.height/s.dx),s.dx,s.dx*s.courant,s.border_width,s.border_rate)
    materials, walls, sources = [], [], []
    for obj in project.objects:
        if isinstance(obj,MaterialObject):
            materials.append(Material(obj.vertices,obj.refractive_index,obj.damping_rate))
        elif isinstance(obj,LensObject):
            materials.append(Material(lens_vertices(obj.x,obj.y,obj.radius,obj.aperture,obj.angle),obj.refractive_index,obj.damping_rate))
        elif isinstance(obj,WallObject):
            walls.append(Wall(obj.x,obj.y,obj.width,obj.height))
        elif isinstance(obj,SourceObject):
            sources.append(Source(obj.start,obj.end,obj.wavelength,obj.amplitude,obj.phase))
    for detector in project.detectors: detector_spec(detector,0).validate(grid)
    if grid.estimated_bytes > 512*1024**2:
        raise ValueError("Estimated numerical buffers exceed the 512 MiB development budget. Reduce resolution.")
    return prepare_scene(grid,materials,walls,sources)


def detector_spec(obj,revision):
    return Detector(obj.id,obj.start,obj.end,obj.samples,obj.settling,obj.window,revision)
