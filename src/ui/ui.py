from PySide6.QtWidgets import (
    QLabel, QMainWindow, QMenuBar, QMenu, QStackedWidget, QWidget,
    QButtonGroup, QRadioButton, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QMessageBox, QListWidget, QLineEdit, QGridLayout, QGroupBox
)
from PySide6.QtCore import Qt, QEasingCurve, QPropertyAnimation, Property
from PySide6.QtGui import QPainter, QColor, QBrush, QAction, QIcon, QPixmap

import qdarkstyle
from qdarkstyle.dark.palette import DarkPalette
from qdarkstyle.light.palette import LightPalette

from matrix.MatrixOperations import determinant, gauss_jordan_elimination, inverse


def resource_path(relative_path):
    import os, sys
    try:
        base_path = sys._MEIPASS  
    except Exception:
        base_path = os.path.abspath(".")  

    return os.path.join(base_path, relative_path)



class PulseButton(QPushButton):
    def __init__(self, text, on_click_callback=None):
        super().__init__(text)
        self.setFixedSize(150, 100)
        self.connected = False
        self._pulse_radius = 0
        self._pulse_color = "#2ecc71"
        self.on_click_callback = on_click_callback
        self.anim = QPropertyAnimation(self, b"pulseRadius")
        self.anim.setStartValue(0)
        self.anim.setEndValue(100)
        self.anim.setDuration(1000)
        self.anim.setLoopCount(-1)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.updateStyle()
        self.clicked.connect(self.toggle_and_calculate)

    def updateStyle(self):
        if self.connected:
            self.setText("SOLVING")
            self.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    font-size: 20px;
                    font-weight: bold;
                    border-radius: 40px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            self._pulse_color = "#e74c3c"
            self.anim.start()
        else:
            self.setText("SOLVE👨‍🔬")
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2ecc71;
                    color: white;
                    font-size: 20px;
                    font-weight: bold;
                    border-radius: 40px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                }
            """)
            self._pulse_color = "#2ecc71"
            self.anim.stop()
            self._pulse_radius = 0
            self.update()

    def toggle_and_calculate(self):
        self.connected = True
        self.updateStyle()
        if self.on_click_callback:
            self.on_click_callback()
        self.connected = False
        self.updateStyle()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.connected:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            center = self.rect().center()
            opacity = max(0.0, 1.0 - self._pulse_radius / 100)
            color = QColor(self._pulse_color)
            color.setAlphaF(opacity * 0.7)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center, self._pulse_radius, self._pulse_radius)

    def getPulseRadius(self): return self._pulse_radius
    def setPulseRadius(self, value): self._pulse_radius = value; self.update()
    pulseRadius = Property(int, getPulseRadius, setPulseRadius)

class MathWindow(QWidget):
    input_history = []

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.input_mode = 'text'
        self.grid_size = (2, 2)

        main_layout = QHBoxLayout(self)
        
       
        
        
        

        self.list_widget = QListWidget(self)
        self.list_widget.itemClicked.connect(self._select_history)
        self.list_widget.setFixedWidth(200)
        main_layout.addWidget(self.list_widget)

        self.right_layout = QVBoxLayout()
        main_layout.addLayout(self.right_layout)

        layout_mode = QHBoxLayout(self)
        self.right_layout.addLayout(layout_mode)
        
        btn_text = QPushButton("text")
        btn_text.clicked.connect(lambda: self.switch_input_mode("text"))
        layout_mode.addWidget(btn_text)
        
        
        btn_grid = QPushButton("grid")
        btn_grid.clicked.connect(lambda: self.switch_input_mode("grid"))

        layout_mode.addWidget(btn_grid)

        self.radio_group = QButtonGroup(self)
        self.radio_solve = QRadioButton("Solve System (Gauss-Jordan)")
        self.radio_inverse = QRadioButton("Inverse")
        self.radio_det = QRadioButton("Determinant")
        self.radio_solve.setChecked(True)
        for rb in (self.radio_solve, self.radio_inverse, self.radio_det):
            self.radio_group.addButton(rb)
            self.right_layout.addWidget(rb)

        self.input_container = QWidget(self)
        self.input_layout = QVBoxLayout(self.input_container)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Enter matrix, e.g. \n [[1,2],[3,4]] or \nx+y=1\n2x+3y=5")
        self.input_text.setFixedHeight(100)
        self.input_layout.addWidget(self.input_text)

        self.grid_box = QGroupBox("Matrix Grid Input")
        self.grid_layout = QVBoxLayout(self.grid_box)
        self._build_grid_inputs()
        self.input_layout.addWidget(self.grid_box)

        self.right_layout.addWidget(self.input_container)

        self.solve_btn = PulseButton("Solve👨‍🔬", self.perform_calculation)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.solve_btn)
        btn_layout.addStretch()
        self.right_layout.addLayout(btn_layout)

        self.output_result = QTextEdit()
        self.output_result.setReadOnly(True)
        self.output_result.setFixedHeight(100)
        self.right_layout.addWidget(self.output_result)

        self.switch_input_mode('text')

    def _build_grid_inputs(self):
        self.grid_widget = QWidget(self)
        self.grid_layout_inner = QVBoxLayout(self.grid_widget)

        self.grid_grid = QGridLayout()
        self.grid_controls = QHBoxLayout()

        self.grid_layout_inner.addLayout(self.grid_grid)
        self.grid_layout_inner.addLayout(self.grid_controls)

        self.inputs = []
        rows, cols = self.grid_size

        for i in range(rows):
            row_widgets = []
            for j in range(cols):
                le = QLineEdit()
                le.setFixedWidth(50)
                self.grid_grid.addWidget(le, i, j)
                row_widgets.append(le)
            self.inputs.append(row_widgets)

        self.btn_add_col = QPushButton("+ Col")
        self.btn_add_col.clicked.connect(self._add_column)

        self.btn_remove_col = QPushButton("- Col")
        self.btn_remove_col.clicked.connect(self._remove_column)

        self.btn_add_row = QPushButton("+ Row")
        self.btn_add_row.clicked.connect(self._add_row)

        self.btn_remove_row = QPushButton("- Row")
        self.btn_remove_row.clicked.connect(self._remove_row)

        for btn in [self.btn_remove_col, self.btn_add_col, self.btn_remove_row, self.btn_add_row]:
            self.grid_controls.addWidget(btn)

        self.grid_box.setLayout(QVBoxLayout())
        self.grid_box.layout().addWidget(self.grid_widget)

    def _add_column(self):
        for i in range(len(self.inputs)):
            le = QLineEdit()
            le.setFixedWidth(50)
            self.inputs[i].append(le)
            self.grid_grid.addWidget(le, i, len(self.inputs[i]) - 1)
        self.grid_size = (len(self.inputs), len(self.inputs[0]))

    def _remove_column(self):
        if len(self.inputs[0]) <= 1:
            return
        col_index = len(self.inputs[0]) - 1
        for i in range(len(self.inputs)):
            le = self.inputs[i].pop()
            self.grid_grid.removeWidget(le)
            le.deleteLater()
        self.grid_size = (len(self.inputs), len(self.inputs[0]))

    def _add_row(self):
        cols = len(self.inputs[0])
        new_row = []
        row_index = len(self.inputs)
        for j in range(cols):
            le = QLineEdit()
            le.setFixedWidth(50)
            self.grid_grid.addWidget(le, row_index, j)
            new_row.append(le)
        self.inputs.append(new_row)
        self.grid_size = (len(self.inputs), cols)

    def _remove_row(self):
        if len(self.inputs) <= 1:
            return
        row_index = len(self.inputs) - 1
        for le in self.inputs.pop():
            self.grid_grid.removeWidget(le)
            le.deleteLater()
        self.grid_size = (len(self.inputs), len(self.inputs[0]))

    def switch_input_mode(self, mode):
        self.input_mode = mode
        self.input_text.setVisible(mode == 'text')
        self.grid_box.setVisible(mode == 'grid')

    def set_input_mode_from_settings(self, mode):
        self.switch_input_mode(mode)

    def _refresh_history(self):
        self.list_widget.clear()
        self.list_widget.addItems(self.input_history)

    def _add_history(self, matrix_repr, method):
        entry = f"{matrix_repr} || {method} || {self.input_mode}"
        self.input_history.append(entry)
        self._refresh_history()

    def _select_history(self, item):
        import ast
        try:
            matrix_repr, method, mode = item.text().split(' || ')
        except Exception as e:
            self.output_result.setText(f"Error loading history: {e}")
            return

        self.switch_input_mode(mode)

        if mode == 'text':
            self.input_text.setText(matrix_repr)
        else:
            try:
                matrix = ast.literal_eval(matrix_repr)
            except Exception as e:
                self.output_result.setText(f"Error parsing matrix from history: {e}")
                return

            rows, cols = len(matrix), len(matrix[0])
            self._rebuild_grid(rows, cols)
            for i in range(rows):
                for j in range(cols):
                    self.inputs[i][j].setText(str(matrix[i][j]))

        for rb in (self.radio_solve, self.radio_inverse, self.radio_det):
            if rb.text() == method:
                rb.setChecked(True)

    def _rebuild_grid(self, rows, cols):
        for i in reversed(range(self.grid_grid.count())):
            widget = self.grid_grid.itemAt(i).widget()
            if widget:
                self.grid_grid.removeWidget(widget)
                widget.deleteLater()

        self.inputs = []
        for i in range(rows):
            row_widgets = []
            for j in range(cols):
                le = QLineEdit()
                le.setFixedWidth(50)
                self.grid_grid.addWidget(le, i, j)
                row_widgets.append(le)
            self.inputs.append(row_widgets)

        self.grid_size = (rows, cols)

    def perform_calculation(self):
        try:
            if self.input_mode == 'text':
                text = self.input_text.toPlainText().strip()
                matrix_repr = text
                if ("+" in text or "=" in text or "-" in text) and self.radio_solve.isChecked():
                    matrix = text
                else:
                    import ast
                    matrix = ast.literal_eval(text)
            else:
                matrix = [
                    [float(self.inputs[i][j].text() or 0) for j in range(len(self.inputs[0]))]
                    for i in range(len(self.inputs))
                ]
                matrix_repr = str(matrix)

            method = self.radio_group.checkedButton().text()
            self._add_history(matrix_repr, method)

            if self.radio_solve.isChecked():
                result = gauss_jordan_elimination(matrix)
            elif self.radio_inverse.isChecked():
                result = inverse(matrix)
                if result is None:
                    raise ValueError("Matrix is singular")
            else:
                result = determinant(matrix)

            self.output_result.setText(str(result))
        except Exception as e:
            self.output_result.setText(f"Error: {e}")

class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(resource_path("src\\ui\\favicon.ico")).scaled(30, 30))
        self.title = QLabel("Ⓜ️🅰️TH👨‍🔬🅰️🅰️🅿️")
        self.title.setStyleSheet("margin-left:10px; font-weight:bold; font-size:16px;")
        self.btn_min = QPushButton("➖")
        self.btn_close = QPushButton("✖️")
        for btn in (self.btn_min, self.btn_close):
            btn.setFixedSize(30, 30)
        self.btn_min.clicked.connect(lambda: parent.showMinimized())
        self.btn_close.clicked.connect(parent.close)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(icon_label)
        layout.addWidget(self.title)
        layout.addStretch()
        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_close)
        self._start_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._start_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self._start_pos:
            delta = event.globalPosition().toPoint() - self._start_pos
            self.window().move(self.window().pos() + delta)
            self._start_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._start_pos = None


class SettingWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent
        layout = QVBoxLayout(self)

        btn_back = QPushButton("Back")
        btn_back.clicked.connect(self.back_to_proxy)
        layout.addWidget(btn_back)

        layout.addWidget(QLabel("Theme:"))
        theme_group = QButtonGroup(self)
        btn_dark = QRadioButton("Dark"); btn_dark.setChecked(True)
        btn_light = QRadioButton("Light")
        for b in (btn_dark, btn_light):
            theme_group.addButton(b)
            layout.addWidget(b)
        theme_group.buttonClicked.connect(lambda b: self._change_theme(b.text().lower()))

        layout.addWidget(QLabel("Input Mode:"))
        self.input_group = QButtonGroup(self)
        btn_text = QRadioButton("Text"); btn_text.setChecked(True)
        btn_grid = QRadioButton("Grid")
        for b in (btn_text, btn_grid):
            self.input_group.addButton(b)
            layout.addWidget(b)
        self.input_group.buttonClicked.connect(lambda b: self._change_input(b.text().lower()))

    def _change_theme(self, mode):
        pal = LightPalette() if mode == 'light' else DarkPalette()
        self._parent.app.setStyleSheet(qdarkstyle.load_stylesheet(palette=pal))

    def _change_input(self, mode):
        self._parent.proxyWidget.set_input_mode_from_settings(mode)

    def back_to_proxy(self):
        self._parent.stack.setCurrentIndex(0)
        
        
        
class Window(QMainWindow):
    def __init__(self, app):
        super().__init__(); self.app = app
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.resize(800, 600)



        main = QWidget(self)
        self.setCentralWidget(main)
        layout = QVBoxLayout(main)

        self.title_bar = CustomTitleBar(self)
        layout.addWidget(self.title_bar)

        menuBar = QMenuBar(self)
        fileMenu = QMenu("&File", self)
        exitA = QAction("E&xit", self); exitA.setShortcut("Ctrl+Q"); exitA.triggered.connect(self.close)
        fileMenu.addAction(exitA); menuBar.addMenu(fileMenu)
        viewMenu = QMenu("&View", self)
        appA = QAction("&Appearance", self); appA.setShortcut("Ctrl+E")
        appA.triggered.connect(lambda: self.stack.setCurrentIndex(1))
        viewMenu.addAction(appA); menuBar.addMenu(viewMenu)
        helpMenu = QMenu("&Help", self)
        aboutA = QAction("&About", self)
        aboutA.triggered.connect(lambda: QMessageBox.information(self, "About", "Matrix Solver App\nBy NimaSalamat"))
        helpMenu.addAction(aboutA); menuBar.addMenu(helpMenu)

        layout.addWidget(menuBar)


        self.stack = QStackedWidget(self)
        self.proxyWidget = MathWindow(self)
        self.settingWidget = SettingWindow(self)
        self.stack.addWidget(self.proxyWidget)
        self.stack.addWidget(self.settingWidget)
        layout.addWidget(self.stack)
