from __future__ import annotations

import sys
import asyncio

from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QGroupBox
from PyQt6 import uic
from PyQt6.QtGui import QCloseEvent
from qasync import QEventLoop, asyncSlot

if TYPE_CHECKING:
    import asyncio

    from .sparky import Sparky


class MainWindow(QMainWindow):
    loop: asyncio.AbstractEventLoop

    def __init__(self, robot: Sparky):
        super(MainWindow, self).__init__()

        self.robot = robot

        uic.loadUi("platform.ui", self)

        # Access the button from the UI file
        self.enableButton = self.findChild(QPushButton, "enableButton")
        self.enableButton.clicked.connect(self.on_enable)

        self.disableButton = self.findChild(QPushButton, "disableButton")
        self.disableButton.clicked.connect(self.on_disable)

        # Connect modeSelect group buttons
        self.modeSelect = self.findChild(QGroupBox, "modeSelect")
        if self.modeSelect:
            for btn in self.modeSelect.findChildren(QPushButton):
                btn.clicked.connect(self.on_mode_button)

    def set_mode_buttons_disabled(self, disabled: bool):
        for btn in self.modeSelect.findChildren(QPushButton):
            btn.setDisabled(disabled)

    async def set_enabled(self, en: bool):
        await self.robot.set_enabled(en)

        # print("Starting async task...")

        self.enableButton.setDown(True)
        self.disableButton.setDown(True)

        # print(self.robot.motion.count)

        # await asyncio.sleep(1)

        # print("Async task completed!")

        if self.robot.enabled:
            self.disableButton.setDisabled(False)
            self.enableButton.setDisabled(True)
            self.set_mode_buttons_disabled(True)
        else:
            self.disableButton.setDisabled(True)
            self.enableButton.setDisabled(False)
            self.set_mode_buttons_disabled(False)


    @asyncSlot()
    async def on_enable(self):
        checked_button = next((btn for btn in self.modeSelect.findChildren(QPushButton) if btn.isChecked()), None)

        self.robot.selected_mode_name = checked_button.objectName().replace("mode_", "")

        await self.set_enabled(True)


    @asyncSlot()
    async def on_disable(self):
        await self.set_enabled(False)

    def on_mode_button(self):
        active_button = self.sender()
        for btn in self.modeSelect.findChildren(QPushButton):
            btn.setChecked(btn is active_button)

    @classmethod
    def start(cls, robot: Sparky):
        app = QApplication(sys.argv)

        self = cls(robot)
        self.loop = QEventLoop(app)
        self.show()

        return self

    def closeEvent(self, event: QCloseEvent):
        print(event.type().name)

        # self.loop.create_task(self.on_close())

        self.robot.stop()

    # async def on_close(self):
    #     await self.robot.controller.set_led_color(0, 0, 255)
        # pass
