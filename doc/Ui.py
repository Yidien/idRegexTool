import Analyse
import threading
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QStandardItemModel, QStandardItem, QGuiApplication
from PySide6.QtWidgets import QDialog, QStyleFactory, QFileDialog, \
    QLineEdit, QHBoxLayout, QVBoxLayout, QPushButton, QTreeView


class Ui(QDialog):
    def __init__(self, parent=None):
        super(Ui, self).__init__(parent)

        self.line_edit1 = QLineEdit("输入分析文件路径")
        self.button1 = QPushButton("...")
        self.button2 = QPushButton("分析")

        self.model = QStandardItemModel(self)
        self.model.setHorizontalHeaderLabels(['类型', '数量'])
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setColumnWidth(0, 500)
        self.tree.setColumnWidth(1, 500)

        self.line_edit2 = QLineEdit("输出文件路径")
        self.button3 = QPushButton("筛选")
        self.button4 = QPushButton("附加")

        self.init_base()
        self.setLayout(self.init_layout())
        self.init_slot()
        return

    def init_base(self):
        screen = QGuiApplication.primaryScreen().geometry()
        width = screen.width() * 0.6
        height = screen.height() * 0.6
        self.resize(width, height)
        return

    def init_layout(self):
        layout1 = QHBoxLayout()
        layout1.addWidget(self.line_edit1)
        layout1.addWidget(self.button1)
        layout1.addWidget(self.button2)

        self.tree.setStyle(QStyleFactory.create('windows'))

        layout3 = QHBoxLayout()
        layout3.addWidget(self.line_edit2)
        layout3.addWidget(self.button3)
        layout3.addWidget(self.button4)

        layout = QVBoxLayout()
        layout.addLayout(layout1)
        layout.addWidget(self.tree)
        layout.addLayout(layout3)
        return layout

    def get_file_path(self):
        path = QFileDialog.getOpenFileName()[0]
        path_list = path.split('.')
        self.line_edit1.setText(path)
        self.line_edit2.setText(path_list[0]+'_output'+('.'+path_list[1]) if path_list[1] else '')
        return

    def create_tree_item(self, _data):
        items = []
        if type(_data).__name__ == 'list':
            for value in sorted(_data, key=lambda x: x.account_id):
                item = QStandardItem(value.account_id)
                item.setData(value)
                item.setCheckable(True)
                item.setAutoTristate(True)
                items.append(item)
        if type(_data).__name__ == 'dict':
            for key, value in sorted(_data.items(), key=lambda x: int(x[0]) if x[0].isdigit() else x[0]):
                item = QStandardItem(str(key))
                item.setCheckable(True)
                item.setAutoTristate(True)
                item.appendRows(self.create_tree_item(value))
                items.append(item)
        return items

    def show_count(self, model_item, count):
        if type(model_item).__name__ == 'QStandardItemModel':
            for index in range(model_item.rowCount()):
                row = model_item.item(index).row()
                text = model_item.item(index).text()
                count_item = QStandardItem(str(count[text]['self']))
                model_item.setItem(row, 1, count_item)
                self.show_count(model_item.item(index), count[text])
        else:
            for index in range(model_item.rowCount()):
                row = model_item.child(index).row()
                text = model_item.child(index).text()
                count_item = QStandardItem(str(count[text]['self']))
                model_item.setChild(row, 1, count_item)
        return

    def set_button_enabled(self, flag):
        self.button1.setEnabled(flag)
        self.button2.setEnabled(flag)
        self.button3.setEnabled(flag)
        self.button4.setEnabled(flag)
        return

    def start_analyse(self):
        self.model.removeRows(0, self.model.rowCount())
        data, count = Analyse.analyse_account(self.line_edit1.text())
        for item in self.create_tree_item(data):
            self.model.appendRow(item)
        self.show_count(self.model, count)
        #time.sleep(1)
        self.set_button_enabled(True)
        return

    def check_parent_check_state(self, a):
        if not a: return
        a1 = sum([int(a.child(index).checkState()) for index in range(a.rowCount())])
        flag = Qt.PartiallyChecked
        if a1 == 0: flag = Qt.Unchecked
        if a1 == 2*a.rowCount(): flag = Qt.Checked
        a.setCheckState(flag)
        self.check_parent_check_state(a.parent())
        return

    def set_child_item_check_state(self, a, flag):
        for index in range(a.rowCount()):
            _item = a.child(index)
            _item.setCheckState(flag)
            self.set_child_item_check_state(_item, flag)
        # self.check_parent_check_state(a.parent())
        return

    def set_parent_item_check_state(self, a):
        if a.parent():
            a.parent().setCheckState(Qt.PartiallyChecked)
            self.set_parent_item_check_state(a.parent())
        return

    def check_state_changed_event(self, a):
        '''
        flag = a.checkState()
        if flag != Qt.PartiallyChecked:
            self.set_child_item_check_state(a, flag)
            return
        if a.parent():
            a.parent().setCheckState(Qt.PartiallyChecked)
        '''
        self.model.itemChanged.disconnect(self.check_state_changed_event)
        flag = a.checkState()
        self.set_child_item_check_state(a, flag)
        self.check_parent_check_state(a.parent())
        # self.set_parent_item_check_state(a)
        self.model.itemChanged.connect(self.check_state_changed_event)
        return

    def get_current_path_event(self):
        index = self.tree.currentIndex()
        item = self.model.itemFromIndex(index)
        print(item.data())
        return

    def sift_account(self):
        data = []
        for item_index in range(self.model.rowCount()):
            item = self.model.item(item_index)
            if item.checkState() != Qt.Unchecked:
                for child_index in range(item.rowCount()):
                    child = item.child(child_index)
                    if child.checkState() != Qt.Unchecked:
                        for acc_index in range(child.rowCount()):
                            account = child.child(acc_index)
                            if account.checkState() == Qt.Checked:
                                data.append(account.data())
        Analyse.output_file(data, self.line_edit1.text(), self.line_edit2.text())
        self.set_button_enabled(True)
        print('ok')
        return

    def attach_account(self):
        data = []
        for item_index in range(self.model.rowCount()):
            item = self.model.item(item_index)
            for child_index in range(item.rowCount()):
                child = item.child(child_index)
                for acc_index in range(child.rowCount()):
                    account = child.child(acc_index)
                    data.append(account.data())
        Analyse.output_file(data, self.line_edit1.text(), self.line_edit2.text())
        self.set_button_enabled(True)
        print('ok')
        return

    @Slot()
    def analyse_slot(self):
        self.set_button_enabled(False)
        threading.Thread(target=self.start_analyse).start()
        return

    @Slot()
    def sift_slot(self):
        self.set_button_enabled(False)
        threading.Thread(target=self.sift_account).start()
        return

    @Slot()
    def attach_slot(self):
        self.set_button_enabled(False)
        threading.Thread(target=self.attach_account).start()
        return

    def init_slot(self):
        self.button1.clicked.connect(self.get_file_path)
        self.button2.clicked.connect(self.analyse_slot)
        self.model.itemChanged.connect(self.check_state_changed_event)
        # self.tree.doubleClicked.connect(self.get_current_path_event)
        self.button3.clicked.connect(self.sift_slot)
        self.button4.clicked.connect(self.attach_slot)
        return
