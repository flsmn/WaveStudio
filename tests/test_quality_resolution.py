"""Preset raster floors preserve geometry, Custom spacing and resource admission."""
from dataclasses import replace
import pytest
from wave_studio.domain.project import Project
from wave_studio.domain.quality import estimate


@pytest.mark.parametrize('name,axis',[('Preview',512),('Balanced',1024),('High Quality',1920)])
@pytest.mark.parametrize('width,height',[(32,32),(32,18),(18,32)])
def test_preset_resolution_floors_preserve_aspect_ratio(name,axis,width,height):
    project=Project(objects=())
    project=replace(project,settings=replace(project.settings,width=width,height=height))
    result=estimate(project,name)
    assert max(result.nx,result.ny)==axis
    assert result.nx/result.ny==pytest.approx(width/height)
    assert result.nx*result.dx==pytest.approx(width)
    assert result.ny*result.dx==pytest.approx(height)
    assert result.supported


def test_visual_resolution_floor_still_obeys_resource_budget():
    project=Project()
    project=replace(project,settings=replace(project.settings,buffer_limit_mib=32))
    result=estimate(project,'High Quality')
    assert (result.nx,result.ny)==(1920,1920)
    assert not result.supported and 'configured limits' in result.reason


def test_custom_grid_is_not_refined_by_display_resolution_floors():
    result=estimate(Project(),'Custom',.125)
    assert (result.nx,result.ny,result.dx)==(256,256,.125)
