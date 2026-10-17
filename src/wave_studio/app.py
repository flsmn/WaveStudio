import argparse
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description='Wave Studio desktop workbench')
    parser.add_argument('--smoke-test',action='store_true',help='Start, run briefly and close automatically')
    parser.add_argument('--check-workflow',metavar='OUTPUT_DIR',help='Run the local integration check and write its artifacts')
    args = parser.parse_args(argv)
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
