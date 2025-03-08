# -*- coding utf-8 -*-
# 这不是我写的，我直接cv过来改了一下)


from __future__ import annotations
import sys
from datetime import datetime
import psutil

from PySide6.QtCore import QThread, Signal, Slot
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget
from supervice import supervicer




class SuperviceTread(QThread):
    def __init__(self, debug):
        super().__init__()
        self.debug = debug
        self.supervice = supervicer(debug)

    def run(self):
        self.supervice.notStop = True
        self.supervice.startSupervice(True, False)

    def pauseOrContinue(self):
        if self.supervice.notStop == True:
            self.supervice.notStop = False
        else:
            self.supervice.notStop = True
            self.supervice.startSupervice(True, False)


    def stop(self):
        self.supervice.notStop = False


class CountTread(QThread):
    update_count = Signal(str)  # 发送带时间戳的计数信息

    def __init__(self):
        super().__init__()
        self.running = False
        self.paused = False

    def run(self):
        count = 0
        self.running = True
        while self.running:
            if not self.paused:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = f"{timestamp} - Count: {count}"
                self.update_count.emit(message)
                count += 1
                self.sleep(1)

    def pause_or_resume(self):
        self.paused = not self.paused

    def stop(self):
        self.running = False
        self.paused = False


class MainWindow(QMainWindow):
    debug = False
    useDefaultConfig = True


    def debugPrint(self, outString):
        if self.debug:
            print("MainWd:\t",outString,'\n')


    def __init__(self,debug = False,usedefault = True):
        self.debug = debug
        self.useDefaultConfig = usedefault
        self.debugPrint("主窗口开始创建\n")
        self.totalmmr = str(round(psutil.virtual_memory().total / 1024 / 1024 / 1000, 2))#GB
        super().__init__()
        self.log_thread = SuperviceTread(debug)
        self.counter_thread = CountTread()
        self.start_button = QPushButton("Start", self)
        self.toggle_pause_button = QPushButton("Pause", self)
        self.stop_button = QPushButton("Stop", self)
        # 计算运行时长
        self.count_label = QLabel("Counter not started", self)
        # 显示占用内存
        self.using_mmr = QLabel("mmr:"+self.usingMMr()+"GB/"+self.totalmmr+"GB", self)
        self.init_ui()

    
    def usingMMr(self):
        return str(round(psutil.virtual_memory().used / 1024 / 1024 / 1000, 2))#GB


    def init_ui(self):
        self.debugPrint("创建ui界面\n")
        self.setWindowTitle("Spvc")

        self.start_button.clicked.connect(self.start_thread)
        self.toggle_pause_button.clicked.connect(self.toggle_pause)
        self.stop_button.clicked.connect(self.stop_thread)

        self.toggle_pause_button.setEnabled(False)  # 初始时Pause按钮不可用

        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.toggle_pause_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.count_label)
        layout.addWidget(self.using_mmr)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.counter_thread.update_count.connect(self.handle_count_update)

    @Slot(str)
    def handle_count_update(self, message):
        self.count_label.setText(message)

    def start_thread(self):
        if not self.counter_thread.isRunning():
            self.log_thread.start()
            self.counter_thread.start()
            self.toggle_pause_button.setText("Pause")
            self.toggle_pause_button.setEnabled(True)  # 启动后Pause按钮可用

    def toggle_pause(self):
        self.counter_thread.pause_or_resume()
        self.log_thread.pauseOrContinue()
        if self.counter_thread.paused:
            self.toggle_pause_button.setText("Resume")
        else:
            self.toggle_pause_button.setText("Pause")

    def stop_thread(self):
        self.counter_thread.stop()
        self.counter_thread.wait()  # 等待线程安全结束
        self.log_thread.stop()
        self.log_thread.wait()
        self.count_label.setText("Counter stopped")
        self.toggle_pause_button.setEnabled(False)  # 停止后Pause按钮不可用


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(False,True)
    window.show()
    sys.exit(app.exec())