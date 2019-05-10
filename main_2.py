# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 17:04:57 2018

@author: marcin
"""
import datetime
import json
import os
import re
import sys
import time
from subprocess import call

import dateutil.parser as dparser
import unidecode
from PyQt5 import QtCore, QtGui, QtWidgets
from pandas import read_csv, DataFrame

import edit_users
import login
import mainwindow
import message_box
import new_bill
import options
import report_mail
import summary
from billmodule import bill
from logmodule import log
from mailmodule import mail
from reportmodule import report

try:
    user_df = read_csv('users.csv', sep=';', index_col='ID', encoding='utf8')
except:
    user_df = DataFrame(columns=['User', 'PayID', 'Patterns', 'Mail'])

user_df.sort_values(by=['User'], inplace=True)
user_df.fillna('', inplace=True)


class App(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setupUi(self)

        self.menu_fields = [[self.menuPayments, self.actionImportuj_2, self.menuExportuj, self.actionTo_CSV,
                             self.actionTo_XLS, self.actionOpen_directory, self.actionCount_spectra,
                             self.actionRead_spectra, self.actionMatch_users, self.actionDelete_rows,
                             self.actionCreate_summary, self.actionShow_summary],
                            [self.menuMail, self.actionOpen_directory_2, self.actionMatch_users_2,
                             self.actionDelete_rows_2, self.actionSend_all, self.actionSend_selected],
                            [self.menuLogs, self.actionOpen_log_file], [],
                            [self.menuBills, self.actionNew_Bill, self.actionEdit_bill, self.actionDelete,
                             self.actionMark_as_archived, self.actionOpen_corresponding_report]]

        self.set_connections_main()
        self.set_connections_payments()
        self.set_connections_mail()
        self.set_connections_bills()
        self.set_connections_logs()
        self.set_connections_options()

        self.disable_menus()
        self.billtabSelChange()
        self.comboSelChange()
        self.tabSelChange()
        self.mainTabSelChange()

        self.bills = None
        self.found_files = 1
        self.sender = None
        self.start = None
        self.end = None

        self.stop_button.hide()

        self.set_tables_widths()
        self.activateTab(1)

        self.current_pixmap = QtGui.QPixmap('icons/if_Circle_Yellow_34215.ico')

        self.status_label = QtWidgets.QLabel()
        self.statusbar.addWidget(self.status_label)

        curr_date = QtCore.QDate.currentDate()
        self.dateEdit_2.setDate(curr_date)
        year = curr_date.year()
        begin_date = QtCore.QDate(year, 1, 1)
        self.dateEdit.setDate(begin_date)

        self.buttons_connections = [self.button_connect, self.button_login, self.button_logout]
        self.buttons_sending = [self.pushButton_2, self.pushButton_3, self.pushButton_5, self.pushButton_6,
                                self.actionSend_selected, self.actionSend_all]

        for item in [self.button_logout, self.button_login, self.pushButton_5,
                     self.pushButton_6, self.pushButton_4, self.actionLogin, self.actionClose_connection]:
            item.setEnabled(False)

        try:
            with open('data/params.txt', 'r') as input:
                self.params = json.load(input)
        except FileNotFoundError:
            self.params = {'server': '', 'port': 0, 'username': '', 'password': '', 'mail_from': '',
                           'mail_ans': '', 'mail_topic': '', 'mail_text': '', 'timeout': 30,
                           'main_dir': '', 'zip_dir': '', 'log_dir': '', 'price': '', 'spectra_dir': '',
                           'report_dir': '', 'notification_mails': ''}

        self.set_params()
        self.label_user.setText('')

        self.Combo_Zlec.addItems(['Zmieniacz', 'Zlecenia indywidualne', 'Spektrometr 300 MHz'])
        self.Combo_Zlec.setCurrentIndex(-1)

    def set_connections_main(self):
        self.actionPayments.triggered.connect(lambda: self.activateTab(0))
        self.actionSend_mail.triggered.connect(lambda: self.activateTab(1))
        self.actionLogs.triggered.connect(lambda: self.activateTab(2))
        self.pushButton_8.clicked.connect(lambda: self.activateTab(0))
        self.actionBills.triggered.connect(self.activate_bills)

    def set_connections_payments(self):
        self.chooseDir.clicked.connect(self.choose_dir)
        self.analyze_button.clicked.connect(self.analyze_files)
        self.find_button.clicked.connect(self.count_files)
        self.users_button.clicked.connect(self.analyze_users)

        self.del_button.clicked.connect(self.clear_table)
        self.pushButton.clicked.connect(self.group_df)

        self.actionTo_CSV.triggered.connect(self.export_csv)
        self.actionTo_XLS.triggered.connect(self.export_xls)
        self.actionImportuj_2.triggered.connect(self.import_csv)

        self.actionOpen_directory.triggered.connect(self.choose_dir)
        self.actionCount_spectra.triggered.connect(self.count_files)
        self.actionRead_spectra.triggered.connect(self.analyze_files)
        self.actionMatch_users.triggered.connect(self.analyze_users)
        self.actionDelete_rows.triggered.connect(self.clear_table)
        self.actionCreate_summary.triggered.connect(self.group_df)
        self.actionShow_summary.triggered.connect(lambda: self.activateTab(3))

        self.raport_button.clicked.connect(self.create_report)
        self.zaksieguj.clicked.connect(self.save_bills)

    def set_connections_mail(self):
        self.actionConnect.triggered.connect(self.connect_server)
        self.actionLogin.triggered.connect(self.login_server)
        self.actionClose_connection.triggered.connect(self.close_connection)
        self.button_connect.clicked.connect(self.connect_server)
        self.button_login.clicked.connect(self.login_server)
        self.button_logout.clicked.connect(self.close_connection)

        self.pushButton_2.clicked.connect(self.choose_spectra)
        self.pushButton_3.clicked.connect(self.match_user)
        self.actionOpen_directory_2.triggered.connect(self.choose_spectra)
        self.actionMatch_users_2.triggered.connect(self.match_user)

        self.pushButton_5.clicked.connect(self.send_all)
        self.pushButton_6.clicked.connect(self.send_selected)
        self.pushButton_4.clicked.connect(self.deleteRows)
        self.actionSend_all.triggered.connect(self.send_all)
        self.actionSend_selected.triggered.connect(self.send_selected)
        self.actionDelete_rows_2.triggered.connect(self.deleteRows)

        self.tableWidget_2.itemSelectionChanged.connect(self.tabSelChange)

    def set_connections_bills(self):
        self.new_bill.clicked.connect(self.add_new_bill)
        self.delete_bill.clicked.connect(self.del_bill)
        self.edit_bill.clicked.connect(self.edit_existing_bill)
        self.tableWidget_4.cellDoubleClicked.connect(self.edit_existing_bill)
        self.archive_button.clicked.connect(self.archive_bill)

        self.filter_bills.clicked.connect(self.filterbills)
        self.send_bill_msg.clicked.connect(self.send_bill_mail)

        self.actionNew_Bill.triggered.connect(self.add_new_bill)
        self.actionEdit_bill.triggered.connect(self.edit_existing_bill)
        self.actionDelete.triggered.connect(self.del_bill)
        self.actionMark_as_archived.triggered.connect(self.archive_bill)
        self.actionOpen_corresponding_report.triggered.connect(self.open_bill_report)

        self.tableWidget_4.itemSelectionChanged.connect(self.billtabSelChange)
        self.platnik_send.currentIndexChanged.connect(self.comboSelChange)

    def set_connections_logs(self):
        self.choose_log.clicked.connect(self.get_open_log)
        self.read_log.clicked.connect(self.read_log_file)
        self.actionOpen_log_file.triggered.connect(self.get_open_log)

    def set_connections_options(self):
        self.actionUsers.triggered.connect(self.edit_users)
        self.actionPreferences.triggered.connect(self.show_options)

    def activateTab(self, num):
        self.stackedWidget.setCurrentIndex(num)
        self.disable_menus()
        for item in self.menu_fields[num]:
            item.setEnabled(True)

    def disable_menus(self):
        for item in self.menu_fields:
            if item:
                for jtem in item:
                    jtem.setEnabled(False)

    def show_error_msg(self, error, title, type):
        icons = {'Critical': QtWidgets.QMessageBox.Critical, 'Information': QtWidgets.QMessageBox.Information,
                 'Warning': QtWidgets.QMessageBox.Warning}
        error_dialog = QtWidgets.QMessageBox(self)
        error_dialog.setWindowTitle("An error occured!")
        error_dialog.setText(title)
        error_dialog.setInformativeText(str(error))
        error_dialog.setIcon(icons[type])

        error_dialog.show()

    def closeEvent(self, evnt):
        evnt.ignore()
        self.quit_app()

    def quit_app(self):
        msg = 'Do you want to quit program? This will terminate all active processes.'
        ans = QtWidgets.QMessageBox.question(self, 'Quit', msg,
                                             QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if ans == QtWidgets.QMessageBox.Yes:
            sys.exit()

    def set_tables_widths(self):
        self.tableWidget.setColumnWidth(0, 600)
        self.tableWidget.setColumnWidth(1, 200)
        self.tableWidget.setColumnWidth(2, 150)
        self.tableWidget.setColumnWidth(3, 300)
        self.tableWidget.setColumnWidth(4, 300)
        self.tableWidget.setColumnWidth(5, 200)
        self.tableWidget.setColumnWidth(6, 200)
        self.tableWidget.setColumnWidth(7, 100)
        self.tableWidget.setColumnWidth(8, 100)
        self.tableWidget.setColumnWidth(9, 200)
        self.tableWidget.setColumnWidth(10, 100)
        self.tableWidget.setColumnWidth(11, 100)
        self.tableWidget.setColumnWidth(12, 100)

        self.tableWidget_2.setColumnWidth(0, 600)
        self.tableWidget_2.setColumnWidth(1, 150)
        self.tableWidget_2.setColumnWidth(2, 150)
        self.tableWidget_2.setColumnWidth(3, 300)
        self.tableWidget_2.setColumnWidth(4, 150)
        self.tableWidget_2.setColumnWidth(5, 400)

        self.tableWidget_3.setColumnWidth(0, 200)
        self.tableWidget_3.setColumnWidth(1, 250)
        self.tableWidget_3.setColumnWidth(2, 300)
        self.tableWidget_3.setColumnWidth(3, 180)
        self.tableWidget_3.setColumnWidth(4, 150)
        self.tableWidget_3.setColumnWidth(5, 100)

        self.tableWidget_4.setColumnWidth(0, 50)
        self.tableWidget_4.setColumnWidth(1, 120)
        self.tableWidget_4.setColumnWidth(2, 150)
        self.tableWidget_4.setColumnWidth(3, 200)
        self.tableWidget_4.setColumnWidth(4, 200)
        self.tableWidget_4.setColumnWidth(5, 120)
        self.tableWidget_4.setColumnWidth(6, 120)
        self.tableWidget_4.setColumnWidth(7, 120)
        self.tableWidget_4.setColumnWidth(8, 120)
        self.tableWidget_4.setColumnWidth(9, 120)
        self.tableWidget_4.setColumnWidth(10, 200)
        self.tableWidget_4.setColumnWidth(11, 200)
        self.tableWidget_4.setColumnWidth(12, 120)

        self.treeWidget.setColumnWidth(0, 400)
        self.treeWidget.setColumnWidth(1, 150)
        self.treeWidget.setColumnWidth(2, 250)
        self.treeWidget.setColumnWidth(3, 200)
        self.treeWidget.setColumnWidth(4, 150)

    def show_options(self):
        options = OptionsDialog(self)
        if self.params:
            options.server.setText(self.params['server'])
            options.port.setValue(self.params['port'])
            options.timeout.setValue(self.params['timeout'])
            options.username.setText(self.params['username'])
            options.password.setText(self.params['password'])
            options.mail_from.setText(self.params['mail_from'])
            options.mail_ans.setText(self.params['mail_ans'])
            options.mail_topic.setText(self.params['mail_topic'])
            options.mail_text.setText(self.params['mail_text'])

            options.main_dir.setText(self.params['main_dir'])
            options.zip_dir.setText(self.params['zip_dir'])
            options.log_dir.setText(self.params['log_dir'])

            options.price.setValue(float(self.params['price'] or 0))
            options.spectra_dir.setText(self.params['spectra_dir'])
            options.report_dir.setText(self.params['report_dir'])
            options.notification_emails.setText(self.params['notification_mails'].replace(';', '\n'))
            with open('data/bill_mail.txt', 'r', encoding='utf-8') as mail_template:
                options.notification_text.setText(mail_template.read())

            options.nadplata.setText(self.params['nadplata'])
            options.niedoplata.setText(self.params['niedoplata'])
            options.saldo.setText(self.params['saldo'])
            options.brak_naleznosci.setText(self.params['brak_naleznosci'])

        options.show()

        if options.exec_():
            self.params['server'] = options.server.text()
            self.params['port'] = options.port.value()
            self.params['timeout'] = options.timeout.value()
            self.params['username'] = options.username.text()
            self.params['password'] = options.password.text()
            self.params['mail_from'] = options.mail_from.text()
            self.params['mail_ans'] = options.mail_ans.text()
            self.params['mail_topic'] = options.mail_topic.text()
            self.params['mail_text'] = options.mail_text.toPlainText()

            self.params['main_dir'] = options.main_dir.text()
            self.params['zip_dir'] = options.zip_dir.text()
            self.params['log_dir'] = options.log_dir.text()

            self.params['price'] = options.price.value()
            self.params['spectra_dir'] = options.spectra_dir.text()
            self.params['report_dir'] = options.report_dir.text()
            self.params['notification_mails'] = options.notification_emails.toPlainText().replace('\n', ';')

            with open('data/bill_mail.txt', 'w', encoding='utf-8') as mail_template:
                mail_template.write(options.notification_text.toPlainText())

            self.params['nadplata'] = options.nadplata.text()
            self.params['niedoplata'] = options.niedoplata.text()
            self.params['saldo'] = options.saldo.text()
            self.params['brak_naleznosci'] = options.brak_naleznosci.text()

            self.save_params()
            self.set_params()

    def save_params(self):
        with open('data/params.txt', 'w') as output:
            json.dump(self.params, output)

    def set_params(self):
        self.label_server.setText(self.params['server'])
        self.label_port.setText('%d' % self.params['port'])
        # self.label_user.setText(self.params['username'])
        self.label_from.setText(self.params['mail_from'])
        self.label_ans.setText(self.params['mail_ans'])
        self.label_topic.setText(self.params['mail_topic'])
        self.label_text.setText(self.params['mail_text'])
        self.doubleSpinBox.setValue(float(self.params['price'] or 0))

    ####wysylanie###

    def connect_server(self):

        self.sender = mail.MailSender(self.params['server'], self.params['port'], self.params['timeout'])

        thread = QtCore.QThread(self)
        worker = self.mail_worker = MailWorker(self.sender, self.params)
        # self.stop_button.clicked.connect(self.worker.kill)
        worker.moveToThread(thread)
        thread.started.connect(worker.connect_to_server)

        # worker.status.connect(self.statusbar.showMessage)
        worker.status.connect(self.status_label.setText)
        worker.finished.connect(self.finish_connection)

        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        worker.finished.connect(thread.quit)

        self.button_connect.setEnabled(False)
        self.actionConnect.setEnabled(False)

        self.label_status.setText('Connecting...')
        pixmap = QtGui.QPixmap('icons/if_Circle_Orange_34213.ico')
        self.label_17.setPixmap(pixmap)

        thread.start()

    def finish_connection(self, status):
        if status:
            self.label_status.setText('Connected')
            pixmap = QtGui.QPixmap('icons/if_Circle_Yellow_34215.ico')
            self.label_17.setPixmap(pixmap)

            self.button_login.setEnabled(True)
            self.button_logout.setEnabled(True)
            self.actionLogin.setEnabled(True)
            self.actionClose_connection.setEnabled(True)
            self.current_pixmap = QtGui.QPixmap('icons/if_Circle_Yellow_34215.ico')
            self.status_control()
        else:
            self.label_status.setText('Connection error')
            pixmap = QtGui.QPixmap('icons/if_Circle_Red_34214.ico')
            self.label_17.setPixmap(pixmap)
            self.button_connect.setEnabled(True)
            self.actionConnect.setEnabled(True)

    def status_control(self):
        thread = QtCore.QThread(self)
        worker = self.status_worker = StatusControlWorker(self.sender)

        worker.moveToThread(thread)
        thread.started.connect(worker.start_status_control)

        worker.finished.connect(self.close_server_connection)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        worker.finished.connect(thread.quit)

        worker.status_info.connect(self.status_color)

        thread.start()

    def status_color(self, status_info):
        status_code = status_info[0]
        if status_code == 9:
            pixmap = QtGui.QPixmap('icons/if_Circle_Empty_34217.ico')
            self.label_17.setPixmap(pixmap)
        elif status_code == 0:
            pixmap = QtGui.QPixmap('icons/if_Circle_Red_34214.ico')
            self.label_17.setPixmap(pixmap)
            self.label_status.setText(status_info[1])
            self.close_connection()
        elif status_code == 1:
            self.label_17.setPixmap(self.current_pixmap)
            # self.repaint()

    def login_server(self):

        params = self.params.copy()

        username = params['username']
        password = params['password']

        if not (username and password):
            login = Login(self)
            login.show()
            login.username.setText(params['username'])

            if login.exec_():
                username = login.username.text()
                password = login.password.text()
                params['username'] = username
                params['password'] = password

        thread = QtCore.QThread(self)
        worker = self.mail_worker = MailWorker(self.sender, params)
        # self.stop_button.clicked.connect(self.worker.kill)
        worker.moveToThread(thread)
        thread.started.connect(worker.login)

        # self.pushButton_8.clicked.connect(thread.quit)

        # worker.status.connect(self.statusbar.showMessage)
        worker.status.connect(self.status_label.setText)
        worker.user_info.connect(self.label_user.setText)
        worker.finished.connect(self.finish_login)

        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        worker.finished.connect(thread.quit)

        for item in [self.button_connect, self.button_login, self.button_logout,
                     self.actionConnect, self.actionLogin, self.actionClose_connection]:
            item.setEnabled(False)

        self.label_status.setText('Logging in...')
        pixmap = QtGui.QPixmap('icons/if_Circle_Orange_34213.ico')
        self.label_17.setPixmap(pixmap)

        thread.start()

    def finish_login(self, status):
        if status:
            self.label_status.setText('Ready')
            pixmap = QtGui.QPixmap('icons/if_Circle_Green_34211.ico')
            self.label_17.setPixmap(pixmap)
            self.current_pixmap = QtGui.QPixmap('icons/if_Circle_Green_34211.ico')
            for item in [self.pushButton_5, self.pushButton_6]:
                item.setEnabled(True)
        else:
            self.label_status.setText('Authentication error')
            pixmap = QtGui.QPixmap('icons/if_Circle_Orange_34213.ico')

            self.label_17.setPixmap(pixmap)
            self.current_pixmap = QtGui.QPixmap('icons/if_Circle_Orange_34213.ico')
            self.button_login.setEnabled(True)
            self.actionLogin.setEnabled(True)
        self.button_logout.setEnabled(True)
        self.actionClose_connection.setEnabled(True)

    def close_connection(self):
        if self.status_worker:
            self.status_worker.abort = True

    def close_server_connection(self):
        self.sender.close()
        self.status_label.setText('Connection closed')
        self.button_connect.setEnabled(True)
        self.actionConnect.setEnabled(True)

        for item in [self.button_logout, self.button_login, self.pushButton_5, self.pushButton_6,
                     self.actionLogin, self.actionClose_connection]:
            item.setEnabled(False)
        self.label_user.setText('')

        self.label_status.setText('No connection')
        pixmap = QtGui.QPixmap('icons/if_Circle_Red_34214.ico')
        self.label_17.setPixmap(pixmap)

    def tabSelChange(self):
        selected_rows = self.tableWidget_2.selectedIndexes()
        if selected_rows:
            self.pushButton_4.setEnabled(True)
            self.actionDelete_rows_2.setEnabled(True)
        else:
            self.pushButton_4.setEnabled(False)
            self.actionDelete_rows_2.setEnabled(False)

    def deleteRows(self):
        selected_rows = self.tableWidget_2.selectedIndexes()

        indices = list(set([x.row() for x in selected_rows]))
        for item in reversed(sorted(indices)):
            self.tableWidget_2.removeRow(item)

    def choose_spectra(self):

        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        file_dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
        if self.params['main_dir']:
            file_dialog.setDirectory(self.params['main_dir'])

        for view in file_dialog.findChildren((QtWidgets.QListView, QtWidgets.QTreeView)):
            if isinstance(view.model(), QtWidgets.QFileSystemModel):
                view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        paths = None
        if file_dialog.exec_():
            paths = file_dialog.selectedFiles()

        for item in paths or []:
            cur_row = self.tableWidget_2.rowCount()
            self.tableWidget_2.insertRow(cur_row)

            path_item = QtWidgets.QTableWidgetItem(item)
            path_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            # path_item.setLayoutDirection(QtCore.Qt.RightToLeft)
            self.tableWidget_2.setItem(cur_row, 0, path_item)
            directory_size = mail.Compressor.calculate_size(item)
            size_item = QtWidgets.QTableWidgetItem('%.2f MB' % (float(directory_size) / 1000000))
            self.tableWidget_2.setItem(cur_row, 4, size_item)

    def match_user(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        i = 0
        self.tableWidget_2.setSortingEnabled(False)
        rows = self.tableWidget_2.rowCount()

        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.NoBrush)

        for i in range(rows):
            path_item = self.tableWidget_2.item(i, 0)
            # self.tableWidget.setItem(i,3,QtWidgets.QTableWidgetItem(''))
            # self.tableWidget.setItem(i,4,QtWidgets.QTableWidgetItem(''))
            if path_item:
                path_text = path_item.text()
            else:
                path_text = ''

            sample_text = os.path.split(path_text)[1]
            self.tableWidget_2.setItem(i, 1, QtWidgets.QTableWidgetItem(sample_text))
            user_text = sample_text.split('.')[0]

            result = Spectrum.find_user(user_text)

            user_item = QtWidgets.QTableWidgetItem(result[0])
            if result[0] == '__undefined__':
                user_item.setForeground(brush)
            self.tableWidget_2.setItem(i, 2, user_item)

            mail_item = QtWidgets.QTableWidgetItem(result[2])
            if result[1] == '__undefined__':
                mail_item.setForeground(brush)
            self.tableWidget_2.setItem(i, 3, mail_item)

            i = i + 1
            progress = i / rows
            self.progressBar.setValue(progress * 100)
        self.tableWidget_2.setSortingEnabled(True)
        QtWidgets.QApplication.restoreOverrideCursor()

    def send_selected(self):
        selected_rows = self.tableWidget_2.selectedIndexes()
        indices = list(set([x.row() for x in selected_rows]))
        col_white = QtGui.QColor(255, 255, 255)
        for item in indices:
            self.setRowColor(item, col_white)

        data_list = []
        for i in indices:
            path_item = self.tableWidget_2.item(i, 0)
            if path_item:
                path_text = path_item.text()
            else:
                path_text = ''
            mail_item = self.tableWidget_2.item(i, 3)
            if mail_item:
                mail_text = mail_item.text()
            else:
                mail_text = ''
            name_item = self.tableWidget_2.item(i, 1)
            if name_item:
                name_text = name_item.text()
            else:
                name_text = ''
            size_item = self.tableWidget_2.item(i, 4)
            if size_item:
                size_text = size_item.text()
            else:
                size_text = ''
            data_list.append((i, path_text, name_text, mail_text, size_text))
        self.send(data_list)

    def send_all(self):

        rows = self.tableWidget_2.rowCount()
        col_white = QtGui.QColor(255, 255, 255)
        for item in range(rows):
            self.setRowColor(item, col_white)

        data_list = []
        for i in range(rows):
            path_item = self.tableWidget_2.item(i, 0)
            if path_item:
                path_text = path_item.text()
            else:
                path_text = ''
            mail_item = self.tableWidget_2.item(i, 3)
            if mail_item:
                mail_text = mail_item.text()
            else:
                mail_text = ''
            name_item = self.tableWidget_2.item(i, 1)
            if name_item:
                name_text = name_item.text()
            else:
                name_text = ''
            size_item = self.tableWidget_2.item(i, 4)
            if size_item:
                size_text = size_item.text()
            else:
                size_text = ''
            data_list.append((i, path_text, name_text, mail_text, size_text))
        self.send(data_list)

    def filter_data(self, data_list):
        new_list = []
        for i, item in enumerate(data_list):
            size_text = item[4]
            name_text = item[2]
            size_obj = re.search(r'^(.*) MB', size_text)
            if size_obj:
                size = float(size_obj.groups()[0])
            else:
                size = 0
            if size > 20:
                msg = 'The total size of the directory corresponding to spectrum ' + \
                      name_text + ' is greater than 20 MB, and probably will be rejected by server. Do you really want to try to send these spectrum as a e-mail message?'
                ans = QtWidgets.QMessageBox.warning(self, 'Spectrum size warning', msg,
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                    QtWidgets.QMessageBox.No)
                if ans == QtWidgets.QMessageBox.Yes:
                    new_list.append(item)
            else:
                new_list.append(item)

        return new_list

    def send(self, raw_data_list):
        data_list = self.filter_data(raw_data_list)
        thread = QtCore.QThread(self)
        worker = self.mail_worker = MailWorker(self.sender, self.params, data_list)
        # self.stop_button.clicked.connect(self.worker.kill)
        worker.moveToThread(thread)
        self.tableWidget_2.setSortingEnabled(False)
        self.pushButton_7.setEnabled(True)
        for item in [self.button_logout, self.pushButton_2, self.pushButton_3,
                     self.pushButton_5, self.pushButton_6, self.actionClose_connection]:
            item.setEnabled(False)

        # self.pushButton_7.clicked.connect(worker.kill)
        self.pushButton_7.clicked.connect(self.kill_sending)
        thread.started.connect(worker.send)

        # worker.status.connect(self.statusbar.showMessage)
        worker.status.connect(self.status_label.setText)
        worker.progress.connect(self.progressBar.setValue)

        worker.status_info.connect(self.show_status)

        worker.killed.connect(self.finish_sending)

        worker.finished.connect(self.finish_sending)

        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        worker.finished.connect(thread.quit)

        thread.start()

    def kill_sending(self):
        self.mail_worker.abort = True

    def finish_sending(self):
        for item in [self.button_logout, self.pushButton_2, self.pushButton_3,
                     self.pushButton_5, self.pushButton_6, self.actionClose_connection]:
            item.setEnabled(True)

        self.pushButton_7.setEnabled(False)
        self.tableWidget_2.setSortingEnabled(True)

    def setRowColor(self, rowIndex, color):
        for j in range(self.tableWidget_2.columnCount()):
            try:
                self.tableWidget_2.item(rowIndex, j).setBackground(color)
            except:
                pass

    def show_status(self, num, status):
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.NoBrush)

        col_red = QtGui.QColor(255, 0, 0)
        col_yellow = QtGui.QColor(255, 224, 36)
        col_green = QtGui.QColor(0, 205, 0)

        status_text = status[1]
        status_item = QtWidgets.QTableWidgetItem(status_text)
        self.tableWidget_2.setItem(num, 5, status_item)
        if status[0] == 0:
            self.setRowColor(num, col_red)
        elif status[0] == 2:
            self.setRowColor(num, col_green)
        else:
            self.setRowColor(num, col_yellow)

    ####rozliczenie############################################################

    def export_csv(self):
        cwd = self.params['report_dir'] or os.getcwd()
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, 'Exportuj', cwd, 'CSV (*.csv)')[0]
        if fileName:
            df = self.read_df()
            df.to_csv(fileName, sep=',', index_label='ID')

    def export_xls(self):
        cwd = self.params['report_dir'] or os.getcwd()
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, 'Exportuj', cwd, 'XLS (*.xls)')[0]
        if fileName:
            df = self.read_df()
            df.to_excel(fileName)

    def import_csv(self):
        cwd = self.params['report_dir'] or os.getcwd()
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Otwórz plik', cwd, 'CSV (*.csv)')[0]
        if fileName:
            imported_df = read_csv(fileName, sep=',', index_col='ID')
            rows = self.tableWidget.rowCount()
            if rows > 0:
                msg_box = MessageBox(self)
                ans = msg_box.exec_()
                if ans:
                    ans2 = msg_box.ans
                    if ans2 == 1:
                        self.tableWidget.clearContents()
                        self.tableWidget.setRowCount(0)
                    self.fill_from_df(imported_df)
            else:
                self.fill_from_df(imported_df)

    def fill_from_df(self, df):
        brush = QtGui.QBrush(QtGui.QColor(213, 121, 0))
        brush.setStyle(QtCore.Qt.NoBrush)
        df = df.fillna('')
        for i, item in enumerate(df.index.tolist()):
            self.tableWidget.insertRow(i)
            for j, column in enumerate(df):
                # print(column)
                item_text = str(df[column][item])
                tab_item = QtWidgets.QTableWidgetItem(item_text)
                if item_text == '__undefined__':
                    tab_item.setForeground(brush)
                self.tableWidget.setItem(i, j, tab_item)

    def group_df_old(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        full_df = self.read_df()
        full_df['STime'] = full_df['STime'].map(float)

        grouped_df = full_df.groupby(['Payer'])['STime'].sum()
        QtWidgets.QApplication.restoreOverrideCursor()
        summary = Summary(self)
        summary.fill_table(grouped_df)
        summary.show()

    def read_df(self):
        rows = self.tableWidget.rowCount()
        cols = self.tableWidget.columnCount()

        full_df = DataFrame(columns=['Spectrum', 'Date', 'Username', 'User', 'Payer',
                                     'Start', 'End', 'Time', 'STime', 'EXP', 'NS', 'TD1', 'TD2'], index=range(rows))

        for i in range(rows):
            for j in range(cols):
                item = self.tableWidget.item(i, j)
                if item:
                    full_df.iloc[i, j] = item.text()
                else:
                    full_df.iloc[i, j] = ''

        full_df.to_csv('temp/temp.csv', sep=';')
        return full_df

    def edit_users(self):

        users_dialog = EditUsers(self)
        users_dialog.show()

    def mainTabSelChange(self):
        selected_rows = self.tableWidget.selectedIndexes()
        if selected_rows:
            self.del_button.setEnabled(True)
            self.actionDelete_rows.setEnabled(True)
        else:
            self.del_button.setEnabled(False)
            self.actionDelete_rows.setEnabled(True)

    def clear_table(self):
        msg = 'Czy na pewno chcesz usunąć wybrane wiersze?'
        ans = QtWidgets.QMessageBox.question(self, 'Usuń dane', msg,
                                             QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if ans == QtWidgets.QMessageBox.Yes:
            selected_rows = self.tableWidget.selectedIndexes()

            indices = list(set([x.row() for x in selected_rows]))
            for item in reversed(sorted(indices)):
                self.tableWidget.removeRow(item)

    def choose_dir(self):
        directory = self.params['spectra_dir'] or os.getcwd()
        destDir = QtWidgets.QFileDialog.getExistingDirectory(None,
                                                             'Wybierz folder do przeanalizowania',
                                                             directory,
                                                             QtWidgets.QFileDialog.ShowDirsOnly)

        self.dest_dir.setText(destDir)

    def set_dates(self):
        self.start = self.dateEdit.date().toPyDate()
        self.end = self.dateEdit_2.date().toPyDate()

        # print(self.start,self.end)

    def set_found(self, status, num):
        self.found = num
        self.stop_button.hide()
        self.label_found.setText("Znalezionych widm: " + '%d' % self.found)

    def count_files(self):
        rootdir = self.dest_dir.text()
        self.set_dates()
        self.stop_button.show()

        thread = QtCore.QThread(self)
        worker = self.worker = Worker(rootdir, self.start, self.end)
        self.stop_button.clicked.connect(self.worker.kill)
        worker.moveToThread(thread)
        thread.started.connect(worker.count_files)
        worker.progress.connect(self.progressBar.value)
        worker.status.connect(self.statusbar.showMessage)
        worker.killed.connect(self.an_finished)
        worker.finished.connect(self.set_found)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        worker.finished.connect(thread.quit)

        thread.start()

    def an_finished(self):
        self.tableWidget.setSortingEnabled(True)
        self.stop_button.hide()

    def insert_row(self, row_list):
        rows = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rows)
        for j, item in enumerate(row_list):
            self.tableWidget.setItem(rows, j, item)

    def analyze_files(self):
        self.tableWidget.setSortingEnabled(False)
        rootdir = self.dest_dir.text()
        self.set_dates()
        self.stop_button.show()

        thread = QtCore.QThread(self)
        worker = self.worker = Worker(rootdir, self.start, self.end, self.found)

        worker.moveToThread(thread)
        self.stop_button.clicked.connect(self.worker.kill)
        thread.started.connect(worker.analyze_files)
        worker.progress.connect(self.progressBar.setValue)
        worker.status.connect(self.statusbar.showMessage)

        # worker.finished.connect(self.set_found)
        worker.return_row.connect(self.insert_row)
        worker.finished.connect(self.an_finished)
        worker.killed.connect(self.an_finished)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        worker.finished.connect(thread.quit)
        thread.start()

    def group_df(self):
        self.activateTab(3)
        self.treeWidget.setEnabled(False)

        self.repaint()

        self.summ_df = DataFrame(columns=['Count', 'Times', 'Cost', 'Users'])

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        full_df = self.read_df()
        full_df['STime'] = full_df['STime'].map(float)

        self.full_df = full_df

        for item in full_df.index.tolist():
            user = full_df.loc[item, 'User']
            if user == "__undefined__":
                username = full_df.loc[item, 'Username']
                full_df.loc[item, 'User'] = username

        self.lineEdit.setText(self.dest_dir.text())

        if self.start:
            self.dateEdit_3.setDate(self.start)

        if self.end:
            self.dateEdit_4.setDate(self.end)

        self.treeWidget.clear()
        header = QtWidgets.QTreeWidgetItem(["Płatnik", "Liczba widm", "Czas", "Czas [s]", "Koszt [PLN]"])
        self.treeWidget.setHeaderItem(header)

        thread = QtCore.QThread(self)
        worker = self.group_worker = GroupWorker(full_df)
        worker.moveToThread(thread)

        thread.started.connect(worker.group)

        worker.progress.connect(self.progressBar.setValue)
        worker.status.connect(self.statusbar.showMessage)

        worker.return_row.connect(self.group_row)

        worker.finished.connect(self.gr_finished)
        worker.killed.connect(self.gr_finished)

        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        worker.finished.connect(thread.quit)

        thread.start()

    def gr_finished(self):
        QtWidgets.QApplication.restoreOverrideCursor()
        self.treeWidget.setEnabled(True)
        # print(self.summ_df)

        # summary=Summary(self)
        # summary.fill_table(grouped_df)
        # summary.show()

    def create_report(self):
        report_title = self.Combo_Zlec.currentText()

        start = datetime.datetime.strftime(self.dateEdit_3.date().toPyDate(), '%Y-%m-%d')
        end = datetime.datetime.strftime(self.dateEdit_4.date().toPyDate(), '%Y-%m-%d')

        cwd = self.params['report_dir'] or os.getcwd()
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, 'Zapisz raport', cwd, 'PDF (*.pdf)')[0]
        if fileName:
            rep_gen = report.Generator(fileName, report_title, start, end, float(self.doubleSpinBox.value()),
                                       self.summ_df, self.full_df)
            rep_gen.generate_report()
            self.raport_path.setText(fileName)
            if sys.platform.startswith('linux'):
                call(["xdg-open", fileName])
            else:
                os.startfile(fileName)

    def save_bills(self):
        bills = bill.Bill()

        zlec = self.Combo_Zlec.currentText()
        start = self.dateEdit_3.date().toPyDate()
        end = self.dateEdit_4.date().toPyDate()

        report_path = self.raport_path.text()

        for item in self.summ_df.index.tolist():
            if item != '__undefined__':
                lexp = self.summ_df.loc[item, 'Count']
                hours = '%.2f' % (float(self.summ_df.loc[item, 'Times']) / 3600)
                cost = '%.2f' % (-1 * float(self.summ_df.loc[item, 'Cost']))
                partial_name = report_path.split('.')[0].replace(' ', '_') + '_' + item.replace(', ', '_') + '.pdf'

                bills.new('Obciazenie', zlec, item, cost, hours, lexp, start, end,
                          'Cena jednostkowa %.2f' % float(self.doubleSpinBox.value()), partial_name, 'Nowe')

        self.activate_bills()

    def group_row(self, status, payer_list):
        price = float(self.doubleSpinBox.value())
        if status:
            stime = float(payer_list[3])
            cost = stime * price / 3600

            payer_tree = QtWidgets.QTreeWidgetItem(self.treeWidget, payer_list[0:4] + ['%.2f' % cost])
            users_list = payer_list[4:]
            for item in users_list:
                user_tree = QtWidgets.QTreeWidgetItem(payer_tree, item)
                payer_tree.addChild(user_tree)
            self.treeWidget.addTopLevelItem(payer_tree)

            self.summ_df.loc[payer_list[0], 'Count'] = int(payer_list[1])
            self.summ_df.loc[payer_list[0], 'Times'] = float(payer_list[3])
            self.summ_df.loc[payer_list[0], 'Cost'] = cost
            self.summ_df.loc[payer_list[0], 'Users'] = users_list
        self.repaint()

    def analyze_users(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        i = 0
        self.tableWidget.setSortingEnabled(False)
        rows = self.tableWidget.rowCount()

        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.NoBrush)

        for i in range(rows):
            user_item = self.tableWidget.item(i, 2)
            # self.tableWidget.setItem(i,3,QtWidgets.QTableWidgetItem(''))
            # self.tableWidget.setItem(i,4,QtWidgets.QTableWidgetItem(''))
            if user_item:
                user_text = user_item.text()
            else:
                user_text = ''

            result = Spectrum.find_user(user_text)

            for j, item in enumerate(result[0:2]):
                tab_item = QtWidgets.QTableWidgetItem(item)
                if item == '__undefined__':
                    tab_item.setForeground(brush)
                self.tableWidget.setItem(i, j + 3, tab_item)

            i = i + 1
            progress = i / rows
            self.progressBar.setValue(progress * 100)
        self.tableWidget.setSortingEnabled(True)
        QtWidgets.QApplication.restoreOverrideCursor()

    def get_open_log(self):
        log_dir = self.params['log_dir']
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Open log file', log_dir, 'Log files (*.log)')[0]
        self.logpath.setText(fileName)

    def read_log_file(self):
        self.tableWidget_3.clearContents()
        self.tableWidget_3.setSortingEnabled(False)
        fileName = self.logpath.text()
        if fileName:
            log_df = read_csv(fileName, sep=',', index_col=0)
            log_df.fillna('', inplace=True)
            for i, item in enumerate(log_df.index.tolist()):
                time = log_df['time'][item]
                name = log_df['spectrum'][item]
                to = log_df['address'][item]
                from_ad = log_df['from'][item]
                user = log_df['by'][item]
                status = log_df['status'][item]

                values_list = [time, name, to, from_ad, user, status]
                rows = self.tableWidget_3.rowCount()
                self.tableWidget_3.insertRow(rows)
                for j, item2 in enumerate(values_list):
                    table_item = QtWidgets.QTableWidgetItem(item2)
                    self.tableWidget_3.setItem(i, j, table_item)

        self.tableWidget_3.setSortingEnabled(True)

    ##################Platnosci##########################################

    def activate_bills(self):
        self.bills = bill.Bill()

        curr_date = QtCore.QDate.currentDate()
        self.created_to.setDate(curr_date)
        self.expt_to.setDate(curr_date)

        year = curr_date.year()
        begin_date = QtCore.QDate(year, 1, 1)
        self.created_from.setDate(begin_date)
        self.exp_from.setDate(begin_date)

        self.bill_payer.clear()
        self.bill_payer.addItems(user_df['User'])
        self.bill_payer.setCurrentIndex(-1)

        self.type_exp.clear()
        self.type_exp.addItems(['Zmieniacz', 'Zlecenia indywidualne', 'Spektrometr 300 MHz'])
        self.type_exp.setCurrentIndex(-1)

        self.activateTab(4)
        #self.show_bills(self.bills.filter())
        self.filterbills()

    def filterbills(self):
        date1 = self.created_from.date().toPyDate()
        date2 = self.created_to.date().toPyDate()

        date3 = self.exp_from.date().toPyDate()
        date4 = self.expt_to.date().toPyDate()

        payer = self.bill_payer.currentText()
        zlec_type = self.type_exp.currentText()

        arch = self.check_arch.isChecked()
        obciaz = self.check_obciazenia.isChecked()
        uznania = self.check_uznania.isChecked()

        filtered_bills = self.bills.filter(payer, zlec_type, date1, date2, date3, date4, arch, obciaz, uznania)

        self.show_bills(filtered_bills)

    def show_bills(self, bill_df):
        self.tableWidget_3.clearContents()
        self.tableWidget_3.setSortingEnabled(False)

        self.tableWidget_4.setRowCount(0)

        # bill_df=self.bills.filter()

        for i, item in enumerate(bill_df.index.tolist()):
            date = bill_df['Date'][item]
            type = bill_df['Type'][item]
            zlec = bill_df['Zlecenie'][item]
            payer = bill_df['Payer'][item]
            price = float(bill_df['Price'][item])
            hours = float(bill_df['Hours'][item])
            expt = float(bill_df['Experiments'][item])
            date_from = bill_df['From'][item]
            date_to = bill_df['To'][item]
            uwagi = bill_df['Uwagi'][item]
            report = bill_df['Raport'][item]
            status = bill_df['Status'][item]

            values_list = ['%d' % item, date, type, zlec, payer, '%.2f' % price, '%.2f' % hours, '%d' % expt, date_from,
                           date_to,
                           uwagi, report, status]
            self.tableWidget_4.insertRow(i)
            font = QtGui.QFont()
            if status == 'Archiwalne':
                brush_arch = QtGui.QBrush(QtGui.QColor(160, 160, 160))
            elif status == "Powiadomienie":
                font.setBold(True)
                brush_arch = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            else:
                brush_arch = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                font.setBold(False)
            brush_arch.setStyle(QtCore.Qt.NoBrush)

            for j, item2 in enumerate(values_list):
                table_item = QtWidgets.QTableWidgetItem(item2)
                table_item.setForeground(brush_arch)
                table_item.setFont(font)
                if j == 5 and status != 'Archiwalne':
                    if float(item2) < 0:
                        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
                        brush.setStyle(QtCore.Qt.NoBrush)
                    else:
                        brush = QtGui.QBrush(QtGui.QColor(0, 100, 0))
                        brush.setStyle(QtCore.Qt.NoBrush)
                    table_item.setForeground(brush)
                if j == 5 or j == 6 or j == 7:
                    table_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                if j == 11:
                    table_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter | QtCore.Qt.AnchorRight)

                self.tableWidget_4.setItem(i, j, table_item)

        obc_df = bill_df[bill_df['Price'] < 0]

        opl_df = bill_df[bill_df['Price'] > 0]

        self.num_bills.setText('%d' % len(bill_df.index.tolist()))
        self.num_bills_w.setText('%d' % len(obc_df.index.tolist()))
        self.num_bills_o.setText('%d' % len(opl_df.index.tolist()))

        self.bill_num_exp.setText('%d' % obc_df['Experiments'].sum())
        self.bill_num_exp_w.setText('%d' % obc_df['Experiments'].sum())
        self.bill_num_exp_o.setText('%d' % opl_df['Experiments'].sum())

        self.bill_time_exp.setText('%.2f' % obc_df['Hours'].sum())
        self.bill_time_exp_w.setText('%.2f' % obc_df['Hours'].sum())
        self.bill_time_exp_o.setText('%.2f' % opl_df['Hours'].sum())

        self.bill_price.setText('%.2f' % bill_df['Price'].sum())
        self.bill_price_w.setText('%.2f' % obc_df['Price'].sum())
        self.bill_price_o.setText('%.2f' % opl_df['Price'].sum())

        self.tableWidget_4.setSortingEnabled(True)

        self.platnik_send.clear()
        payers = bill_df.Payer.unique()
        self.platnik_send.addItems(payers)
        self.platnik_send.setCurrentIndex(-1)

    def add_new_bill(self):

        newBillDialog = NewBill(self)
        newBillDialog.show()

        curr_date = QtCore.QDate.currentDate()
        newBillDialog.od.setDate(curr_date)
        newBillDialog.do_2.setDate(curr_date)

        if newBillDialog.exec_():
            type = unidecode.unidecode(newBillDialog.type.currentText())
            zlec = unidecode.unidecode(newBillDialog.zlecenie.currentText())
            payer = unidecode.unidecode(newBillDialog.platnik.currentText())
            price = newBillDialog.kwota.value()
            if type == 'Uznanie':
                price = abs(price)
            elif type == 'Obciazenie':
                price = -1 * abs(price)
            hours = newBillDialog.liczba_godzin.value()
            expt = newBillDialog.liczba_pomiarow.value()
            date_from = newBillDialog.od.date().toPyDate()
            date_to = newBillDialog.do_2.date().toPyDate()
            uwagi = unidecode.unidecode(newBillDialog.uwagi.text())
            raport = newBillDialog.raport_line.text()
            status = unidecode.unidecode(newBillDialog.status_line.text())
            self.bills.new(type, zlec, payer, price, hours, expt, date_from, date_to, uwagi, raport, status)

            self.filterbills()

    def edit_existing_bill(self):

        current_row = self.tableWidget_4.currentRow()
        print(current_row)
        if current_row > -1:
            index = self.tableWidget_4.item(current_row, 0).text()
            values = self.bills.get(int(index))
            print(values)
            print(values[0])
            print(values[1])
            print(values[3])

            newBillDialog = NewBill(self)
            newBillDialog.show()

            widgets = [newBillDialog.id, newBillDialog.type, newBillDialog.zlecenie, newBillDialog.platnik,
                       newBillDialog.kwota, newBillDialog.liczba_godzin, newBillDialog.liczba_pomiarow,
                       newBillDialog.od, newBillDialog.do_2, newBillDialog.uwagi, newBillDialog.raport_line,
                       newBillDialog.status_line]

            widgets[0].setText(index)
            for i, item in enumerate(widgets):
                if i == 1 or i == 2 or i == 3:
                    item.setEditText(values[i])
                elif i == 4 or i == 5 or i == 6:
                    item.setValue(values[i])
                elif i == 7 or i == 8:
                    item.setDate(datetime.datetime.strptime(values[i], '%Y-%m-%d'))
                elif i == 9 or i == 10 or i == 11:
                    item.setText(values[i])

            if newBillDialog.exec_():
                index_ed = int(newBillDialog.id.text())
                type = unidecode.unidecode(newBillDialog.type.currentText())
                zlec = unidecode.unidecode(newBillDialog.zlecenie.currentText())
                payer = unidecode.unidecode(newBillDialog.platnik.currentText())
                price = newBillDialog.kwota.value()
                if type == 'Uznanie':
                    price = abs(price)
                elif type == 'Obciazenie':
                    price = -1 * abs(price)
                hours = newBillDialog.liczba_godzin.value()
                expt = newBillDialog.liczba_pomiarow.value()
                date_from = newBillDialog.od.date().toPyDate()
                date_to = newBillDialog.do_2.date().toPyDate()
                uwagi = unidecode.unidecode(newBillDialog.uwagi.text())
                raport = newBillDialog.raport_line.text()
                status = unidecode.unidecode(newBillDialog.status_line.text())

                self.bills.change(index_ed, type, zlec, payer, price, hours, expt, date_from, date_to, uwagi, raport,
                                  status)

                self.filterbills()

    def archive_bill(self):
        current_row = self.tableWidget_4.currentRow()
        print(current_row)
        if current_row > -1:
            index = self.tableWidget_4.item(current_row, 0).text()
            self.bills.archive(int(index))
            self.filterbills()

    def billtabSelChange(self):
        selected_rows = self.tableWidget_4.selectedIndexes()
        if selected_rows:
            self.delete_bill.setEnabled(True)
            self.edit_bill.setEnabled(True)
            # self.send_bill_msg.setEnabled(True)
            self.archive_button.setEnabled(True)
            self.actionEdit_bill.setEnabled(True)
            self.actionDelete.setEnabled(True)
            self.actionMark_as_archived.setEnabled(True)
            self.actionOpen_corresponding_report.setEnabled(True)
        else:
            self.delete_bill.setEnabled(False)
            self.edit_bill.setEnabled(False)
            # self.send_bill_msg.setEnabled(False)
            self.archive_button.setEnabled(False)
            self.actionEdit_bill.setEnabled(False)
            self.actionDelete.setEnabled(False)
            self.actionMark_as_archived.setEnabled(False)
            self.actionOpen_corresponding_report.setEnabled(False)

    def comboSelChange(self):
        combo_text = self.platnik_send.currentText()
        if combo_text:
            self.send_bill_msg.setEnabled(True)
        else:
            self.send_bill_msg.setEnabled(False)

    def del_bill(self):
        current_row = self.tableWidget_4.currentRow()
        print(current_row)
        if current_row > -1:
            index = self.tableWidget_4.item(current_row, 0).text()
            msg = 'Czy na pewno chcesz usunąć rozliczenie nr ' + index + '?'
            ans = QtWidgets.QMessageBox.question(self, 'Usuń wpis', msg,
                                                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if ans == QtWidgets.QMessageBox.Yes:
                self.bills.delete(int(index))
                self.filterbills()

    def open_bill_report(self):
        current_row = self.tableWidget_4.currentRow()
        if current_row > -1:
            index = self.tableWidget_4.item(current_row, 0).text()
            try:
                self.bills.open_report(int(index))
            except FileNotFoundError as error:
                self.show_error_msg(error, 'Error during opening of the file', 'Critical')

    def find_mail(self, user_name):
        user_match = user_df[user_df['User'] == user_name.strip()]
        if not user_match.empty:
            found_mail = user_match['Mail']
            return found_mail.iloc[0]

    def send_bill_mail(self):
        # selected_rows = self.tableWidget_4.selectedIndexes()
        # indices = [int(self.tableWidget_4.item(item, 0).text()) for item in list(set([x.row() for x in selected_rows]))]
        selected_payer = self.platnik_send.currentText()

        payer_bills = self.bills.filter(payer=selected_payer, arch=True)

        old_bills = payer_bills[payer_bills['Status'] == 'Archiwalne']
        print(old_bills)
        if not old_bills.empty:
            old_price = old_bills['Price'].sum()
        else:
            old_price = 0.0

        df = payer_bills[payer_bills['Status'] != 'Archiwalne']

        current_df_indices = df.index.tolist()

        if old_price:
            old_price_info = '{: 9.2f}'.format(old_price) + '   ' + self.params['saldo']
            # df_to_print.loc['old_bills','Zlecenie']='Saldo z poprzednich okresów rozliczeniowych'
        else:
            old_price_info = ''

        # df=self.bills.get(indices)

        for item in current_df_indices:
            if float(df.loc[item, 'Price']) > 0:
                df.loc[item, 'Zlecenie'] = 'Uznanie'

        if not df.empty:
            table_str = df.to_string(columns=['Price', 'Zlecenie', 'From', 'To', 'Date'],
                                     header=False,
                                     formatters=['{: 9.2f}'.format, None, 'za okres od {}'.format, ' do {}.'.format,
                                                 'Zaksięgowano {}'.format],
                                     index=False, justify='right')
        else:
            table_str = self.params['brak_naleznosci']

        payers = df.Payer.unique()
        if len(payers) == 1:
            payer_info = payers[0]
        else:
            payer_info = 'Więcej niż jeden!'

        total_price = df['Price'].sum() + old_price
        if total_price > 0:
            nadpl = 'nadpłata'
            nadpl_text = self.params['nadplata']
        elif total_price < 0:
            nadpl = 'do zapłaty'
            nadpl_text = self.params['niedoplata']
        else:
            nadpl = ''
            nadpl_text = ''

        attachements = df['Raport']
        # print(attachements)

        zal = [df.loc[index, 'Raport'] for index in current_df_indices]

        zal_names = [' - ' + os.path.basename(item) for item in zal if item]

        with open('data/bill_mail.txt', 'r', encoding='utf-8') as mail_template:
            mail_text = mail_template.read() % (
            self.bills.format_date(datetime.datetime.now()), '; '.join(payers), table_str,
            old_price_info, nadpl, '{: 9.2f} PLN'.format(total_price), nadpl_text,
            '\n'.join(zal_names))

        mail_bill = MailBill(self)
        mail_bill.platnik.setText(payer_info)

        default_mails = self.params['notification_mails']
        for item in default_mails.split(';'):
            mail_bill.mail.addItem(item)

        for item in payers:
            mail = self.find_mail(item)
            if mail:
                mail_bill.mail.addItem(mail)

        mail_bill.tresc.setText(mail_text)
        mail_bill.temat.setText('Rozliczenie pomiarów NMR')
        mail_bill.current_df_indices = current_df_indices
        for report_file in zal:
            if report_file:
                item = QtWidgets.QListWidgetItem()
                item.setText(os.path.basename(report_file))
                item.report_path = report_file
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("icons/pdf.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                item.setIcon(icon)
                mail_bill.listWidget.addItem(item)
        mail_bill.show()

        # if mail_bill.exec_():
        #     files=[mail_bill.listWidget.item(index).report_path for index in range(mail_bill.listWidget.count())]
        #     from_mail=self.params['mail_from']
        #     #if self.button_connect.isEnabled():
        #     #    self.connect_server()
        #     #if self.button_login.isEnabled():
        #     #    self.login_server()
        #     ans_mail = self.sender.send([mail_bill.mail.currentText()], from_mail, mail_bill.temat.text(), mail_bill.tresc.toPlainText(), files, from_mail)
        #     print(ans_mail)
        #     for item in current_df_indices:
        #         self.bills.archive(item)
        #     self.bills.filter()


class NewBill(QtWidgets.QDialog, new_bill.Ui_Dialog):

    def __init__(self, parent=None):
        super(NewBill, self).__init__(parent)
        self.setupUi(self)
        self.platnik.addItems(user_df['User'])
        self.platnik.setCurrentIndex(-1)

        self.type.addItems(['Uznanie', 'Obciazenie'])
        self.zlecenie.addItems(['Zmieniacz', 'Zlecenia indywidualne', 'Spektrometr 300 MHz'])
        self.zlecenie.setCurrentIndex(-1)


class MailBill(QtWidgets.QDialog, report_mail.Ui_Dialog):

    def __init__(self, parent=None):
        super(MailBill, self).__init__(parent)
        self.setupUi(self)
        self.listWidget.itemDoubleClicked.connect(self.load_report)
        self.parent = parent
        self.pushButton.clicked.connect(self.send)

    def load_report(self):
        item = self.listWidget.currentItem()
        report_file = item.report_path

        if sys.platform.startswith('linux'):
            call(["xdg-open", report_file])
        else:
            os.startfile(report_file)

    def send(self):
        files = [self.listWidget.item(index).report_path for index in range(self.listWidget.count())]
        from_mail = self.parent.params['mail_from']
        # if self.button_connect.isEnabled():
        #    self.connect_server()
        # if self.button_login.isEnabled():
        #    self.login_server()
        ans_mail = self.parent.sender.send([self.mail.currentText()], from_mail, self.temat.text(),
                                           self.tresc.toPlainText(), files, from_mail)
        if ans_mail[0]:
            for item in self.current_df_indices:
                self.parent.bills.set_status(item, 'Powiadomienie')
            self.parent.filterbills()

            msg = QtWidgets.QMessageBox.information(self, 'Powiadomienie wysłane',
                                                    'Mail został poprawnie wysłany na adres ' + self.mail.currentText(),
                                                    QtWidgets.QMessageBox.Ok)

            self.destroy()


class GroupWorker(QtCore.QObject):
    def __init__(self, DataFrame, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)

        self.df = DataFrame
        self.abort = False

    def group(self):
        self.status.emit('Trwa generowanie podsumowania. Proszę czekać...')
        self.progress.emit(0)
        try:
            grouped_df = self.df.groupby(['Payer'])['STime'].sum()
            self.progress.emit(50)
            total_items = len(grouped_df.index)
            for i, item in enumerate(grouped_df.index):
                if self.abort is True:
                    print('process aborted')
                    self.killed.emit()
                    break
                payer_spectra = self.df[self.df['Payer'] == item]['STime'].count()
                sec = grouped_df[item]
                td = datetime.timedelta(seconds=sec)
                payer_list = [item, '%d' % payer_spectra, str(td), '%.2f' % sec]

                # self.return_row.emit(0,payer_list)

                filtered_df = self.df[self.df['Payer'] == item]
                gr_filt = filtered_df.groupby(['User'])['STime'].sum()
                for item_filt in gr_filt.index:
                    user = item_filt
                    no_spectra = filtered_df[filtered_df['User'] == user]['STime'].count()
                    stime = gr_filt[item_filt]
                    td = datetime.timedelta(seconds=stime)
                    user_list = [user, '%d' % no_spectra, str(td), '%.2f' % stime]
                    payer_list.append(user_list)
                progress = (i + 1) / total_items * 50 + 50
                self.progress.emit(progress)
                self.return_row.emit(1, payer_list)


        except:
            import traceback
            self.error.emit(traceback.format_exc())
            print(traceback.format_exc())
            self.finished.emit(False)
        else:
            self.finished.emit(True)
            self.status.emit("Zakończono generowanie podsumowania.")

    def calculate_progress(self):
        if self.total_mails:
            self.processed = self.processed + 1
            percentage_new = (self.processed * 100) / self.total_mails
            if percentage_new > self.percentage:
                self.percentage = percentage_new
                self.progress.emit(self.percentage)

    def kill(self):
        self.status.emit('Sending aborted')
        self.abort = True

    progress = QtCore.pyqtSignal(int)
    status = QtCore.pyqtSignal(str)
    error = QtCore.pyqtSignal(str)
    killed = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal(bool)

    return_row = QtCore.pyqtSignal(bool, list)


class StatusControlWorker(QtCore.QObject):
    def __init__(self, MailSenderObj, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)

        self.sender = MailSenderObj
        self.abort = False
        self.interval = 150

        self.check_server()

    def start_status_control(self):
        while not self.abort:
            delta = datetime.datetime.now() - self.last_check
            if delta.total_seconds() > self.interval:
                self.check_server()
            time.sleep(1)
            self.status_info.emit(self.status_ans)
            time.sleep(0.5)
            self.status_info.emit((9, "Empty blink"))
        else:
            self.finished.emit(True)

    def check_server(self):
        print(datetime.datetime.now(), 'Checking server response status...')
        status_ans = self.sender.status()
        self.status_ans = status_ans
        print(status_ans)
        self.last_check = datetime.datetime.now()

    def kill(self):
        self.abort = True
        self.finished.emit(True)

    progress = QtCore.pyqtSignal(int)
    status = QtCore.pyqtSignal(str)
    error = QtCore.pyqtSignal(str)
    killed = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal(bool)
    status_info = QtCore.pyqtSignal(tuple)


class MailWorker(QtCore.QObject):
    def __init__(self, MailSenderObj, params=None, data=None, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)

        self.sender = MailSenderObj

        self.username = params['username']
        self.password = params['password']
        self.processed = 0
        self.successfull = 0
        self.percentage = 0

        if data:
            self.data = data
            self.total_mails = len(data)

        self.zip_dir = params['zip_dir']
        self.mail_from = params['mail_from']
        self.mail_topic = params['mail_topic']
        self.mail_text = params['mail_text']
        self.ans_to = params['mail_ans']
        self.abort = False
        self.log_dir = params['log_dir']

    def connect_to_server(self):
        self.status.emit('Connecting to SMTP server: ' + self.sender.server)
        ans = self.sender.connect()
        if ans[0]:
            self.status.emit('Connection to SMTP server established')
            self.finished.emit(True)
        else:
            self.status.emit('Cannot connect to SMTP server.')
            self.finished.emit(False)

    def login(self):
        self.status.emit('Authenticating user ' + self.username + '...')
        ans = self.sender.login(self.username, self.password)
        if ans[0]:
            self.status.emit('Logged in succesfully.')
            self.user_info.emit(self.username)
            self.finished.emit(True)
        else:
            self.status.emit('Login error - ' + ans[1])
            self.finished.emit(False)

    def send_all(self):
        self.status.emit('Sending in progress...')

    def send(self):
        try:
            self.status.emit('Sending in progress...')
            logfile = log.LogObject(self.log_dir)
            for item in self.data:
                item_no = item[0]
                if self.abort is True:
                    print('process aborted')
                    self.killed.emit()
                    self.status_info.emit(item_no, (0, 'Aborted'))
                    break
                ##zipping
                self.status.emit('Sending mail ' + '%d' % (self.processed + 1) +
                                 '/' + '%d' % (self.total_mails) + '. Preparing zip archive...')
                dir_path = item[1]
                zip_dir = self.zip_dir
                compressor = mail.Compressor(dir_path, zip_dir)
                ans = compressor.zip_spectrum()
                if ans[0]:
                    self.status_info.emit(item_no, (1, 'Archive created succesfully'))
                else:
                    self.status_info.emit(item_no, (0, ans[1]))
                ###sending

                if self.abort is True:
                    self.killed.emit()
                    self.status_info.emit(item_no, (0, 'Aborted'))
                    break
                self.status.emit('Sending mail ' + '%d' % (self.processed + 1) +
                                 '/' + '%d' % (self.total_mails) + '. Preparing mail message...')
                if ans[0]:
                    zip_path = ans[1]
                    spectrum_name = os.path.basename(dir_path)
                    mail_to = [item[3]]
                    mail_from = self.mail_from
                    mail_subj = self.mail_topic % {'name': spectrum_name}
                    mail_text = self.mail_text % {'name': spectrum_name}
                    ans_to = self.ans_to
                    self.status.emit('Sending mail ' + '%d' % (self.processed + 1) +
                                     '/' + '%d' % (self.total_mails) + '. Sending to ' + item[3] + '...')

                    ans_mail = self.sender.send(mail_to, mail_from, mail_subj, mail_text, [zip_path], ans_to)

                    if ans_mail[0]:
                        self.status_info.emit(item_no, (2, 'Sending completed'))
                        self.successfull = self.successfull + 1
                        logfile.add(spectrum_name, '', item[3], mail_from, self.username, 'Sent correctly')
                    else:
                        self.status_info.emit(item_no, (0, ans_mail[1]))

                self.calculate_progress()
                self.status.emit(
                    'Sending mail ' + '%d' % (self.processed) + '/' + '%d' % (self.total_mails) + ' completed')

        except:
            import traceback
            self.error.emit(traceback.format_exc())
            print(traceback.format_exc())
            self.finished.emit(False)
            logfile.save()
        else:
            self.finished.emit(True)
            self.status.emit(
                'Successfully sent ' + '%d' % (self.successfull) + ' out of ' + '%d' % (self.total_mails) + ' mails.')
            logfile.save()

    def calculate_progress(self):
        if self.total_mails:
            self.processed = self.processed + 1
            percentage_new = (self.processed * 100) / self.total_mails
            if percentage_new > self.percentage:
                self.percentage = percentage_new
                self.progress.emit(self.percentage)

    def kill(self):
        self.status.emit('Sending aborted')
        self.abort = True

    progress = QtCore.pyqtSignal(int)
    status = QtCore.pyqtSignal(str)
    error = QtCore.pyqtSignal(str)
    killed = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal(bool)
    status_info = QtCore.pyqtSignal(int, tuple)
    user_info = QtCore.pyqtSignal(str)


class Worker(QtCore.QObject):
    def __init__(self, path, date_from, date_to, found=1, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)
        self.path = path
        self.start = date_from
        self.end = date_to

        self.processed = 0
        self.percentage = 0
        self.found_files = found
        self.abort = False

    def count_files(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            self.status.emit('Trwa wyszukiwanie...')
            for subdir, dirs, files in os.walk(self.path):
                if self.abort is True:
                    self.killed.emit()
                    break
                for file in files:
                    if self.abort is True:
                        self.killed.emit()
                        break
                    if (file.lower() == 'fid' or file.lower() == 'ser'):
                        # print(os.path.join(subdir, file))
                        filetime = os.path.getmtime(os.path.join(subdir, file))
                        file_time = datetime.date.fromtimestamp(filetime)
                        if (file_time >= self.start and file_time <= self.end):
                            self.calculate_progress()
                            self.status.emit('Znalezionych widm: ' + '%d' % (self.processed))

            self.found_files = self.processed
            self.status.emit('Znalezionych widm: ' + '%d' % (self.found_files))
        except:
            import traceback
            self.error.emit(traceback.format_exc())
            self.finished.emit(False, self.found_files)
        else:
            self.finished.emit(True, self.found_files)
        QtWidgets.QApplication.restoreOverrideCursor()

    def analyze_files(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            self.status.emit('Trwa analizowanie plików...')
            for subdir, dirs, files in os.walk(self.path):
                if self.abort is True:
                    self.killed.emit()
                    break
                for file in files:
                    if self.abort is True:
                        self.killed.emit()
                        break
                    if (file.lower() == 'fid' or file.lower() == 'ser'):
                        filetime = os.path.getmtime(os.path.join(subdir, file))
                        file_time = datetime.date.fromtimestamp(filetime)
                        if (file_time >= self.start and file_time <= self.end):

                            spectrum_name = QtWidgets.QTableWidgetItem(subdir)
                            spectrum_time = QtWidgets.QTableWidgetItem(
                                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(filetime)))

                            row_list = [spectrum_name, spectrum_time]

                            spectrum = Spectrum(subdir)

                            brush = QtGui.QBrush(QtGui.QColor(213, 121, 0))
                            brush.setStyle(QtCore.Qt.NoBrush)

                            for j, item in enumerate(spectrum.get_values()):
                                tab_item = QtWidgets.QTableWidgetItem(item)
                                if item == '__undefined__':
                                    tab_item.setForeground(brush)
                                row_list.append(tab_item)

                            self.return_row.emit(row_list)
                            self.calculate_progress()
            self.status.emit('Zakończono.')
        except:
            import traceback
            self.error.emit(traceback.format_exc())
            self.finished.emit(False, self.found_files)
        else:
            self.finished.emit(True, self.found_files)

        QtWidgets.QApplication.restoreOverrideCursor()

    def calculate_progress(self):
        self.processed = self.processed + 1
        percentage_new = (self.processed * 100) / self.found_files
        if percentage_new > self.percentage:
            self.percentage = percentage_new
            self.progress.emit(self.percentage)

    def kill(self):
        self.abort = True

    progress = QtCore.pyqtSignal(int)
    status = QtCore.pyqtSignal(str)
    error = QtCore.pyqtSignal(str)
    killed = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal(bool, int)

    return_row = QtCore.pyqtSignal(list)


class MessageBox(QtWidgets.QDialog, message_box.Ui_Dialog):

    def __init__(self, parent=None):
        super(MessageBox, self).__init__(parent)
        self.setupUi(self)
        self.pushButton_2.clicked.connect(self.add)
        self.pushButton.clicked.connect(self.replace)

    def replace(self):
        self.ans = 1
        self.accept()

    def add(self):
        self.ans = 2
        self.accept()


class EditUsers(QtWidgets.QDialog, edit_users.Ui_Dialog):

    def __init__(self, parent=None):
        super(EditUsers, self).__init__(parent)
        self.setupUi(self)
        self.fill_table()
        self.set_enabled(False)

        self.tableWidget.cellDoubleClicked.connect(self.click_user)
        self.pushButton_3.clicked.connect(self.new_user)
        self.pushButton_4.clicked.connect(self.click_user)
        self.pushButton_2.clicked.connect(self.clear)
        self.pushButton.clicked.connect(self.save)
        self.pushButton_5.clicked.connect(self.delete_user)
        self.pushButton_6.clicked.connect(self.fill_table)
        self.find_query.textChanged.connect(self.fill_table)

        self.tableWidget.setColumnWidth(0, 50)

        self.comboBox.addItems(user_df['User'])
        self.comboBox.setCurrentIndex(-1)

    def fill_table(self):

        query = self.find_query.text()

        if query:
            udf = user_df[
                (user_df['User'].str.contains('(?i)' + query)) | (user_df['Patterns'].str.contains('(?i)' + query))]
        else:
            udf = user_df

        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(udf))
        self.tableWidget.setSortingEnabled(0)
        for i, item in enumerate(udf.index.tolist()):
            user = user_df.loc[item, 'User']
            payer_id = int(user_df.loc[item, 'PayID'])
            payer = user_df.loc[payer_id, 'User']
            pattern = user_df.loc[item, 'Patterns']
            mail = user_df.loc[item, 'Mail']

            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem('%d' % (item)))
            self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(user))
            self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(payer))
            self.tableWidget.setItem(i, 3, QtWidgets.QTableWidgetItem(pattern))
            self.tableWidget.setItem(i, 4, QtWidgets.QTableWidgetItem(mail))

        self.tableWidget.setSortingEnabled(1)

    def fill_combo(self):
        self.comboBox.clear()
        self.comboBox.addItems(user_df['User'])
        self.comboBox.setCurrentIndex(-1)

    def set_enabled(self, val):

        if val:
            self.lineEdit.setEnabled(True)
            self.lineEdit_2.setEnabled(True)
            self.lineEdit_3.setEnabled(True)
            self.comboBox.setEnabled(True)
            self.pushButton.setEnabled(True)
            self.pushButton_2.setEnabled(True)
        else:
            self.lineEdit.setEnabled(False)
            self.lineEdit_2.setEnabled(False)
            self.lineEdit_3.setEnabled(False)
            self.comboBox.setEnabled(False)
            self.pushButton.setEnabled(False)
            self.pushButton_2.setEnabled(False)

    def click_user(self):
        self.set_enabled(True)

        row = self.tableWidget.currentRow()
        curr_index = int(self.tableWidget.item(row, 0).text())

        self.label_num.setText('%d' % (curr_index))
        self.lineEdit.setText(user_df.loc[curr_index, 'User'])
        self.lineEdit_3.setText(user_df.loc[curr_index, 'Mail'])
        print(user_df.loc[curr_index, 'Patterns'])
        self.lineEdit_2.setText(user_df.loc[curr_index, 'Patterns'].replace('\r', ''))
        self.comboBox.setEditText(user_df.loc[int(user_df.loc[curr_index, 'PayID']), 'User'])

    def delete_user(self):
        row = self.tableWidget.currentRow()
        curr_index = int(self.tableWidget.item(row, 0).text())
        user_name = user_df.loc[curr_index, 'User']
        msg = 'Czy na pewno chcesz usunąć dane użytkownika "' + user_name + '"?'
        ans = QtWidgets.QMessageBox.question(self, 'Usuń', msg,
                                             QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if ans == QtWidgets.QMessageBox.Yes:
            user_df.drop([curr_index], inplace=True)
            user_df.sort_values(by=['User'], inplace=True)
            user_df.to_csv('users.csv', sep=';', index_label='ID', encoding='utf8')

            self.fill_table()
            self.fill_combo()

    def new_user(self):
        self.set_enabled(True)
        if not user_df.empty:
            new_index = max(user_df.index.tolist()) + 1
        else:
            new_index = 0
        self.label_num.setText('%d' % (new_index))
        self.lineEdit.setText('')
        self.lineEdit_2.setText('')
        self.lineEdit_3.setText('')
        self.comboBox.setCurrentIndex(-1)

    def clear(self):
        self.label_num.setText('')
        self.lineEdit.setText('')
        self.lineEdit_2.setText('')
        self.lineEdit_3.setText('')
        self.comboBox.setCurrentIndex(-1)
        self.set_enabled(False)

    def save(self):
        index = int(self.label_num.text())
        user_text = unidecode.unidecode(self.lineEdit.text())
        patterns = unidecode.unidecode(self.lineEdit_2.toPlainText())
        mail = self.lineEdit_3.text()
        if (user_text == '' or patterns == ''):
            msg_box = QtWidgets.QMessageBox.critical(self, 'Błąd', 'Uzupełnij brakujące dane!',
                                                     QtWidgets.QMessageBox.Ok)
            return
        else:
            match_user = user_df[user_df['User'] == user_text]

            if not match_user.empty:
                user_ind = match_user.index.tolist()[0]
                if user_ind != index:
                    msg_text = 'Nazwa użytkownika "' + user_text + '" jest już przypisana. Wybierz inną nazwę.'
                    msg_box = QtWidgets.QMessageBox.critical(self, 'Błąd', msg_text,
                                                             QtWidgets.QMessageBox.Ok)
                    return

            patterns_list = patterns.split('\n')
            for item in patterns_list:
                find_pattern = Spectrum.find_pattern(item)

                if find_pattern:
                    if find_pattern != index:
                        found_user = user_df.loc[find_pattern, 'User']
                        msg_text = 'Wzorzec "' + item + '" jest już przypisany do użytkownika: ' + '%d' % find_pattern + ' ' + found_user + '. Wybierz inną nazwę.'
                        msg_box = QtWidgets.QMessageBox.critical(self, 'Błąd', msg_text,
                                                                 QtWidgets.QMessageBox.Ok)
                        return

        payer_text = self.comboBox.currentText()
        if payer_text == '':
            payer_id = index
        else:
            match_df = user_df[user_df['User'] == payer_text]
            if not match_df.empty:
                payer_id = int(match_df.index.tolist()[0])
            else:
                msg_box = QtWidgets.QMessageBox.critical(self, 'Błąd',
                                                         'Dane w polu "Płatnik" nie pasują do żadnego użytkownika!',
                                                         QtWidgets.QMessageBox.Ok)
                return

        user_df.loc[index, 'User'] = user_text
        user_df.loc[index, 'Patterns'] = patterns
        user_df.loc[index, 'PayID'] = int(payer_id)
        user_df.loc[index, 'Mail'] = mail

        user_df.sort_values(by=['User'], inplace=True)
        user_df.to_csv('users.csv', sep=';', index_label='ID', encoding='utf8')

        self.fill_table()
        self.fill_combo()
        self.clear()


class Summary(QtWidgets.QDialog, summary.Ui_Dialog):

    def __init__(self, parent=None):
        super(Summary, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.bill)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Save).clicked.connect(self.export)
        self.doubleSpinBox.editingFinished.connect(self.bill)

    def fill_table(self, df):
        print(df)
        self.tableWidget.setRowCount(len(df))
        for i, item in enumerate(df.index):
            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(item))
            sec = df[item]
            td = datetime.timedelta(seconds=sec)
            self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(str(td)))
            self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem('%d' % sec))

    def bill(self):
        fee = float(self.doubleSpinBox.value())

        i = 0
        self.tableWidget.setSortingEnabled(False)
        rows = self.tableWidget.rowCount()

        for i in range(rows):
            user_item = self.tableWidget.item(i, 2)
            if user_item:
                times = float(user_item.text())
                cost = times * fee / 3600
                self.tableWidget.setItem(i, 3, QtWidgets.QTableWidgetItem('%.2f' % cost))

    def export(self):
        cwd = os.getcwd()
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, 'Exportuj', cwd,
                                                         'Comma-separated .csv (*.csv);; MS Excel .xls (*.xls)')[0]
        if fileName:
            df = self.read_df()
            if (fileName.endswith('.csv') or fileName.endswith('.CSV')):
                df.to_csv(fileName, sep=',', index_label='ID')
            elif (fileName.endswith('.xls') or fileName.endswith('.XLS')):
                df.to_excel(fileName)

    def read_df(self):
        rows = self.tableWidget.rowCount()
        cols = self.tableWidget.columnCount()

        full_df = DataFrame(columns=['Payer', 'Time', 'TimeS', 'Cost'], index=range(rows))

        for i in range(rows):
            for j in range(cols):
                item = self.tableWidget.item(i, j)
                if item:
                    full_df.iloc[i, j] = item.text()
                else:
                    full_df.iloc[i, j] = ''

        return full_df


class Login(QtWidgets.QDialog, login.Ui_Dialog):

    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.setupUi(self)


class OptionsDialog(QtWidgets.QDialog, options.Ui_Dialog):

    def __init__(self, parent=None):
        super(OptionsDialog, self).__init__(parent)
        self.setupUi(self)

        self.choose_main.clicked.connect(lambda: self.choose_dir(self.main_dir))
        self.choose_zip.clicked.connect(lambda: self.choose_dir(self.zip_dir))
        self.choose_log.clicked.connect(lambda: self.choose_dir(self.log_dir))
        self.choose_spectr_dir.clicked.connect(lambda: self.choose_dir(self.spectra_dir))
        self.choose_report_dir.clicked.connect(lambda: self.choose_dir(self.report_dir))

    def choose_dir(self, input_widget):
        destDir = None
        destDir = QtWidgets.QFileDialog.getExistingDirectory(None,
                                                             'Choose directory',
                                                             os.getcwd(),
                                                             QtWidgets.QFileDialog.ShowDirsOnly)
        if destDir:
            input_widget.setText(destDir)


class Spectrum(object):

    def __init__(self, path):
        self.path = path
        self.exp_type = ""
        self.ns = 0
        self.td1 = 0
        self.td2 = 0
        self.msg = ""
        self.user_text = ''
        self.user = ''
        self.payer = ''
        self.start_time = None
        self.end_time = None
        self.analyze()

    def find_pattern(text):
        # user_match=user_df[user_df['Patterns'].str.lower()==text.lower()]
        # if user_match.empty():
        user_match = user_df[user_df['Patterns'].str.contains(text, case=False, regex=False)]
        if not user_match.empty:
            ids_list = user_match.index.tolist()
            matched_id = None
            for item in ids_list:
                pattern = user_df.loc[item, 'Patterns']
                patt_list = pattern.split('\n')
                for pat_item in patt_list:
                    if pat_item.strip().lower() == text.lower():
                        matched_id = item
                        break
                if matched_id:
                    break
            return matched_id
        else:
            return None

    def find_user(text):
        user_id = Spectrum.find_pattern(text)
        if user_id:
            user = user_df.loc[user_id, 'User']
            payer_id = int(user_df.loc[user_id, 'PayID'])
            payer = user_df.loc[payer_id, 'User']
            mail = user_df.loc[user_id, 'Mail']
        else:
            user = '__undefined__'
            payer = '__undefined__'
            mail = '__undefined__'

        return (user, payer, mail)

    def get_values(self):

        times = self.get_times()

        return [self.user_text, '', '', times['start'], times['end'],
                times['duration'], str(times['dur_s']), self.exp_type, self.ns, self.td1, self.td2]

    def get_times(self):

        if self.start_time:
            start = datetime.datetime.strftime(self.start_time, '%Y-%m-%d %H:%M:%S %z')
        else:
            start = '__undefined__'

        if self.end_time:
            end = datetime.datetime.strftime(self.end_time, '%Y-%m-%d %H:%M:%S %z')
        else:
            end = '__undefined__'

        if (self.start_time and self.end_time):
            self.duration = self.end_time - self.start_time
            duration = str(self.duration)
            dur_s = self.duration.total_seconds()
        else:
            duration = '__undefined__'
            dur_s = 0

        return {'start': start, 'end': end, 'duration': duration, 'dur_s': dur_s}

    def analyze(self):

        sample_full_name = os.path.split(self.path)[0]
        sample_name = os.path.split(sample_full_name)[1]
        splits = ['.', '-', '_', ' ']
        new_name = sample_name
        for item in splits:
            new_name = new_name.split(item)[0]
        user_text = new_name

        self.user_text = user_text

        try:
            acqus = os.path.join(self.path, 'acqus')
            acqus_file = open(acqus, 'r')
        except FileNotFoundError:
            try:
                acqus = os.path.join(self.path, 'ACQUS')
                acqus_file = open(acqus, 'r')
            except:
                pass

        try:
            for line in acqus_file:
                if "$EXP=" in line:
                    matchObj = re.search(r'##\$EXP= (.*)', line)
                    if matchObj:
                        exp_type = matchObj.group(1)
                        self.exp_type = exp_type
                if "$NS=" in line:
                    matchObj = re.search(r'##\$NS= (.*)', line)
                    if matchObj:
                        ns = matchObj.group(1)
                        self.ns = ns
                if "$TD=" in line:
                    matchObj = re.search(r'##\$TD= (.*)', line)
                    if matchObj:
                        td = matchObj.group(1)
                        self.td1 = td
        except:
            self.ns = '__undefined__'

        try:
            acqus2 = os.path.join(self.path, 'acqu2s')
            acqus2_file = open(acqus2, 'r')
        except FileNotFoundError:
            try:
                acqus2 = os.path.join(self.path, 'ACQU2S')
                acqus2_file = open(acqus2, 'r')
            except:
                pass

        try:
            for line in acqus2_file:
                if "$TD=" in line:
                    matchObj = re.search(r'##\$TD= (.*)', line)
                    if matchObj:
                        td = matchObj.group(1)
                        self.td2 = td
        except:
            pass

        try:
            audita = os.path.join(self.path, 'audita.txt')
            audita_file = open(audita, 'r')
        except FileNotFoundError:
            try:
                audita = os.path.join(self.path, 'AUDITA.TXT')
                audita_file = open(audita, 'r')
            except:
                pass

        try:
            audita_text = audita_file.read().replace('\n', '')
            audit_list = audita_text.split('##')
            for item in audit_list:
                if "AUDIT TRAIL=" in item:
                    values = item.split(')(')[1]
                    values_list = values.split(',')
                    finished = values_list[1][1:-1]
                    started = values_list[6]
                    try:
                        end_time = datetime.datetime.strptime(finished, '%Y-%m-%d %H:%M:%S.%f %z')
                        self.end_time = end_time
                    except:
                        end_time = None
                    try:
                        start_time_str = started.split('started at')[1].strip()
                        start_time = datetime.datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S.%f %z')
                        self.start_time = start_time
                    except:
                        try:
                            acqu = os.path.join(self.path, 'acqu')
                            acqu_file = open(acqu, 'r')
                        except FileNotFoundError:
                            try:
                                acqu = os.path.join(self.path, 'ACQU')
                                acqu_file = open(acqu, 'r')
                            except:
                                pass

                        for line in acqu_file:
                            if line.startswith("$$"):
                                start_time1 = dparser.parse(line, fuzzy=True)
                                break

                        acqu_file.close()

                        try:
                            pulse = os.path.join(self.path, 'pulseprogram')
                            pulse_file = open(pulse, 'r')
                        except FileNotFoundError:
                            try:
                                pulse = os.path.join(self.path, 'PULSEPROGRAM')
                                pulse_file = open(pulse, 'r')
                            except:
                                pass
                        pulse_file.close()

                        auditatime = os.path.getmtime(audita)
                        audita_time = datetime.datetime.fromtimestamp(auditatime)
                        end_time2 = audita_time

                        pulsetime = os.path.getmtime(pulse)
                        pulse_time = datetime.datetime.fromtimestamp(pulsetime)
                        start_time2 = pulse_time

                        dif1 = self.end_time - start_time1
                        dif2 = end_time2 - start_time2
                        if dif1 == abs(dif1):
                            self.start_time = start_time1
                        elif dif2 == abs(dif2):
                            self.start_time = start_time2
                            self.end_time = end_time2
                        else:
                            self.start_time = None

        except:
            pass


def excepthookA(excType, excValue, tracebackobj):
    """
    Global function to catch unhandled exceptions.
    
    @param excType exception type
    @param excValue exception value
    @param tracebackobj traceback object
    """

    separator = '-' * 40
    logFile = "errors.log"
    notice = "An unhandled exception occurred.\n"
    versionInfo = "2.0"
    timeString = time.strftime("%Y-%m-%d, %H:%M:%S")

    errmsg = '%s: \n%s' % (str(excType), str(excValue))
    sections = [timeString, separator, errmsg, separator]
    msg = '\n'.join(sections)
    try:
        f = open(logFile, "a")
        f.write(msg)
        f.write(versionInfo)
        f.close()
    except IOError:
        pass
    errorbox = QtWidgets.QMessageBox()
    errorbox.setText(str(notice) + str(msg))
    errorbox.exec_()


sys.excepthook = excepthookA


def main():
    app = QtWidgets.QApplication(sys.argv)

    # # Create and display the splash screen
    # splash_pix = QtGui.QPixmap('icons/pdf.png')
    # splash = QtWidgets.QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
    # splash.setMask(splash_pix.mask())
    # splash.show()
    #
    # # create elapse timer to cal time
    # timer = QtCore.QElapsedTimer()
    # timer.start()
    # # we give 3 secs
    # while timer.elapsed() < 3000:
    #     app.processEvents()
    # #app.processEvents()
    #
    # # qt_translator = QtCore.QTranslator()
    # qt_translator.load("qt_pl",QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
    # app.installTranslator(qt_translator)
    print(QtWidgets.QStyleFactory.keys())
    # app.setStyle(QtWidgets.QStyleFactory.create('Breeze'))

    form = App()
    form.show()
    # splash.finish(form)
    app.exec_()


if __name__ == '__main__':
    main()
