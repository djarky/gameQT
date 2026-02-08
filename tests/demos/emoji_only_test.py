import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from pdf_visual_editor.gameqt.application import QApplication
from pdf_visual_editor.gameqt.widgets.qwidget import QWidget
from pdf_visual_editor.gameqt.widgets.qlabel import QLabel
from pdf_visual_editor.gameqt.layouts.box_layout import QVBoxLayout
from pdf_visual_editor.gameqt.gui import QFont

def main():
    app = QApplication(sys.argv)
    
    window = QWidget()
    window.setWindowTitle("Only Emojis Test 🚀🌟✨")
    window.resize(600, 500)
    window.setStyleSheet("background-color: #ffffff;")
    
    layout = QVBoxLayout(window)
    
    # Just emojis, no text
    label1 = QLabel("🚀🚀🚀🚀🚀")
    label1.setFont(QFont("Arial", 60))
    label1.setStyleSheet("color: #ff0000; background-color: #ffffcc; border: 2px solid #ccc;")
    layout.addWidget(label1)
    
    label2 = QLabel("🌟✨🔥🌈🍎")
    label2.setFont(QFont("Arial", 60))
    label2.setStyleSheet("color: #0000ff; background-color: #cceeff; border: 2px solid #ccc;")
    layout.addWidget(label2)
    
    label3 = QLabel("✅👍🎸⚡💎")
    label3.setFont(QFont("Arial", 60))
    label3.setStyleSheet("color: #008800; background-color: #eeffee; border: 2px solid #ccc;")
    layout.addWidget(label3)
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
