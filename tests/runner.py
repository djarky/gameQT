
import sys
import os
import subprocess
import datetime

# Ensure gameqt is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if os.path.join(project_root, 'pdf_visual_editor') not in sys.path:
     sys.path.insert(0, os.path.join(project_root, 'pdf_visual_editor'))

from gameqt.application import QApplication
from gameqt.widgets import (QMainWindow, QWidget, QLabel, QPushButton, 
                             QCheckBox)
from gameqt.layouts import QVBoxLayout, QHBoxLayout, QGridLayout
from gameqt.core import Qt

class TestRunner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GameQt Test Runner")
        self.resize(800, 600)
        
        central = QWidget()
        main_layout = QVBoxLayout(central)
        
        # Header
        header = QLabel(central)
        header.setText("GameQt Test Suite")
        header.show()
        main_layout.addWidget(header)
        
        # Populating tests and demos
        self.tests = self.discover_tests()
        
        # Create test cards in a simple vertical list
        for test_name, test_path, test_type in self.tests:
            card = self.create_test_card(test_name, test_path, test_type, central)
            main_layout.addWidget(card)
        
        # Footer / Log actions
        exit_btn = QPushButton("Exit", central)
        exit_btn.clicked.connect(self.close)
        exit_btn.show()
        main_layout.addWidget(exit_btn)
        
        self.setCentralWidget(central)
        central.show()

    def discover_tests(self):
        """Scans directories for tests and demos."""
        tests = []
        
        # Demos
        demos_dir = os.path.join(current_dir, 'demos')
        if os.path.exists(demos_dir):
            for f in sorted(os.listdir(demos_dir)):
                if f.endswith('.py'):
                    name = f.replace('_', ' ').title().replace('.Py', '')
                    path = os.path.join(demos_dir, f)
                    tests.append((name, path, 'Demo'))
        
        # Unit Tests
        unit_dir = os.path.join(current_dir, 'unit')
        if os.path.exists(unit_dir):
             for f in sorted(os.listdir(unit_dir)):
                if f.startswith('test_') and f.endswith('.py'):
                    name = f.replace('_', ' ').title().replace('.Py', '')
                    path = os.path.join(unit_dir, f)
                    tests.append((name, path, 'Unit'))
                    
        return tests

    def create_test_card(self, name, path, test_type, parent):
        # Create a horizontal card layout
        card = QWidget(parent)
        card.resize(750, 40)
        
        layout = QHBoxLayout(card)
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title label
        title = QLabel(card)
        title.setText(f"[{test_type}] {name}")
        title.show()
        layout.addWidget(title)
        
        # Run button
        run_btn = QPushButton("Run", card)
        run_btn.clicked.connect(lambda: self.run_test(path))
        run_btn.show()
        layout.addWidget(run_btn)
        
        # Pass checkbox
        pass_chk = QCheckBox("Pass", card)
        pass_chk.stateChanged.connect(lambda s: self.log_result(name, "PASS" if s == 2 else "RESET"))
        pass_chk.show()
        layout.addWidget(pass_chk)
        
        # Fail checkbox
        fail_chk = QCheckBox("Fail", card)
        fail_chk.stateChanged.connect(lambda s: self.log_result(name, "FAIL" if s == 2 else "RESET"))
        fail_chk.show()
        layout.addWidget(fail_chk)
        
        card.show()
        return card

    def run_test(self, path):
        # Run in a separate process
        print(f"Running {path}...")
        subprocess.Popen([sys.executable, path])

    def log_result(self, name, result):
        if result == "RESET": return
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {name}: {result}\n"
        print(log_entry.strip())
        
        log_dir = os.path.join(current_dir, 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        with open(os.path.join(log_dir, 'test_report.log'), 'a') as f:
            f.write(log_entry)

def main():
    app = QApplication(sys.argv)
    runner = TestRunner()
    runner.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
