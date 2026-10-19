"""Opt-in dispatch/GC trace around the existing real-event-loop MPS diagnostic.

No extra polling timers; instrumentation is diagnostic, not a matched FPS or
resource-acceptance run. Event/sleep spans locate a gap but do not establish its
cause (e.g. OS wakeup, GIL scheduling and native calls can overlap).
"""
import argparse
from collections import deque
import gc
import json
from pathlib import Path
import threading
import time

from PySide6.QtCore import QAbstractEventDispatcher
from PySide6.QtWidgets import QApplication
from wave_studio import performance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seconds', type=float, default=30.)
    parser.add_argument('--warmup', type=float, default=15.)
    parser.add_argument('--context', default='No concurrent-work context supplied; not an acceptance report.')
    parser.add_argument('--resource-check', action='store_true', help='Trace the existing balanced resource workflow instead of the FPS diagnostic.')
    parser.add_argument('--case', choices=['one_view_economical', 'two_views_economical', 'two_views_performance'],
                        default='one_view_economical')
    args = parser.parse_args()
    started = time.monotonic()
    events, collections, sleeps = deque(maxlen=512), deque(maxlen=128), deque(maxlen=256)
    collecting = {}
    current_block = None
    maximum_dispatch_ms = 0.
    def stamp():
        return time.monotonic()-started
    def gc_event(phase, info):
        key = threading.get_ident()
        if phase == 'start':
            collecting[key] = time.monotonic()
        elif key in collecting:
            elapsed = (time.monotonic()-collecting.pop(key))*1000
            if elapsed >= 1:
                collections.append({'at_seconds': stamp(), 'milliseconds': elapsed,
                                    'thread': key, 'generation': info['generation']})
    class TracingApplication(QApplication):
        def notify(self, receiver, event):
            nonlocal maximum_dispatch_ms
            began = time.monotonic()
            kind, name = int(event.type()), type(receiver).__name__
            try:
                return super().notify(receiver, event)
            finally:
                elapsed = (time.monotonic()-began)*1000
                maximum_dispatch_ms = max(maximum_dispatch_ms, elapsed)
                if elapsed >= 10:
                    events.append({'at_seconds': stamp(), 'milliseconds': elapsed,
                                   'receiver': name, 'event_type': kind,
                                   'thread': threading.get_ident()})
        def __init__(self, *arguments):
            super().__init__(*arguments)
            dispatcher = QAbstractEventDispatcher.instance()
            def blocked():
                nonlocal current_block
                current_block = time.monotonic()
            def awake():
                nonlocal current_block
                if current_block is not None:
                    elapsed = (time.monotonic()-current_block)*1000
                    if elapsed >= 100:
                        sleeps.append({'at_seconds': stamp(), 'milliseconds': elapsed})
                    current_block = None
            dispatcher.aboutToBlock.connect(blocked)
            dispatcher.awake.connect(awake)
    original = performance.QApplication
    performance.QApplication = TracingApplication
    gc.callbacks.append(gc_event)
    try:
        if args.resource_check:
            import check_balanced_resources as balanced
            original_resource_app=balanced.QApplication
            balanced.QApplication=TracingApplication
            try:return balanced.main(['--output-dir',str(args.output)])
            finally:balanced.QApplication=original_resource_app
        return performance.run_performance(args.output, seconds=args.seconds, warmup=args.warmup,
                                           accessibility=True, case=args.case)
    finally:
        performance.QApplication = original
        gc.callbacks.remove(gc_event)
        trace = {'instrumented': True, 'extra_polling_timers': False,
                 'case': 'balanced_resource_all_cases' if args.resource_check else args.case,
                 'context': args.context,
                 'includes_startup_and_shutdown': True, 'maximum_dispatch_ms': maximum_dispatch_ms,
                 'main_thread': threading.main_thread().ident,
                 'long_dispatches': list(events), 'long_gc_collections': list(collections),
                 'long_dispatcher_block_intervals': list(sleeps),
                 'interpretation': 'Diagnostic context only. Nested dispatches overlap; do not sum spans. A long block interval is not proof of App Nap or an application stall.'}
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output/'event-trace.json').write_text(json.dumps(trace, indent=2)+'\n')


if __name__ == '__main__':
    raise SystemExit(main())
