# -*- coding: utf-8 -*-
import sys
import requests
import random
import re
from hashlib import md5
from PyQt5.QtWidgets import QApplication, QWidget,QVBoxLayout,QPushButton,\
QPlainTextEdit,QHBoxLayout,QSystemTrayIcon,QMenu,QAction
from PyQt5.QtCore import pyqtSignal,Qt
from PyQt5.QtGui import QTextCursor,QIcon

# Set your own appid/appkey.
#添加自己的appid和密码
appid = ''
appkey = ''

# For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
from_lang = 'auto'
to_lang =  'auto'

endpoint = 'http://api.fanyi.baidu.com'
path = '/api/trans/vip/translate'
url = endpoint + path
# Generate salt and sign

def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()

def tranlate(query):
    if query != '':
        salt = random.randint(32768, 65536)
        sign = make_md5(appid + query + str(salt) + appkey)

        # Build request
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

        # Send request
        r = requests.post(url, params=payload, headers=headers)
        result = r.json()

        dst_value = result["trans_result"][0]["dst"]
        return dst_value

class EnterTextEdit(QPlainTextEdit):
    returnPressed = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.returnPressed.emit()
        else:
            super().keyPressEvent(event)
            
class Translate_win(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("自制翻译器")
        self.setWindowIcon(QIcon('icon/translate_tool.ico'))
        self.screen_size = QApplication.primaryScreen().availableGeometry()
        self.win_width ,self.win_height,self.win_Margin= 400,200,200
        self.resize(self.win_width,self.win_height)
        self.move(self.screen_size.width()-self.win_width-self.win_Margin,self.win_Margin)
        # 移除最大化和最小化按钮
        self.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint, False)
        self.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint, False)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        self.input_text = EnterTextEdit()
        self.button = QPushButton(text="翻译")
        self.clear_button = QPushButton(text="X")
        self.output_text = QPlainTextEdit()
        self.clear_button.setMinimumSize(40,30)
        self.input_text.setMinimumSize(200, 80)
        self.output_text.setMinimumSize(200, 80)
        font = self.input_text.font()
        font.setPointSize(11)
        self.input_text.setFont(font) 
        self.output_text.setFont(font)
        
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('icon/translate_tool.ico'))
        self.tray_icon.setVisible(True)
        self.create_tray_menu()
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.setContextMenu(self.tray_menu)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.button,stretch=10)
        button_layout.addWidget(self.clear_button,stretch=1)
        
        layout  = QVBoxLayout()
        layout.addWidget(self.input_text)
        layout.addLayout(button_layout)
        layout.addWidget(self.output_text)
        layout.setContentsMargins(5,5,5,5)
        layout.setSpacing(2)
        self.setLayout(layout)
        
        self.input_text.returnPressed.connect(self.translate_text)
        self.clear_button.clicked.connect(self.clear)
        self.button.clicked.connect(self.translate_text)
        self.previous_text = ""
        
    def create_tray_menu(self):
        self.tray_menu = QMenu(self)
        show_action = QAction("显示窗口", self)
        show_action.triggered.connect(self.show_window)
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.exit_app)

        self.tray_menu.addAction(show_action)
        self.tray_menu.addAction(exit_action)
        
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()
            
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        
    def exit_app(self):
        self.tray_icon.setVisible(False)
        app.quit()
        
    def show_window(self):
        self.showNormal()
        self.activateWindow()
        
    def clear(self):
        self.input_text.clear()
        self.output_text.clear()
        
    def translate_text(self):
        current_text = self.input_text.toPlainText().replace('\n', '').replace('\r', '')
        current_text = re.sub(r'\s+', ' ', current_text)
        self.input_text.setPlainText(current_text)
        cursor = self.input_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.input_text.setTextCursor(cursor)
        self.input_text.setFocus()
        try:
            translated_text = tranlate(current_text)
        except Exception as e:
            print("Translation failed:", str(e))
            translated_text = "Translation failed. Please try again."
        self.output_text.setPlainText(translated_text)
        self.resizeTextEdit()

    def resizeTextEdit(self):
        if self.output_text.verticalScrollBar().maximum() != 0:
            window_width = self.screen_size.width() // 2
            window_height = self.screen_size.height() // 2
            self.resize(window_width, window_height)
            self.move(window_width,0)
        else:
            self.resize(self.win_width,self.win_height)
            self.move(self.screen_size.width()-self.win_width-self.win_Margin,self.win_Margin)


        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Translate_win()
    window.show()
    sys.exit(app.exec_())