from dataclasses import replace
import pytest
from wave_studio.domain.project import Project, MaterialObject, SourceObject, with_source
from wave_studio.simulation.lifecycle import Lifecycle, State
from wave_studio.simulation.compiler import compile_project
from wave_studio.simulation.worker import Latest


def test_pause_resume_step_change_reset_reject_stale_frames():
    c = Lifecycle('project')
    assert not c.can_step
    assert c.run()
    identity = c.identity
    assert c.accepts(identity)
    with pytest.raises(ValueError): c.physical_change()
    c.pause()
    assert c.can_step
    assert not c.run() and c.identity == identity
    c.pause()
    c.physical_change()
    assert c.state == State.CHANGED and not c.can_step and not c.accepts(identity)
    assert c.run() and c.identity != identity
    previous = c.identity
    c.reset()
    assert not c.can_step and not c.accepts(previous)
    assert c.state == State.READY
    assert c.run() and c.identity != previous
    c.fail('Device disconnected')
    assert c.state == State.ERROR and c.error == 'Device disconnected'
    assert not c.can_step


def test_project_and_compiler_keep_geometry_and_invalid_candidate():
    original = Project()
    candidate = with_source(original,wavelength=3)
    assert candidate.objects[0].start == original.objects[0].start
    compiled = compile_project(original)
    other = compile_project(candidate)
    assert other.grid == compiled.grid
    with pytest.raises(ValueError):
        compile_project(with_source(original,wavelength=float('nan')))
    assert original.objects[0].wavelength == 2
    material = MaterialObject()
    with_material = replace(original,objects=original.objects+(material,))
    assert compile_project(with_material).refractive_index.max() == 1.5
    finer = replace(with_material,settings=replace(with_material.settings,dx=.0625))
    assert compile_project(finer).grid.width == compiled.grid.width
    assert finer.objects == with_material.objects


def test_bounded_latest_mailbox():
    latest = Latest()
    for value in range(10000): latest.put(value)
    assert latest.take() == 9999
    assert latest.take() is None
