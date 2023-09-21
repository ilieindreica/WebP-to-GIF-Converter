from PIL import Image
import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QFileDialog
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal


class ConverterThread(QThread):
    progress_signal = pyqtSignal(int, int)

    def __init__(self, input_dir, output_dir):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir

    def run(self):
        image_files = [filename for filename in os.listdir(self.input_dir) if filename.endswith('.webp')]
        total_images = len(image_files)
        converted_images = 0

        for filename in image_files:
            webp_path = os.path.join(self.input_dir, filename)
            image = Image.open(webp_path)
            image.info.pop('background', None) 

            gif_path = os.path.join(self.output_dir, os.path.splitext(filename)[0] + '.gif')
            image.save(gif_path, "GIF", save_all=True, lossless=True, quality=100, method=6)

            converted_images += 1
            self.progress_signal.emit(converted_images, total_images)


class WebToGifConverter(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("WebP to GIF Converter")
        self.setGeometry(100, 100, 400, 200)

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout(main_widget)

        self.input_button = QPushButton('Select Input Directory', self)
        self.input_button.clicked.connect(self.selectInputDirectory)
        layout.addWidget(self.input_button)

        self.convert_button = QPushButton('Convert', self)
        self.convert_button.clicked.connect(self.convert)
        layout.addWidget(self.convert_button)

        self.directory_label = QLabel('', self)
        layout.addWidget(self.directory_label)

        self.progress_label = QLabel('', self)
        layout.addWidget(self.progress_label)

        self.input_directory = None

    def selectInputDirectory(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self.input_directory = QFileDialog.getExistingDirectory(self, "Select Input Directory", options=options)
        if self.input_directory:
            self.directory_label.setText(f'Selected Directory: {self.input_directory}')
    
    def convert(self):
        if self.input_directory is not None:
            output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")            

            self.converter_thread = ConverterThread(self.input_directory, output_dir)                   
            self.converter_thread.progress_signal.connect(self.updateProgressLabel)
            self.converter_thread.start()            
    
    def updateProgressLabel(self, converted_images, total_images):
        self.progress_label.setText(f'Converted: {converted_images}/{total_images}')

def main():
    app = QApplication(sys.argv)
    converter = WebToGifConverter()
    converter.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
