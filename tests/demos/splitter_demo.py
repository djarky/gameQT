import sys
import os

# Ensure gameqt is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gameqt import QApplication, QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QLabel, Qt, QColor

def main():
    app = QApplication(sys.argv)
    
    # Main Window
    main_window = QWidget()
    main_window.resize(800, 600)
    main_window.setWindowTitle("QSplitter Interactive Demo")
    
    layout = QVBoxLayout(main_window)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(10)
    
    title = QLabel("Try to drag the space between the colored panels!", main_window)
    layout.addWidget(title)
    
    # Horizontal Splitter
    splitter_h = QSplitter(Qt.Orientation.Horizontal)
    
    # Left Widget (Red)
    w1 = QWidget()
    w1.setStyleSheet("background-color: #FFCDD2; border: 1px solid #E57373; border-radius: 4px;")
    l1 = QVBoxLayout(w1); l1.addWidget(QLabel("Left Panel"))
    
    # Middle Widget (Green)
    w2 = QWidget()
    w2.setStyleSheet("background-color: #C8E6C9; border: 1px solid #81C784; border-radius: 4px;")
    l2 = QVBoxLayout(w2); l2.addWidget(QLabel("Middle Panel"))
    
    # Right Widget (Blue)
    w3 = QWidget()
    w3.setStyleSheet("background-color: #BBDEFB; border: 1px solid #64B5F6; border-radius: 4px;")
    l3 = QVBoxLayout(w3); l3.addWidget(QLabel("Right Panel"))
    
    splitter_h.addWidget(w1)
    splitter_h.addWidget(w2)
    splitter_h.addWidget(w3)
    
    # Set initial sizes (optional)
    splitter_h.setSizes([100, 200, 100])
    
    layout.addWidget(splitter_h)
    
    # Vertical Splitter section
    splitter_v = QSplitter(Qt.Orientation.Vertical)
    
    top = QWidget()
    top.setStyleSheet("background-color: #FFF9C4; border: 1px solid #FFF176;")
    l_top = QVBoxLayout(top); l_top.addWidget(QLabel("Top"))
    
    bottom = QWidget()
    bottom.setStyleSheet("background-color: #E1BEE7; border: 1px solid #BA68C8;")
    l_bottom = QVBoxLayout(bottom); l_bottom.addWidget(QLabel("Bottom"))
    
    splitter_v.addWidget(top)
    splitter_v.addWidget(bottom)
    
    layout.addWidget(splitter_v)
    
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
