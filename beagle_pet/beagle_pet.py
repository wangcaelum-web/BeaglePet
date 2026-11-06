#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比格多栋 Beagle Desktop Pet v2.0
使用原版角色形象的桌面宠物！
"""

import sys
import math
import random
import os

from PyQt5.QtWidgets import (
    QApplication, QWidget, QMenu, QMessageBox,
    QSystemTrayIcon, QDialog, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QSlider, QCheckBox
)
from PyQt5.QtCore import (
    Qt, QTimer, QPoint, QRect, QRectF
)
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush, QPixmap, QPainterPath,
    QFont, QIcon, QCursor, QTransform
)

# ============================================================
# PATHS (support both source and PyInstaller bundle)
# ============================================================
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle
    SCRIPT_DIR = sys._MEIPASS
else:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SPRITE_PATH = os.path.join(SCRIPT_DIR, "beagle_sprite.png")
SPRITE_FLIP_PATH = os.path.join(SCRIPT_DIR, "beagle_sprite_flip.png")
ICON_PATH = os.path.join(SCRIPT_DIR, "beagle_icon.png")

# ============================================================
# PET WINDOW
# ============================================================
class PetWindow(QWidget):
    """Frameless transparent window showing the Beagle."""

    def __init__(self):
        super().__init__()

        # Load sprites
        self.sprite = QPixmap(SPRITE_PATH)
        self.sprite_flip = QPixmap(SPRITE_FLIP_PATH)
        if self.sprite.isNull():
            self.sprite = QPixmap(129, 127)
            self.sprite.fill(Qt.transparent)
        if self.sprite_flip.isNull():
            self.sprite_flip = self.sprite

        # Sprite dimensions
        self.sprite_w = self.sprite.width()
        self.sprite_h = self.sprite.height()
        self.win_w = self.sprite_w + 20
        self.win_h = self.sprite_h + 20

        # State
        self.state = "idle"  # idle, walk, sit, sleep, happy
        self.state_timer = 0
        self.state_duration = random.randint(80, 200)
        self.dir = 1  # 1 = right, -1 = left
        self.facing_right = True

        # Position
        self.pos_x = 200
        self.pos_y = 200
        self.target_x = 200
        self.target_y = 200

        # Animation
        self.time_ms = 0
        self.walk_phase = 0
        self.bounce_offset = 0
        self.breath = 0
        self.blink_timer = 0
        self.blinking = False

        # Screen
        try:
            screen = QApplication.primaryScreen()
            if screen:
                self.screen_w = screen.geometry().width()
                self.screen_h = screen.geometry().height()
            else:
                self.screen_w, self.screen_h = 1920, 1080
        except:
            self.screen_w, self.screen_h = 1920, 1080

        # Window setup
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.SubWindow
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setGeometry(200, 200, self.win_w, self.win_h)

        # Interaction
        self.dragging = False
        self.drag_offset = QPoint()

        # Menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_anim)
        self.timer.start(33)  # ~30fps

        self.change_state("idle")

    def update_anim(self):
        """Main animation loop."""
        self.time_ms += 33
        self.state_timer += 1

        # Update breathing
        self.breath = math.sin(self.time_ms * 0.003) * 1.5
        # Blink check
        if self.blinking:
            self.blink_timer -= 1
            if self.blink_timer <= 0:
                self.blinking = False
        else:
            if random.random() < 0.005:
                self.blinking = True
                self.blink_timer = 4

        if self.state == "walk":
            self._update_walk()
        elif self.state == "idle":
            self._update_idle()
        elif self.state == "sit":
            if random.random() < 0.003:
                self.change_state("sleep")
        elif self.state == "sleep":
            if random.random() < 0.005:
                self.change_state("idle")
        elif self.state == "happy":
            pass  # Stays happy then changes

        # State timeout
        if self.state_timer > self.state_duration:
            self._next_state()

        self.update()

    def _update_walk(self):
        """Walking movement."""
        dx = self.target_x - self.pos_x
        dy = self.target_y - self.pos_y
        dist = math.sqrt(dx*dx + dy*dy)

        if dist < 8:
            self.change_state(random.choice(["idle", "sit", "happy"]))
            return

        speed = 2.0
        step = min(speed, dist)
        self.pos_x += (dx / dist) * step
        self.pos_y += (dy / dist) * step
        self.walk_phase += 0.15

        if dx > 1:
            self.facing_right = True
        elif dx < -1:
            self.facing_right = False

        self._clamp_pos()
        self.move(int(self.pos_x), int(self.pos_y))

    def _update_idle(self):
        """Idle actions."""
        r = random.random()
        if r < 0.003:
            self.change_state("happy")
        elif r < 0.002:
            self.change_state("sit")

    def _next_state(self):
        if self.state == "walk":
            self.change_state(random.choice(["idle", "sit"]))
        else:
            # 40% chance to walk somewhere
            if random.random() < 0.4:
                self._set_target()
                self.change_state("walk")
            else:
                self.change_state(random.choice(["idle", "sit", "happy"]))

    def _set_target(self):
        m = 60
        self.target_x = random.randint(m, max(m+10, self.screen_w - self.win_w - m))
        self.target_y = random.randint(m, max(m+10, self.screen_h - self.win_h - m))

    def _clamp_pos(self):
        m = 10
        self.pos_x = max(m, min(self.pos_x, self.screen_w - self.win_w - m))
        self.pos_y = max(m, min(self.pos_y, self.screen_h - self.win_h - m))

    def go_walk(self):
        self._set_target()
        self.change_state("walk")

    def change_state(self, new_state):
        self.state = new_state
        self.state_timer = 0
        self.state_duration = random.randint(80, 200)

    # ---- Painting ----
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        cx = self.win_w // 2
        cy = self.win_h // 2
        s = self.sprite_w / 129.0  # scale based on original

        if self.state == "walk":
            self._draw_walk(painter, cx, cy, s)
        elif self.state == "sit":
            self._draw_sit(painter, cx, cy, s)
        elif self.state == "sleep":
            self._draw_sleep(painter, cx, cy, s)
        elif self.state == "happy":
            self._draw_happy(painter, cx, cy, s)
        else:
            self._draw_idle(painter, cx, cy, s)

        # Draw state text (subtle)
        painter.setPen(QPen(QColor(160, 140, 120, 100), 1))
        painter.setFont(QFont("Microsoft YaHei", 8))
        state_names = {"idle": "站立", "walk": "走路", "sit": "坐下",
                       "sleep": "睡觉", "happy": "开心"}
        painter.drawText(5, self.win_h - 8, state_names.get(self.state, ""))

    def _get_sprite(self):
        """Get current sprite based on facing direction."""
        return self.sprite if self.facing_right else self.sprite_flip

    def _draw_idle(self, painter, cx, cy, s):
        """Idle pose with breathing."""
        offset_y = self.breath * 0.5
        sprite = self._get_sprite()
        painter.save()
        painter.translate(cx - self.sprite_w//2, cy - self.sprite_h//2 + offset_y)
        painter.drawPixmap(0, 0, sprite)
        # Draw blink overlay
        if self.blinking:
            painter.setPen(QPen(QColor(30, 25, 20), 2))
            painter.setBrush(Qt.NoBrush)
            # Calculate eye position based on sprite dimensions
            if self.facing_right:
                painter.drawLine(int(self.sprite_w*0.53), int(self.sprite_h*0.32),
                                int(self.sprite_w*0.62), int(self.sprite_h*0.32))
            else:
                painter.drawLine(int(self.sprite_w*0.38), int(self.sprite_h*0.32),
                                int(self.sprite_w*0.47), int(self.sprite_h*0.32))
        painter.restore()

    def _draw_walk(self, painter, cx, cy, s):
        """Walking with bounce."""
        bounce = abs(math.sin(self.walk_phase)) * 4
        sprite = self._get_sprite()
        painter.save()
        painter.translate(cx - self.sprite_w//2, cy - self.sprite_h//2 - bounce)
        # Slight tilt while walking
        painter.rotate(math.sin(self.walk_phase) * 3)
        painter.drawPixmap(0, 0, sprite)
        painter.restore()

    def _draw_sit(self, painter, cx, cy, s):
        """Sitting - scale down and position lower."""
        sprite = self._get_sprite()
        painter.save()
        painter.translate(cx, cy + 15)
        painter.scale(0.8, 0.8)
        painter.translate(-self.sprite_w//2, -self.sprite_h//2)
        painter.drawPixmap(0, 0, sprite)
        painter.restore()

    def _draw_sleep(self, painter, cx, cy, s):
        """Sleeping - rotated and with Zzz."""
        sprite = self._get_sprite()
        painter.save()
        painter.translate(cx, cy + 30)
        painter.rotate(-90)
        painter.translate(-self.sprite_w//2, -self.sprite_h//2)
        painter.drawPixmap(0, 0, sprite)
        painter.restore()

        # Draw Zzz
        z_alpha = int(100 + 55 * math.sin(self.time_ms * 0.003))
        painter.setPen(QPen(QColor(100, 150, 255, z_alpha), 2))
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        offset = math.sin(self.time_ms * 0.005) * 5
        painter.drawText(int(cx + 20 + offset), int(cy - 10), "z")
        painter.drawText(int(cx + 30 + offset*0.7), int(cy - 25), "z")
        painter.setFont(QFont("Arial", 16, QFont.Bold))
        painter.drawText(int(cx + 38 + offset*0.4), int(cy - 42), "z")

    def _draw_happy(self, painter, cx, cy, s):
        """Happy jumping."""
        jump = abs(math.sin(self.time_ms * 0.008)) * 15
        sprite = self._get_sprite()
        painter.save()
        painter.translate(cx - self.sprite_w//2, cy - self.sprite_h//2 - jump)
        painter.rotate(math.sin(self.time_ms * 0.008) * 5)
        painter.drawPixmap(0, 0, sprite)

        # Hearts or sparkles
        alpha = int(100 + 55 * math.sin(self.time_ms * 0.01))
        painter.setPen(QPen(QColor(255, 100, 150, alpha), 2))
        painter.setFont(QFont("Arial", 14))
        hx = self.sprite_w + 5 if self.facing_right else -25
        painter.drawText(int(hx), int(10 + math.sin(self.time_ms*0.01)*5), "♥")
        painter.restore()

    # ---- Interaction ----
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_offset = event.pos()
        elif event.button() == Qt.RightButton:
            self.show_menu(event.pos())

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(self.mapToParent(event.pos() - self.drag_offset))
            self.pos_x = self.x()
            self.pos_y = self.y()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            self.pos_x = self.x()
            self.pos_y = self.y()
            if self.state not in ["walk"]:
                self.change_state("happy")

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.change_state("happy")

    def show_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #fff8f0;
                border: 2px solid #d2965a;
                border-radius: 10px;
                padding: 6px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 5px;
                font-size: 13px;
                color: #5a3e2b;
            }
            QMenu::item:selected {
                background-color: #f0e0c8;
            }
            QMenu::separator {
                height: 1px;
                background: #e8d5b8;
                margin: 4px 10px;
            }
        """)

        menu.addAction("🐾 去散步").triggered.connect(self.go_walk)
        menu.addSeparator()
        menu.addAction("🪑 坐下").triggered.connect(lambda: self.change_state("sit"))
        menu.addAction("😴 睡觉").triggered.connect(lambda: self.change_state("sleep"))
        menu.addAction("🎉 开心").triggered.connect(lambda: self.change_state("happy"))
        menu.addSeparator()
        menu.addAction("💡 关于").triggered.connect(self.show_about)
        menu.addAction("🚪 退出").triggered.connect(self.quit_pet)
        menu.exec_(self.mapToGlobal(pos))

    def show_about(self):
        QMessageBox.about(self, "关于 比格多栋",
            "🐕 比格多栋 v2.0\n\n"
            "一只可爱的桌面宠物！\n\n"
            "🖱️ 左键拖拽 = 移动位置\n"
            "🖱️ 双击 = 开心蹦跳\n"
            "🖱️ 右键 = 功能菜单\n\n"
            "会自己走路、坐下、睡觉、玩耍~")

    def quit_pet(self):
        self.timer.stop()
        QApplication.instance().quit()


# ============================================================
# MAIN
# ============================================================
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("比格多栋")

    # Icon
    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))

    pet = PetWindow()
    pet.show()

    # System tray
    if QSystemTrayIcon.isSystemTrayAvailable():
        tray_icon = QIcon(ICON_PATH) if os.path.exists(ICON_PATH) else QIcon()
        tray = QSystemTrayIcon(tray_icon, app)
        tray.setToolTip("比格多栋 - 桌面宠物")
        tray_menu = QMenu()
        tray_menu.addAction("🐾 显示").triggered.connect(pet.show)
        tray_menu.addAction("🙈 隐藏").triggered.connect(pet.hide)
        tray_menu.addAction("🚶 散步").triggered.connect(pet.go_walk)
        tray_menu.addSeparator()
        tray_menu.addAction("🚪 退出").triggered.connect(pet.quit_pet)
        tray.setContextMenu(tray_menu)
        tray.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
