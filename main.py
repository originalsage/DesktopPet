# main.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPixmap, QCursor, QPainter, QColor, QIcon
import os

def resource_path(relative_path):
    """获取资源文件的绝对路径，用于处理PyInstaller打包后的资源路径问题"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()
        self.is_transparent = False  # 标记是否处于穿透状态
        self.is_visible = True       # 标记窗口是否可见
        self.init_ui()
        self.init_pet_logic()
        self.create_tray_icon()
        
    def create_tray_icon(self):
        # 创建系统托盘图标和菜单
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("lls pet")
        
        # 设置托盘图标
        if os.path.exists(resource_path("img/lls.png")):
            tray_pixmap = QPixmap(resource_path("img/lls.png"))
            self.tray_icon.setIcon(QIcon(tray_pixmap))
        elif os.path.exists(resource_path("img/NodeCircle.png")):
            tray_pixmap = QPixmap(resource_path("img/NodeCircle.png"))
            tray_pixmap = self.change_pixmap_color(tray_pixmap, QColor(255, 192, 203))
            self.tray_icon.setIcon(QIcon(tray_pixmap))
        else:
            # 如果找不到托盘图标文件，使用默认的粉色圆形图标
            default_icon = QPixmap(64, 64)
            default_icon.fill(QColor(255, 192, 203))
            self.tray_icon.setIcon(QIcon(default_icon))
        
        # 创建托盘菜单
        self.tray_menu = QMenu()
        
        # 添加菜单项
        self.toggle_transparent_action = QAction("切换穿透状态", self)
        self.toggle_transparent_action.triggered.connect(self.toggle_transparent)
        self.tray_menu.addAction(self.toggle_transparent_action)
        
        self.toggle_visibility_action = QAction("隐藏桌宠", self)
        self.toggle_visibility_action.triggered.connect(self.toggle_visibility)
        self.tray_menu.addAction(self.toggle_visibility_action)
        
        quit_action = QAction("退出程序", self)
        quit_action.triggered.connect(self.quit_application)
        self.tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()
        
    def toggle_transparent(self):
        """切换穿透状态"""
        self.is_transparent = not self.is_transparent
        
        if self.is_transparent:
            self.setWindowFlags(
                Qt.FramelessWindowHint |
                Qt.WindowStaysOnTopHint |
                Qt.Tool |
                Qt.WindowTransparentForInput  # 窗口穿透，鼠标事件穿透到下层窗口
            )
            self.toggle_transparent_action.setText("取消穿透状态")
        else:
            self.setWindowFlags(
                Qt.FramelessWindowHint |
                Qt.WindowStaysOnTopHint |
                Qt.Tool
            )
            self.toggle_transparent_action.setText("切换穿透状态")
            
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 只有在窗口应该是可见的时候才显示
        if self.is_visible:
            self.show()  # 重新显示窗口以应用新属性
        
    def toggle_visibility(self):
        """切换桌宠可见性"""
        if self.is_visible:
            self.hide()
            self.is_visible = False
            self.toggle_visibility_action.setText("显示桌宠")
        else:
            self.show()
            self.is_visible = True
            self.toggle_visibility_action.setText("隐藏桌宠")
            
    def quit_application(self):
        """退出应用程序"""
        # 先隐藏托盘图标，然后再退出应用
        self.tray_icon.hide()
        QApplication.quit()
        sys.exit(0)  # 确保程序完全退出
        
    def keyPressEvent(self, event):
        # 按V键切换为穿透状态
        if event.key() == Qt.Key_V:
            self.toggle_transparent()
            event.accept()
        else:
            super().keyPressEvent(event)
        
    def init_ui(self):
        # 设置窗口属性
        self.setWindowFlags(
            Qt.FramelessWindowHint |      # 无边框
            Qt.WindowStaysOnTopHint |     # 置顶显示
            Qt.Tool                       # 隐藏任务栏图标
        )
        self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景
        
        # 创建标签用于显示图片
        self.pet_container = QLabel(self)
        self.node_halo = QLabel(self.pet_container)
        self.node_circle = QLabel(self.pet_container)
            
        if os.path.exists(resource_path("img/NodeHalo.png")):
            self.halo_pixmap = QPixmap(resource_path("img/NodeHalo.png"))
            self.halo_pixmap = self.change_pixmap_color(self.halo_pixmap, QColor(255, 192, 203))  # 粉色
        else:
            # 如果找不到光环图片，则创建一个默认的占位图片
            self.halo_pixmap = QPixmap(100, 100)
            self.halo_pixmap.fill(Qt.transparent)

        if os.path.exists(resource_path("img/NodeCircle.png")):
            self.circle_pixmap = QPixmap(resource_path("img/NodeCircle.png"))
            # 将图片颜色修改为粉色
            self.circle_pixmap = self.change_pixmap_color(self.circle_pixmap, QColor(255, 192, 203))  # 粉色
        else:
            # 如果找不到主体图片，则创建一个默认的占位图片
            self.circle_pixmap = QPixmap(100, 100)
            self.circle_pixmap.fill(QColor(255, 192, 203))
            
        self.node_halo.setPixmap(self.halo_pixmap)
        self.node_circle.setPixmap(self.circle_pixmap)
        
        # 设置图片层级和位置
        self.node_halo.setGeometry(0, 0, self.halo_pixmap.width(), self.halo_pixmap.height())
        self.node_circle.setGeometry(0, 0, self.circle_pixmap.width(), self.circle_pixmap.height())
        self.node_circle.raise_()  # 主体图片置于顶层
        
        # 设置窗口大小
        width = max(self.halo_pixmap.width(), self.circle_pixmap.width())
        height = max(self.halo_pixmap.height(), self.circle_pixmap.height())
        self.setFixedSize(width, height)
        self.pet_container.resize(width, height)

    def change_pixmap_color(self, pixmap, color):
        """修改图片颜色为指定颜色"""
        if pixmap.isNull():
            return pixmap
        
        # 创建一个副本
        colored_pixmap = QPixmap(pixmap.size())
        colored_pixmap.fill(Qt.transparent)
        
        # 使用 QPainter 修改颜色
        painter = QPainter(colored_pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.drawPixmap(0, 0, pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(colored_pixmap.rect(), color)
        painter.end()
        
        return colored_pixmap
        
    def init_pet_logic(self):
        # 初始化位置，考虑图片中心
        self.pet_width = self.width()
        self.pet_height = self.height()
        self.pet_pos = QPoint(400 - self.pet_width//2, 300 - self.pet_height//2)
        self.move(self.pet_pos)
        
        # 设置定时器用于更新位置
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(10)  # 10ms更新一次
        
        # 移动速度
        self.speed = 1.0
        
        # 添加最小移动距离以防止卡住
        self.min_move_distance = 1

    def update_position(self):
        # 获取鼠标位置
        mouse_pos = QCursor.pos()
        
        # 计算图片中心位置
        center_offset_x = self.pet_width // 2
        center_offset_y = self.pet_height // 2
        pet_center_x = self.pet_pos.x() + center_offset_x
        pet_center_y = self.pet_pos.y() + center_offset_y
        
        # 计算向量差值（从图片中心到鼠标位置）
        delta_x = mouse_pos.x() - pet_center_x
        delta_y = mouse_pos.y() - pet_center_y
        distance = (delta_x ** 2 + delta_y ** 2) ** 0.5  # 使用欧几里得距离
        
        # 精确判断是否需要继续移动
        if distance > 2:  # 设置更合理的停止阈值
            # 动态速度：距离越远速度越快
            speed_factor = 0.006  # 增大速度系数
            dynamic_speed = max(0.5, self.speed + distance * speed_factor)
            # 使用浮点数计算避免精度损失
            move_ratio = min(dynamic_speed / max(distance, 1), 1.0)
            new_x = self.pet_pos.x() + delta_x * move_ratio  # 保持浮点数
            new_y = self.pet_pos.y() + delta_y * move_ratio  # 保持浮点数
            
            # 使用 round 而不是 int 来避免精度损失，并确保即使是很小的距离也能移动
            self.pet_pos = QPoint(round(new_x), round(new_y))
            self.move(self.pet_pos)

    def mousePressEvent(self, event):
        # 实现拖拽功能，保持中心对齐
        if event.button() == Qt.LeftButton:
            # 记录鼠标全局位置与窗口左上角的偏移量
            self.drag_position = event.globalPos() - self.pos()
            event.accept()
        # 添加右键菜单
        elif event.button() == Qt.RightButton:
            # 显示系统托盘菜单
            self.tray_menu.popup(QCursor.pos())
            event.accept()
            
    def mouseMoveEvent(self, event):
        # 拖拽移动
        if event.buttons() == Qt.LeftButton:
            new_pos = event.globalPos() - self.drag_position
            self.pet_pos = new_pos
            self.move(new_pos)
            event.accept()

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 隐藏窗口时不退出应用程序
    app.setApplicationName("lls pet")     # 设置应用程序名称为"lls pet"
    
    pet = DesktopPet()
    pet.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()