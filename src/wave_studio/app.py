import argparse
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description='Wave Studio desktop workbench')
    parser.add_argument('--smoke-test',action='store_true',help='Start, run briefly and close automatically')
    parser.add_argument('--check-workflow',metavar='OUTPUT_DIR',help='Run the local integration check and write its artifacts')
    parser.add_argument('--check-performance',metavar='OUTPUT_DIR',help='Measure the Balanced MPS editor/worker with reproducible timings')
    parser.add_argument('--event-loop',choices=('native','pump'),default='native',help='Performance check only: Qt exec or historical processEvents pump')
    parser.add_argument('--performance-seconds',type=int,default=10,help='Performance check only: seconds per case (3–60)')
    args = parser.parse_args(argv)
    if args.check_performance:
        if not 3<=args.performance_seconds<=60:parser.error('Performance duration must be between 3 and 60 seconds.')
        from .performance import run_performance
        return run_performance(args.check_performance,args.event_loop,args.performance_seconds)
    if args.check_workflow:
        from .checks import run_workflow
        return run_workflow(args.check_workflow)
    import torch
    torch.set_num_threads(1)  # provisional economical CPU setting; see B03
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer
    from .ui.editor import MainWindow
    app = QApplication.instance() or QApplication(sys.argv[:1])
    app.setApplicationName('Wave Studio')
    app.setOrganizationName('Wave Studio')
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    if args.smoke_test:
        QTimer.singleShot(100,window.run_simulation)
        QTimer.singleShot(900,window.pause_simulation)
        QTimer.singleShot(1100,window.step_simulation)
        QTimer.singleShot(1400,window.reset_simulation)
        QTimer.singleShot(1700,window.close)
    return app.exec()
