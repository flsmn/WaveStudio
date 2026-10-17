from dataclasses import asdict,replace


def change_kind(before,after):
    def physical(settings):return replace(settings,quality='Custom',buffer_limit_mib=512,max_axis_cells=4096)
    if (physical(before.settings),before.objects,before.reference_length)!=(physical(after.settings),after.objects,after.reference_length): return 'physical'
    if before.detectors!=after.detectors: return 'measurement'
    return 'display'


class History:
    def __init__(self): self.undo_stack=[]; self.redo_stack=[]
    def push(self,before,after):
        if before==after: return
        self.undo_stack.append((before,after))
        self.undo_stack=self.undo_stack[-100:]
        self.redo_stack.clear()
    def undo(self):
        if not self.undo_stack: return None
        pair=self.undo_stack.pop(); self.redo_stack.append(pair); return pair[0]
    def redo(self):
        if not self.redo_stack: return None
        pair=self.redo_stack.pop(); self.undo_stack.append(pair); return pair[1]
