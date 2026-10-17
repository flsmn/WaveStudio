"""Project resource policy; estimates are not total process or GPU allocations."""
DEFAULT_BUFFER_MIB = 512
DEFAULT_AXIS_CELLS = 4096
# Finite editor ranges prevent malformed imports from bypassing the UI policy.
MAX_BUFFER_MIB = 65536
MAX_AXIS_CELLS = 65536


def validate_limits(settings):
    for name,minimum,maximum in (('buffer_limit_mib',1,MAX_BUFFER_MIB),('max_axis_cells',8,MAX_AXIS_CELLS)):
        value=getattr(settings,name)
        if type(value) is not int or not minimum <= value <= maximum:
            raise ValueError(f'{name} must be a whole number between {minimum} and {maximum}.')


def buffer_bytes(nx,ny):
    return nx*ny*72


def rejection(settings,nx,ny):
    validate_limits(settings)
    memory=buffer_bytes(nx,ny)
    if min(nx,ny)<8 or max(nx,ny)>settings.max_axis_cells or memory>settings.buffer_limit_mib*1024**2:
        return (f'Grid needs {nx} × {ny} cells and {memory/1024**2:.1f} MiB of estimated numerical buffers; '
                f'configured limits: {settings.max_axis_cells} cells per axis and {settings.buffer_limit_mib} MiB. '
                'Reduce resolution/domain or adjust Resource limits in Simulation settings. Runtime memory is additional.')
    return ''


def summary(settings,nx,ny):
    reason=rejection(settings,nx,ny)
    if reason:return reason
    text=(f'{nx} × {ny} · {buffer_bytes(nx,ny)/1024**2:.1f} MiB estimated numerical buffers '
          f'(budget {settings.buffer_limit_mib} MiB; {settings.max_axis_cells} cells/axis). Runtime memory is additional.')
    if buffer_bytes(nx,ny)>DEFAULT_BUFFER_MIB*1024**2 or max(nx,ny)>DEFAULT_AXIS_CELLS:
        text+=' Large grid: allow for slower startup/steps. Pause and Reset wait for the current step.'
    return text
