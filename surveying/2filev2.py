import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QGridLayout,
    QVBoxLayout, QHBoxLayout, QHeaderView
)
from PyQt6.QtCore import Qt


class SurveyPointForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("فرم حرفه‌ای ورود اطلاعات نقاط نقشه‌برداری")
        self.setGeometry(100, 100, 800, 500)

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # بخش فرم
        form_layout = QGridLayout()

        self.id_input = QLineEdit()
        self.x_input = QLineEdit()
        self.y_input = QLineEdit()
        self.z_input = QLineEdit()
        self.desc_input = QLineEdit()

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

        # دکمه‌ها
        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add")
        self.clear_btn = QPushButton("Clear Form")
        self.delete_btn = QPushButton("Delete Row")

        self.add_btn.clicked.connect(self.add_record)
        self.clear_btn.clicked.connect(self.clear_form)
        self.delete_btn.clicked.connect(self.delete_record)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addWidget(self.delete_btn)
        radio_layout = QPushButton
        
        main_layout.addLayout(btn_layout)

        # جدول
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "X", "Y", "Z", "Code"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

    def add_record(self):
        point_id = self.id_input.text().strip()
        x = self.x_input.text().strip()
        y = self.y_input.text().strip()
        z = self.z_input.text().strip()
        desc = self.desc_input.text().strip()

        if not point_id or not x or not y or not z:
            QMessageBox.warning(self, "خطا", "لطفاً فیلدهای اصلی را کامل کنید.")
            return

        # بررسی عددی بودن مختصات
        try:
            float(x)
            float(y)
            float(z)
        except ValueError:
            QMessageBox.warning(self, "خطا", "مقادیر X, Y, Z باید عدد باشند.")
            return

        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(point_id))
        self.table.setItem(row, 1, QTableWidgetItem(x))
        self.table.setItem(row, 2, QTableWidgetItem(y))
        self.table.setItem(row, 3, QTableWidgetItem(z))
        self.table.setItem(row, 4, QTableWidgetItem(desc))

        self.clear_form()

    def clear_form(self):
        self.id_input.clear()
        self.x_input.clear()
        self.y_input.clear()
        self.z_input.clear()
        self.desc_input.clear()

    def delete_record(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "اطلاع", "یک ردیف را انتخاب کنید.")
            return

        for index in sorted(selected_rows, reverse=True):
            self.table.removeRow(index.row())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SurveyPointForm()
    window.show()
    sys.exit(app.exec())