from PyQt5.QtWidgets import QMainWindow, QMessageBox, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QPalette, QBrush, QPixmap, QRadialGradient
from PyQt5.QtCore import Qt, QPoint, QTimer
import traceback
from game import Gomoku
from corner_widget import CornerWidget


def run_with_exc(f):
    """游戏运行出现错误时，用messagebox把错误信息显示出来"""

    def call(window, *args, **kwargs):
        try:
            return f(window, *args, **kwargs)
        except Exception:
            exc_info = traceback.format_exc()
            QMessageBox.about(window, '错误信息', exc_info)
    return call


class GomokuWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.board_size = 3
        self.grid_size = 150
        self.margin = 150
        self.win_size = self.margin * 2 + self.grid_size * (self.board_size - 1)
        
        self.bg_img = QPixmap('imgs/muzm.jpg')
        self.piece1_img = None
        self.piece2_img = None
        
        self.g = Gomoku(mode='PVE', board_size=self.board_size)  # 初始化游戏内容
        self.init_ui()  # 初始化游戏界面

        self.last_pos = (-1, -1)
        self.res = 0  # 记录那边获得了胜利
        self.operate_status = 0  # 游戏操作状态。0为游戏中（可操作），1为游戏结束闪烁过程中（不可操作）

    def init_ui(self):
        """初始化游戏界面"""
        self.setObjectName('MainWindow')
        self.setWindowTitle('简单三子棋 (Simple Three-in-a-Row)')
        self.setFixedSize(self.win_size, self.win_size + 50)
        
        self.update_palette()
        
        # 按钮容器
        self.btn_widget = QWidget(self)
        self.btn_widget.setGeometry(0, self.win_size, self.win_size, 50)
        layout = QHBoxLayout(self.btn_widget)
        
        self.btn_mode = QPushButton('模式: 人机', self)
        self.btn_mode.clicked.connect(self.switch_mode)
        layout.addWidget(self.btn_mode)
        
        self.btn_bg = QPushButton('背景图', self)
        self.btn_bg.clicked.connect(self.load_bg)
        layout.addWidget(self.btn_bg)
        
        self.btn_p1 = QPushButton('棋子1图', self)
        self.btn_p1.clicked.connect(lambda: self.load_piece_img(1))
        layout.addWidget(self.btn_p1)
        
        self.btn_p2 = QPushButton('棋子2图', self)
        self.btn_p2.clicked.connect(lambda: self.load_piece_img(2))
        layout.addWidget(self.btn_p2)

        self.setMouseTracking(True)
        self.corner_widget = CornerWidget(self)
        self.corner_widget.repaint()
        self.corner_widget.hide()
        
        self.end_timer = QTimer(self)
        self.end_timer.timeout.connect(self.end_flash)
        self.flash_cnt = 0
        self.flash_pieces = ((-1, -1), )
        self.show()

    def update_palette(self):
        palette = QPalette()
        if self.bg_img:
            palette.setBrush(QPalette.Window, QBrush(self.bg_img.scaled(self.win_size, self.win_size + 50, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
        self.setPalette(palette)

    def switch_mode(self):
        if self.g.mode == 'PVE':
            self.g.mode = 'PVP'
            self.btn_mode.setText('模式: 双人')
        else:
            self.g.mode = 'PVE'
            self.btn_mode.setText('模式: 人机')
        self.restart_game_completely()

    def load_bg(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择背景图片", "", "Images (*.png *.xpm *.jpg)")
        if path:
            self.bg_img = QPixmap(path)
            self.update_palette()

    def load_piece_img(self, player):
        path, _ = QFileDialog.getOpenFileName(self, f"选择棋子{player}图片", "", "Images (*.png *.xpm *.jpg)")
        if path:
            img = QPixmap(path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            if player == 1:
                self.piece1_img = img
            else:
                self.piece2_img = img
            self.update()

    def restart_game_completely(self):
        self.g = Gomoku(mode=self.g.mode, board_size=self.board_size)
        self.res = 0
        self.operate_status = 0
        self.flash_cnt = 0
        self.update()

    @run_with_exc
    def paintEvent(self, e):
        """绘制游戏内容"""
        qp = QPainter()
        qp.begin(self)
        
        # 绘制棋盘
        qp.setPen(QPen(QColor(0, 0, 0), 2, Qt.SolidLine))
        for i in range(self.board_size):
            # 横线
            qp.drawLine(self.margin, self.margin + i * self.grid_size, self.margin + (self.board_size - 1) * self.grid_size, self.margin + i * self.grid_size)
            # 竖线
            qp.drawLine(self.margin + i * self.grid_size, self.margin, self.margin + i * self.grid_size, self.margin + (self.board_size - 1) * self.grid_size)

        # 绘制选中状态
        if self.g.selected_piece:
            sx, sy = self.g.selected_piece
            qp.setPen(QPen(QColor(255, 0, 0), 3, Qt.DashLine))
            qp.drawRect(self.margin + sx * self.grid_size - 35, self.margin + sy * self.grid_size - 35, 70, 70)

        # 绘制棋子
        for x in range(self.board_size):
            for y in range(self.board_size):
                val = self.g.g_map[x][y]
                if val == 0: continue
                
                if self.flash_cnt % 2 == 1 and (x, y) in self.flash_pieces:
                    continue

                pos = QPoint(self.margin + x * self.grid_size, self.margin + y * self.grid_size)
                
                if val == 1:
                    if self.piece1_img:
                        qp.drawPixmap(pos.x() - 30, pos.y() - 30, self.piece1_img)
                    else:
                        radial = QRadialGradient(pos.x(), pos.y(), 30, pos.x() - 10, pos.y() - 10)
                        radial.setColorAt(0, QColor(96, 96, 96))
                        radial.setColorAt(1, QColor(0, 0, 0))
                        qp.setBrush(QBrush(radial))
                        qp.setPen(Qt.NoPen)
                        qp.drawEllipse(pos, 30, 30)
                elif val == 2:
                    if self.piece2_img:
                        qp.drawPixmap(pos.x() - 30, pos.y() - 30, self.piece2_img)
                    else:
                        radial = QRadialGradient(pos.x(), pos.y(), 30, pos.x() - 10, pos.y() - 10)
                        radial.setColorAt(0, QColor(255, 255, 255))
                        radial.setColorAt(1, QColor(160, 160, 160))
                        qp.setBrush(QBrush(radial))
                        qp.setPen(Qt.NoPen)
                        qp.drawEllipse(pos, 30, 30)
        
        qp.end()

    @run_with_exc
    def mouseMoveEvent(self, e):
        mouse_x = e.windowPos().x()
        mouse_y = e.windowPos().y()
        
        game_x, game_y = -1, -1
        for x in range(self.board_size):
            for y in range(self.board_size):
                px = self.margin + x * self.grid_size
                py = self.margin + y * self.grid_size
                if abs(mouse_x - px) < 30 and abs(mouse_y - py) < 30:
                    game_x, game_y = x, y
                    break
        
        pos_change = (game_x != self.last_pos[0] or game_y != self.last_pos[1])
        self.last_pos = (game_x, game_y)
        
        if pos_change:
            if game_x != -1:
                self.setCursor(Qt.PointingHandCursor)
                self.corner_widget.move(self.margin + game_x * self.grid_size - 15, self.margin + game_y * self.grid_size - 15)
                self.corner_widget.show()
            else:
                self.setCursor(Qt.ArrowCursor)
                self.corner_widget.hide()

    @run_with_exc
    def mousePressEvent(self, e):
        if not (hasattr(self, 'operate_status') and self.operate_status == 0):
            return
        if e.button() == Qt.LeftButton:
            mouse_x = e.windowPos().x()
            mouse_y = e.windowPos().y()
            
            game_x, game_y = -1, -1
            for x in range(self.board_size):
                for y in range(self.board_size):
                    px = self.margin + x * self.grid_size
                    py = self.margin + y * self.grid_size
                    if abs(mouse_x - px) < 30 and abs(mouse_y - py) < 30:
                        game_x, game_y = x, y
                        break
            
            if game_x == -1: return
            
            moved = self.g.move_1step(True, game_x, game_y)
            self.update()

            if not moved: return # 只是选中了棋子，还没有完成移动/放置

            # 检查结果
            res, self.flash_pieces = self.g.game_result(show=True)
            if res != 0:
                self.game_restart(res)
                return

            # 如果是人机模式，轮到 AI
            if self.g.mode == 'PVE' and self.g.cur_step % 2 == 1:
                self.g.ai_play_1step()
                res, self.flash_pieces = self.g.game_result(show=True)
                if res != 0:
                    self.game_restart(res)
                self.update()

    @run_with_exc
    def end_flash(self):
        if self.flash_cnt <= 5:
            self.flash_cnt += 1
            self.update()
        else:
            self.end_timer.stop()
            msg = "玩家1获胜!" if self.res == 1 else ("玩家2获胜!" if self.res == 2 else "平局!")
            QMessageBox.about(self, '游戏结束', msg)
            self.restart_game_completely()

    def game_restart(self, res):
        self.res = res
        self.operate_status = 1
        self.end_timer.start(300)
