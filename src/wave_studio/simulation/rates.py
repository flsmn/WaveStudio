"""Rates of advancing UI frames, excluding startup and paused intervals."""
class FrameRates:
    def __init__(self):self.reset()

    def reset(self):
        self.started=None;self.first_steps=0;self.last_steps=None;self.frames=0

    def observe(self,steps,now):
        if steps<=0 or steps==self.last_steps:return None
        self.last_steps=steps
        if self.started is None:
            self.started=now;self.first_steps=steps;return None
        self.frames+=1;elapsed=now-self.started
        if elapsed<1:return None
        result=((steps-self.first_steps)/elapsed,self.frames/elapsed)
        self.started=now;self.first_steps=steps;self.frames=0
        return result
