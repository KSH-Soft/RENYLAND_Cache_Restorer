from discord_webhook import DiscordWebhook, DiscordEmbed
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QDialog, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QRect, QResource, QThread, pyqtSignal, QSize, QMetaObject
from PyQt5 import QtGui, QtWidgets
from pathlib import Path
import os
from datetime import datetime
import zipfile
from shutil import rmtree

version = "V1.0"
TMP_folder = os.path.join(os.getenv('TMP'))
username = os.path.join(os.getenv('username'))
appdata_locallow = os.path.join(os.getenv('APPDATA'), '..', 'LocalLow')
appdata_locallow = appdata_locallow.replace("Roaming\\..\\LocalLow", "LocalLow")

webhook_url = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
webhook = DiscordWebhook(url=webhook_url)

class Worker(QThread):
    status_update_signal = pyqtSignal(str)

    def __init__(self, cache_dir):
        super().__init__()
        self.cache_dir = cache_dir
        self.found_dirs = []

    def run(self):
        target_dirs = ["Anyland", "cache", "thingdefs"]
        self.status_update_signal.emit(f"[SYS] Target : {self.cache_dir}")
        self.status_update_signal.emit("[SYS] Search : \"Anyland/cache/thingdefs\"")

        for dirpath in Path(self.cache_dir).rglob('*'):
            parts = dirpath.parts
            if len(parts) >= 3 and parts[-3:] == tuple(target_dirs):
                self.found_dirs.append(str(dirpath))
                self.status_update_signal.emit(f"[SYS] Found : \"{dirpath}\"")
        self.status_update_signal.emit("[SYS] Search finished.")
        if self.found_dirs == []:
            self.status_update_signal.emit("")
            self.status_update_signal.emit("")
            self.status_update_signal.emit("[SYS] No cache files were found in the search directory.")
            return
        self.zip_found_dirs()
        
    def zip_found_dirs(self):
        self.status_update_signal.emit("[SYS] Start compressing folders into a ZIP file...")
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        heure = now.strftime("%H-%M-%S")
        output_base_path = os.path.join(TMP_folder, f"REnyland-Restorer\\{date}_{heure}")
        max_size_mb=20
        max_size_bytes = max_size_mb * 1024 * 1024
        total_size = 0
        if not os.path.exists(output_base_path):
            os.makedirs(output_base_path)
        folder_num = 0
        for found_dir in self.found_dirs:
            folder_num += 1
            part_num = 1
            total_size = 0
            print(f"ZIP : {found_dir}")
            current_zip_filename = f"{output_base_path}\\{folder_num}-CacheRestoredFrom-{username}_part{part_num}.zip"
            self.status_update_signal.emit(f"[SYS] Compressing : Folder-{folder_num} ({found_dir})")
            zipf = zipfile.ZipFile(current_zip_filename, 'w', zipfile.ZIP_DEFLATED)
            for root, dirs, files in os.walk(found_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    if total_size + file_size > max_size_bytes:
                        zipf.close()
                        part_num += 1
                        current_zip_filename = f"{output_base_path}\\{folder_num}-CacheRestoredFrom-{username}_part{part_num}.zip"
                        zipf = zipfile.ZipFile(current_zip_filename, 'w', zipfile.ZIP_DEFLATED)
                        total_size = 0

                    zipf.write(file_path, os.path.relpath(file_path, found_dir))
                    total_size += file_size
            zipf.close()
        self.status_update_signal.emit("[SYS] Compressing finished.")
        file_count = len([f for f in os.listdir(output_base_path) if os.path.isfile(os.path.join(output_base_path, f))])
        file_counter = 0
        for filename in os.listdir(output_base_path):
            webhook.clear_attachments()
            embed = DiscordEmbed()
            embed.set_title(f'New Cache Uploaded by {username} !')
            file_counter += 1
            self.status_update_signal.emit(f"[SYS] Upload to server : {file_counter}\\{file_count}")
            embed.set_description(f'Upload {file_counter}\\{file_count} JSON Thing Def')
            with open(os.path.join(output_base_path, filename), "rb") as f:
                webhook.add_file(file=f.read(), filename=filename)
            webhook.add_embed(embed)
            response = webhook.execute(remove_embeds=True)
            if response.status_code == 200:
                self.status_update_signal.emit("[SYS] Server Response : OK, Upload DONE")
            else:
                self.status_update_signal.emit(f"[SYS] Server Response : {response}")
                self.status_update_signal.emit("")
                self.status_update_signal.emit("[SYS-ADMIN] PLS CONTACT MY DEV FOR HELP ! ")
                self.status_update_signal.emit("[SYS-ADMIN] Discord : axsys ! ")
                self.status_update_signal.emit("[SYS-ADMIN] PLS CONTACT MY DEV FOR HELP ! ")
                return
        self.status_update_signal.emit("")
        self.status_update_signal.emit("")
        self.status_update_signal.emit("[SYS] All process DONE")
        self.status_update_signal.emit("")
        self.status_update_signal.emit("[Admin] Thank you for sharing this valuable information with us.")
        self.status_update_signal.emit("[Admin] Thanks to you, we'll be able to restore even more objects !")
        self.status_update_signal.emit("[Admin] We hope to see you soon in REnyland !")
  
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.MainWindow = MainWindow
        self.MainWindow.setWindowTitle("Renyland_Cache_Restorer")
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(600, 300)
        app_icon = QtGui.QIcon()
        app_icon.addFile(':/Assets/logo.ico', QSize(48, 48))
        MainWindow.setWindowIcon(app_icon)
        MainWindow.setWindowFlags(Qt.FramelessWindowHint)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.CustomBrows = QtWidgets.QPushButton(self.centralwidget)
        self.CustomBrows.setGeometry(QRect(415, 236, 171, 31))
        self.CustomBrows.setStyleSheet("QPushButton {\n"
"                background-color: #2a75bf;\n"
"                color: black;\n"
"                border-radius: 8px;\n"
"                padding: 4px 8px;\n"
"                font-size: 12px;\n"
"                font-weight: bold;\n"
"            }\n"
"            QPushButton:hover {\n"
"                background-color: #0058ae;\n"
"            }\n"
"            QPushButton:pressed {\n"
"                background-color: #00468b;\n"
"            }")
        self.CustomBrows.setObjectName("CustomBrows")
        self.CustomBrows.mouseReleaseEvent = self.OnCustomPlay
        
        self.CROSS = QtWidgets.QLabel(self.centralwidget)
        self.CROSS.setGeometry(QRect(576, 4, 20, 20))
        self.CROSS.setStyleSheet("image: url(:/Assets/croixx.png);")
        self.CROSS.setText("")
        self.CROSS.setObjectName("CROSS")
        self.CROSS.mouseReleaseEvent = self.exit_clicked
        
        self.StartBrows = QtWidgets.QPushButton(self.centralwidget)
        self.StartBrows.setGeometry(QRect(415, 174, 171, 51))
        self.StartBrows.setStyleSheet("QPushButton {\n"
"                background-color: #2a75bf;\n"
"                color: black;\n"
"                border-radius: 8px;\n"
"                padding: 4px 8px;\n"
"                font-size: 12px;\n"
"                font-weight: bold;\n"
"            }\n"
"            QPushButton:hover {\n"
"                background-color: #0058ae;\n"
"            }\n"
"            QPushButton:pressed {\n"
"                background-color: #00468b;\n"
"            }")
        self.StartBrows.setObjectName("StartBrows")
        self.StartBrows.mouseReleaseEvent = self.OnPlay
        
        self.BG = QtWidgets.QLabel(self.centralwidget)
        self.BG.setGeometry(QRect(0, 0, 601, 301))
        self.BG.setStyleSheet("background-image: url(:/Assets/bg.png);")
        self.BG.setText("")
        self.BG.setObjectName("label")
        self.BG.mousePressEvent = self.mousePressEvent
        self.BG.mouseMoveEvent = self.mouseMoveEvent
        self.BG.mouseReleaseEvent = self.mouseReleaseEvent
        
        self.INFO = QtWidgets.QLabel(self.centralwidget)
        self.INFO.setGeometry(QRect(575, 276, 20, 20))
        self.INFO.setStyleSheet("image: url(:/Assets/info.png);")
        self.INFO.setText("")
        self.INFO.setObjectName("INFO")
        self.INFO.mouseReleaseEvent = self.Info
        self.STATUS = QtWidgets.QTextEdit(self.centralwidget)
        self.STATUS.setGeometry(QRect(10, 166, 393, 124))
        font = QtGui.QFont()
        font.setKerning(True)
        self.STATUS.setFont(font)
        self.STATUS.setAcceptDrops(False)
        self.STATUS.setStyleSheet("background-color: transparent; color: white;font-weight: bold;font-size: 12px;-webkit-text-stroke: 2px #fff;\n"
"            QTextEdit {\n"
"                scrollbar-color: #2a75bf transparent; /* Couleur de la barre de défilement et de l\'arrière-plan */\n"
"                scrollbar-width: thin; /* Définir l\'épaisseur de la barre de défilement */\n"
"            }\n"
"            QTextEdit::vertical scrollbar:hover {\n"
"                background-color: #dcdcdc;\n"
"                border-radius: 10px;\n"
"            }\n"
"\n"
"            QTextEdit::vertical scrollbar {\n"
"                width: 8px; /* Largeur de la barre de défilement verticale */\n"
"                background-color: #f0f0f0; /* Arrière-plan de la barre de défilement */\n"
"                border-radius: 4px; /* Coins arrondis */\n"
"            }\n"
"\n"
"            QTextEdit::vertical scrollbar:handle {\n"
"                background-color: #2a75bf; /* Couleur du curseur de la scrollbar */\n"
"                border-radius: 4px; /* Coins arrondis du curseur */\n"
"            }\n"
"\n"
"            QTextEdit::horizontal scrollbar {\n"
"                height: 8px; /* Hauteur de la barre de défilement horizontale */\n"
"                background-color: #f0f0f0;\n"
"                border-radius: 4px;\n"
"            }\n"
"\n"
"            QTextEdit::horizontal scrollbar:handle {\n"
"                background-color: #2a75bf;\n"
"                border-radius: 4px;\n"
"            }")
        self.STATUS.setObjectName("textEdit")
        self.STATUS.setReadOnly(True)
        
        self.version = QLabel(self.centralwidget)
        self.version.setObjectName(u"version")
        self.version.setGeometry(QRect(543, 276, 31, 20))
        self.version.setAlignment(Qt.AlignCenter)
        self.version.setText(version)
        self.version.setStyleSheet("color: white;")
        
        self.BG.raise_()
        self.CustomBrows.raise_()
        self.CROSS.raise_()
        self.StartBrows.raise_()
        self.INFO.raise_()
        self.STATUS.raise_()
        self.version.raise_()
        
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def OnPlay(self,event):
        self.STATUS.setText('')
        self.status_update("[SYS] Starting default search...")
        self.worker = Worker(appdata_locallow)
        self.worker.status_update_signal.connect(self.status_update)
        self.worker.start()

    def OnCustomPlay(self,event):
        self.STATUS.setText('')
        self.status_update("[SYS] Starting Custom search...")
        FolderToSearch = QFileDialog.getExistingDirectory(None, "Select a folder")
        self.worker = Worker(FolderToSearch)
        self.worker.status_update_signal.connect(self.status_update)
        self.worker.start()
        
    def Info(self,event):  
        dialog = QDialog(self.MainWindow, Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
        dialog.setWindowTitle("Some Information")
        app_icon = QtGui.QIcon()
        app_icon.addFile(':/Assets/logo.ico', QSize(48, 48))
        dialog.setWindowIcon(app_icon)
        layout = QVBoxLayout(dialog)
        self.LabelInfo = QLabel("Renyland Cache_Restorer is a program designed to\n"
"analyse folders in order to detect files that can be used\n"
"to restore items that have now been lost for the new\n"
"Anyland game server, called REnyland\n"
"We sincerely thank you for every cache donation you send us.\n"
"\n"
"Thanks to your contribution,\n"
"We'll be able to restore even more items to the server\n"
"and provide an optimal gaming experience!\n\n", dialog)
        self.LabelInfo.setFont(QtGui.QFont('Arial', 8))        
        layout.addWidget(self.LabelInfo)
        folder_path = os.path.join(TMP_folder, "REnyland-Restorer")
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)
        total_size = total_size / (1024 * 1024)   
        self.save_button = QtWidgets.QPushButton(f"CLEAR TMP  (TMP Size : {total_size:.2f}Mo)", dialog)
        self.save_button.setFont(QtGui.QFont('Arial', 8))
        self.save_button.clicked.connect(self.cleartmp)
        layout.addWidget(self.save_button)
                
        text_icon_layout = QHBoxLayout()
        self.info_label = QLabel("Admin-DEV : Axsys (aka KSH-SOFT)\nLicence : Do What The Fuck You Want to Public License", dialog)
        self.info_label.setFont(QtGui.QFont('Arial', 8))
        self.info_label.setAlignment(Qt.AlignCenter)
        text_icon_layout.addWidget(self.info_label)

        self.icon_label = QLabel(dialog)
        icon = QtGui.QPixmap(":/Assets/wtfpl.png").scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(icon)
        text_icon_layout.addWidget(self.icon_label)

        text_icon_layout.setAlignment(Qt.AlignCenter)
        layout.addLayout(text_icon_layout)
    
        dialog.setLayout(layout)
        dialog.exec_()
        
    def cleartmp(self):
        folder_path = os.path.join(TMP_folder, "REnyland-Restorer")
        if os.path.exists(folder_path):
            rmtree(folder_path)
        self.save_button.setText('TMP CLEARED !!')

    def exit_clicked(self, event):
        sys.exit(0)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - MainWindow.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'drag_position') and event.buttons() == Qt.LeftButton:
            MainWindow.move(event.globalPos() - self.drag_position)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        if hasattr(self, 'drag_position'):
            del self.drag_position
            
    def status_update(self, message):
        self.STATUS.append(message)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("MainWindow")
        self.CustomBrows.setText("Custom Folder Browser")
        self.StartBrows.setText("START\nStandard Cache Restorer")
        self.STATUS.setText("For more information, click on the (i) at the bottom right.\n\n"
                            "To start, click on one of the buttons on the right")
 
import ressources

if __name__ == "__main__":
    import sys
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
