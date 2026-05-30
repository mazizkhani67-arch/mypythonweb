import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QGridLayout,
    QVBoxLayout, QHBoxLayout, QHeaderView, QRadioButton, QGroupBox,
    QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class SmartLineEdit(QLineEdit):
    enterPressed = pyqtSignal()
    focusLost = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.enterPressed.emit()
            return
        super().keyPressEvent(event)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.focusLost.emit()


class SurveyPointForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("فرم حرفه‌ای ورود اطلاعات نقاط نقشه‌برداری")
        self.setGeometry(100, 100, 1100, 800)

        self.auto_counter = 1
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # ------------------- Form fields -------------------
        form_layout = QGridLayout()

        self.id_input = QLineEdit()
        self.x_input = SmartLineEdit()
        self.y_input = SmartLineEdit()
        self.z_input = SmartLineEdit()
        self.desc_input = SmartLineEdit()

        form_layout.addWidget(QLabel("Point ID:"), 0, 0)
        form_layout.addWidget(self.id_input, 0, 1)

        form_layout.addWidget(QLabel("X:"), 1, 0)
        form_layout.addWidget(self.x_input, 1, 1)

        form_layout.addWidget(QLabel("Y:"), 2, 0)
        form_layout.addWidget(self.y_input, 2, 1)

        form_layout.addWidget(QLabel("Z:"), 3, 0)
        form_layout.addWidget(self.z_input, 3, 1)

        form_layout.addWidget(QLabel("Description:"), 4, 0)
        form_layout.addWidget(self.desc_input, 4, 1)

        main_layout.addLayout(form_layout)

        # ------------------- Auto numbering -------------------
        auto_group = QGroupBox("تنظیمات شماره‌گذاری")
        auto_layout = QGridLayout()

        self.auto_off = QRadioButton("شماره‌گذاری دستی")
        self.auto_on = QRadioButton("شماره‌گذاری خودکار")
        self.auto_off.setChecked(True)

        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("مثلاً 1 یا 1000")
        self.start_input.setEnabled(False)

        auto_layout.addWidget(self.auto_off, 0, 0)
        auto_layout.addWidget(self.auto_on, 0, 1)
        auto_layout.addWidget(QLabel("شروع شماره‌گذاری از:"), 1, 0)
        auto_layout.addWidget(self.start_input, 1, 1)

        auto_group.setLayout(auto_layout)
        main_layout.addWidget(auto_group)

        # ------------------- Point type -------------------
        code_group = QGroupBox("نوع نقطه")
        code_layout = QHBoxLayout()

        self.code_normal = QRadioButton("Point")
        self.code_bench = QRadioButton("BenchMark")
        self.code_boundary = QRadioButton("Boundary")
        self.code_normal.setChecked(True)

        code_layout.addWidget(self.code_normal)
        code_layout.addWidget(self.code_bench)
        code_layout.addWidget(self.code_boundary)

        code_group.setLayout(code_layout)
        main_layout.addWidget(code_group)

        # ------------------- Options -------------------
        options_layout = QHBoxLayout()
        self.save_on_exit_checkbox = QCheckBox("ذخیره هنگام خروج از Description")
        self.save_on_exit_checkbox.setChecked(False)
        options_layout.addWidget(self.save_on_exit_checkbox)
        options_layout.addStretch()
        main_layout.addLayout(options_layout)

        # ------------------- Buttons -------------------
        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add")
        self.clear_btn = QPushButton("Clear Form")
        self.delete_btn = QPushButton("Delete Row")
        self.plot_btn = QPushButton("Show Scatter Plot")

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.plot_btn)

        main_layout.addLayout(btn_layout)

        # ------------------- Table -------------------
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "X", "Y", "Z", "Code - Description"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.table)

        # ------------------- Plot canvas -------------------
        self.figure = plt.Figure(figsize=(7, 4))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setVisible(False)
        main_layout.addWidget(self.canvas)

        self.setLayout(main_layout)

        # ------------------- Connections -------------------
        self.auto_off.toggled.connect(self.toggle_auto_id)
        self.auto_on.toggled.connect(self.toggle_auto_id)
        self.start_input.textChanged.connect(self.update_start_number)

        self.add_btn.clicked.connect(self.add_record)
        self.clear_btn.clicked.connect(self.clear_form)
        self.delete_btn.clicked.connect(self.delete_record)
        self.plot_btn.clicked.connect(self.show_scatter_plot)

        self.x_input.enterPressed.connect(lambda: self.y_input.setFocus())
        self.y_input.enterPressed.connect(lambda: self.z_input.setFocus())
        self.z_input.enterPressed.connect(lambda: self.desc_input.setFocus())
        self.desc_input.enterPressed.connect(self.ask_save_record)

        self.desc_input.focusLost.connect(self.on_desc_focus_lost)

        self.toggle_auto_id()

    def toggle_auto_id(self):
        if self.auto_on.isChecked():
            self.id_input.setDisabled(True)
            self.start_input.setEnabled(True)
        else:
            self.id_input.setEnabled(True)
            self.start_input.setEnabled(False)

    def update_start_number(self):
        text = self.start_input.text().strip()
        if not text:
            return
        try:
            self.auto_counter = int(text)
        except ValueError:
            QMessageBox.warning(self, "خطا", "شماره شروع باید عددی باشد.")
            self.start_input.clear()
            self.auto_counter = 1

    def ask_save_record(self):
        reply = QMessageBox.question(
            self,
            "ذخیره رکورد",
            "فیلد پاک شود و ذخیره شود؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.add_record():
                self.clear_form()
                if self.auto_on.isChecked():
                    self.x_input.setFocus()
                else:
                    self.id_input.setFocus()

    def on_desc_focus_lost(self):
        if self.save_on_exit_checkbox.isChecked():
            if self.desc_input.text().strip() or self.x_input.text().strip() or self.y_input.text().strip():
                self.ask_save_record()

    def add_record(self):
        if self.auto_on.isChecked():
            point_id = str(self.auto_counter)
        else:
            point_id = self.id_input.text().strip()

        x_text = self.x_input.text().strip()
        y_text = self.y_input.text().strip()

        z_text = self.z_input.text().strip()
        if not z_text:
            z_text = "0"

        desc = self.desc_input.text().strip()

        if self.code_bench.isChecked():
            code_value = "BenchMark"
        elif self.code_boundary.isChecked():
            code_value = "Boundary"
        else:
            code_value = "Point"

        if not point_id or not x_text or not y_text:
            QMessageBox.warning(self, "خطا", "لطفاً فیلدهای ID، X و Y را پر کنید.")
            return False

        try:
            float(x_text)
            float(y_text)
            float(z_text)
        except ValueError:
            QMessageBox.warning(self, "خطا", "مقادیر X, Y, Z باید عدد باشند.")
            return False

        row = self.table.rowCount()
        self.table.insertRow(row)

        code_desc = code_value if not desc else f"{code_value} - {desc}"
        values = [point_id, x_text, y_text, z_text, code_desc]

        for i, val in enumerate(values):
            self.table.setItem(row, i, QTableWidgetItem(val))

        if self.auto_on.isChecked():
            self.auto_counter += 1
            self.start_input.setText(str(self.auto_counter))

        self.clear_form()
        return True

    def clear_form(self):
        if not self.auto_on.isChecked():
            self.id_input.clear()
        self.x_input.clear()
        self.y_input.clear()
        self.z_input.clear()
        self.desc_input.clear()

    def delete_record(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "اطلاع", "ابتدا یک ردیف را انتخاب کنید.")
            return

        for index in sorted(selected_rows, key=lambda x: x.row(), reverse=True):
            self.table.removeRow(index.row())

        if self.auto_on.isChecked():
            max_id = 0
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 0)
                if item:
                    try:
                        pid = int(item.text())
                        max_id = max(max_id, pid)
                    except ValueError:
                        pass
            self.auto_counter = max_id + 1 if max_id > 0 else 1
            self.start_input.setText(str(self.auto_counter))

    def show_scatter_plot(self):
        rows = self.table.rowCount()
        if rows == 0:
            QMessageBox.information(self, "اطلاع", "جدول خالی است. ابتدا چند نقطه وارد کنید.")
            return

        x_coords = []
        y_coords = []
        labels = []

        for row in range(rows):
            x_item = self.table.item(row, 1)
            y_item = self.table.item(row, 2)
            id_item = self.table.item(row, 0)

            if x_item and y_item and id_item:
                try:
                    x_coords.append(float(x_item.text()))
                    y_coords.append(float(y_item.text()))
                    labels.append(id_item.text())
                except ValueError:
                    continue

        if not x_coords:
            QMessageBox.warning(self, "خطا", "داده معتبر برای رسم نمودار پیدا نشد.")
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.scatter(x_coords, y_coords, color='blue', marker='o')

        for x, y, label in zip(x_coords, y_coords, labels):
            ax.annotate(label, (x, y), textcoords="offset points", xytext=(5, 5), fontsize=8)

        ax.set_title("Scatter Plot of Survey Points")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.grid(True)

        self.canvas.setVisible(True)
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SurveyPointForm()
    win.show()
    sys.exit(app.exec())
