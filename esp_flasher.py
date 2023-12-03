import sys
import subprocess
import psutil
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, \
    QFileDialog, QMessageBox


class ESPFlashTool(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("ESP Flash & Script Tool")

        layout = QVBoxLayout()

        # Port
        port_hbox = QHBoxLayout()
        self.port_label = QLabel("Port:")
        self.port_entry = QLineEdit("/dev/ttyUSB0")
        port_hbox.addWidget(self.port_label)
        port_hbox.addWidget(self.port_entry)
        layout.addLayout(port_hbox)

        # Firmware Path
        firmware_hbox = QHBoxLayout()
        self.firmware_path_label = QLabel("Firmware Path:")
        self.firmware_path_entry = QLineEdit()
        self.browse_firmware_button = QPushButton("Browse Firmware")
        self.browse_firmware_button.clicked.connect(self.browse_firmware_file)
        firmware_hbox.addWidget(self.firmware_path_label)
        firmware_hbox.addWidget(self.firmware_path_entry)
        firmware_hbox.addWidget(self.browse_firmware_button)
        layout.addLayout(firmware_hbox)

        # Script Path
        script_hbox = QHBoxLayout()
        self.script_path_label = QLabel("MicroPython Script Path:")
        self.script_path_entry = QLineEdit()
        self.browse_script_button = QPushButton("Browse Script")
        self.browse_script_button.clicked.connect(self.browse_script_file)
        script_hbox.addWidget(self.script_path_label)
        script_hbox.addWidget(self.script_path_entry)
        script_hbox.addWidget(self.browse_script_button)
        layout.addLayout(script_hbox)

        # Buttons
        self.erase_button = QPushButton("Erase Flash")
        self.erase_button.clicked.connect(self.erase_flash)
        self.write_button = QPushButton("Write Flash")
        self.write_button.clicked.connect(self.write_flash)
        self.upload_button = QPushButton("Upload Script")
        self.upload_button.clicked.connect(self.upload_script)
        self.check_script_button = QPushButton("Check if Script is Running")
        self.check_script_button.clicked.connect(self.check_script_status)

        layout.addWidget(self.erase_button)
        layout.addWidget(self.write_button)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.check_script_button)

        self.setLayout(layout)

    def erase_flash(self):
        port = self.port_entry.text()
        cmd = ["esptool.py", "--port", port, "erase_flash"]
        subprocess.run(cmd)

    def write_flash(self):
        port = self.port_entry.text()
        firmware_path = self.firmware_path_entry.text()
        cmd = [
            "esptool.py", "--port", port, "--baud", "115200",
            "write_flash", "--flash_size=detect", "0", firmware_path
        ]
        subprocess.run(cmd)

    def upload_script(self):
        port = self.port_entry.text()
        script_path = self.script_path_entry.text()
        cmd = [
            "ampy", "--port", port, "put", script_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            QMessageBox.information(self, "Upload Script", "Script uploaded successfully!")
        else:
            QMessageBox.critical(self, "Upload Script", f"Error uploading script:\n{result.stderr}")

    def browse_firmware_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Firmware File")
        if file_path:
            self.firmware_path_entry.setText(file_path)

    def browse_script_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Script File")
        if file_path:
            self.script_path_entry.setText(file_path)

    def is_script_running(self, script_name):
        for process in psutil.process_iter():
            try:
                pinfo = process.as_dict(attrs=['pid', 'name', 'cmdline'])
                if script_name in pinfo['name'] or script_name in ' '.join(pinfo['cmdline']):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def check_script_status(self):
        script_name = self.script_path_entry.text().split('/')[-1]
        if self.is_script_running(script_name):
            QMessageBox.information(self, "Status", f"{script_name} is running!")
        else:
            QMessageBox.information(self, "Status", f"{script_name} is not running.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ESPFlashTool()
    ex.show()
    sys.exit(app.exec_())
