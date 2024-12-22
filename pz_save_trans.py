import sys
import json
import sqlite3
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QAbstractItemView,
    QPushButton, QFileDialog, QCheckBox, QProgressBar, QMessageBox,
    QLineEdit, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt
import extract_map


class MigrationTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("僵尸毁灭工程存档迁移工具")

        self.initUI()
        self.setGeometry(100, 100, 400, 300)

    def initUI(self):
        layout = QVBoxLayout()

        old_path_layout = QHBoxLayout()
        self.input_old_path = QLineEdit()
        self.input_old_path.setPlaceholderText("旧存档路径")
        self.btn_select_old = QPushButton("旧存档选择")
        self.btn_select_old.clicked.connect(self.select_old_save_path)
        old_path_layout.addWidget(self.input_old_path)
        old_path_layout.addWidget(self.btn_select_old)
        layout.addLayout(old_path_layout)

        new_path_layout = QHBoxLayout()
        self.input_new_path = QLineEdit()
        self.input_new_path.setPlaceholderText("新存档路径")
        self.btn_select_new = QPushButton("新存档选择")
        self.btn_select_new.clicked.connect(self.select_new_save_path)
        new_path_layout.addWidget(self.input_new_path)
        new_path_layout.addWidget(self.btn_select_new)
        layout.addLayout(new_path_layout)

        # 基地, 角色迁移, 车辆选项
        checkbox_layout = QHBoxLayout()
        self.checkbox_migrate_map = QCheckBox("迁移基地")
        self.checkbox_migrate_players = QCheckBox("迁移角色")
        self.checkbox_migrate_players.stateChanged.connect(self.toggle_player_migration)

        self.checkbox_migrate_vehicles = QCheckBox("迁移车辆")
        checkbox_layout.addWidget(self.checkbox_migrate_map)
        checkbox_layout.addWidget(self.checkbox_migrate_players)
        checkbox_layout.addWidget(self.checkbox_migrate_vehicles)
        layout.addLayout(checkbox_layout)

        self.table_players = QTableWidget()
        self.table_players.setColumnCount(3)
        self.table_players.setHorizontalHeaderLabels(["选择", "角色名", "死亡"])
        self.table_players.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_players.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_players.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_players.setVisible(False)
        layout.addWidget(self.table_players)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        # 添加迁移按钮
        self.migrate_button = QPushButton("开始迁移")
        self.migrate_button.clicked.connect(self.startMigration)
        layout.addWidget(self.migrate_button)

        self.setLayout(layout)

    def select_old_save_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择旧存档目录")
        if path:
            self.old_save_path = Path(path)
            self.input_old_path.setText(path)

    def select_new_save_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择新存档目录")
        if path:
            self.new_save_path = Path(path)
            self.input_new_path.setText(path)

    def toggle_player_migration(self, state):
        if state:
            self.load_players()
            self.table_players.setVisible(True)
        else:
            self.table_players.setVisible(False)

    def update_input_path(self):
        # 更新输入的路径
        self.old_save_path= Path(self.input_old_path.text())
        self.new_save_path= Path(self.input_new_path.text())

    def load_players(self):
        self.update_input_path()
        players_db_path = self.old_save_path.joinpath("players.db")
        if not players_db_path.exists():
            QMessageBox.warning(self, "Warning", "旧存档未发现players.db文件.")
            return

        try:
            conn = sqlite3.connect(players_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, isDead FROM localPlayers")
            self.players_data = cursor.fetchall()
            conn.close()

            self.table_players.setRowCount(len(self.players_data))
            for row, (id, name, isDead) in enumerate(self.players_data):
                checkbox = QTableWidgetItem()
                checkbox.setCheckState(Qt.CheckState.Unchecked)
                self.table_players.setItem(row, 0, checkbox)
                self.table_players.setItem(row, 1, QTableWidgetItem(name))
                self.table_players.setItem(row, 2, QTableWidgetItem("Yes" if isDead else "No"))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"未能加载角色信息: {e}")

    def migrate_players(self):
        selected_ids = []
        for row in range(self.table_players.rowCount()):
            if self.table_players.item(row, 0).checkState() == Qt.CheckState.Checked:
                selected_ids.append(self.players_data[row][0])


        old_db_path = self.old_save_path.joinpath("players.db")
        new_db_path = self.new_save_path.joinpath("players.db")
        if not new_db_path.exists():
            QMessageBox.critical(self, "Error", "新存档路径未发现players.db文件.")
            return

        old_conn = sqlite3.connect(old_db_path)
        new_conn = sqlite3.connect(new_db_path)

        old_cursor = old_conn.cursor()
        new_cursor = new_conn.cursor()

        for player_id in selected_ids:
            old_cursor.execute("SELECT name, wx, wy, x, y, z, worldversion,\
                               data, isDead FROM localPlayers WHERE id = ?", (player_id,))
            player_data = old_cursor.fetchone()

            if player_data:
                new_cursor.execute("INSERT INTO localPlayers (name, wx, wy, x, y, z,\
                    worldversion, data, isDead) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", player_data)
        new_conn.commit()
        old_conn.close()
        new_conn.close()

    def load_vehicles(self):
        self.update_input_path()
        vehicles_db_path = self.old_save_path.joinpath("vehicles.db")
        if not vehicles_db_path.exists():
            QMessageBox.warning(self, "Warning", "旧存档未发现vehicles.db文件.")
            return
        try:
            conn = sqlite3.connect(vehicles_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, x, y FROM vehicles")
            self.vehicles_data = cursor.fetchall()
            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"未能加载车辆信息: {e}")

    def migrate_vehicles(self, config):
        filtered_ids = extract_map.filter_vehicles(config, self.vehicles_data)

        old_db_path = self.old_save_path.joinpath("vehicles.db")
        new_db_path = self.new_save_path.joinpath("vehicles.db")
        if not new_db_path.exists():
            QMessageBox.critical(self, "Error", "新存档路径未发现vehicles.db文件.")
            return

        old_conn = sqlite3.connect(old_db_path)
        new_conn = sqlite3.connect(new_db_path)

        old_cursor = old_conn.cursor()
        new_cursor = new_conn.cursor()

        for vehicle_id in filtered_ids:
            old_cursor.execute("SELECT wx, wy, x, y, worldversion,\
                               data FROM vehicles WHERE id = ?", (vehicle_id,))
            vehicle_data = old_cursor.fetchone()
            if vehicle_data:
                new_cursor.execute("INSERT INTO vehicles (wx, wy, x, y,\
                    worldversion, data) VALUES (?, ?, ?, ?, ?, ?)", vehicle_data)

        new_conn.commit()
        old_conn.close()
        new_conn.close()


    def startMigration(self):
        # 这里实现迁移过程的逻辑
        try:
            self.progress_bar.setValue(0)
            CWD = Path(__file__).parent.absolute()
            with open('config.json', 'r', encoding='utf-8') as file:
                CONFIG = json.load(file)

            self.update_input_path()

            if self.checkbox_migrate_map.isChecked():
                extract_map.trans_save(CONFIG, self.old_save_path, self.new_save_path)
            self.progress_bar.setValue(33)

            if self.checkbox_migrate_players.isChecked():
                self.migrate_players()
            self.progress_bar.setValue(66)

            if self.checkbox_migrate_vehicles.isChecked():
                self.load_vehicles()
                self.migrate_vehicles(CONFIG)
            self.progress_bar.setValue(100)
            QMessageBox.information(self, "Success", "迁移完成.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"出现错误: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 设置应用程序的语言
    app.setStyle('Fusion')

    # 创建并显示窗口
    window = MigrationTool()
    window.show()

    app.exec()
