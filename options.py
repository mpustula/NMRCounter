# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'options.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(715, 642)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(Dialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.scrollArea = QtWidgets.QScrollArea(self.tab)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 679, 535))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox = QtWidgets.QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.mail_ans = QtWidgets.QLineEdit(self.groupBox)
        self.mail_ans.setObjectName("mail_ans")
        self.gridLayout.addWidget(self.mail_ans, 10, 1, 1, 2)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.groupBox)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 10, 0, 1, 1)
        self.port = QtWidgets.QSpinBox(self.groupBox)
        self.port.setMaximum(999999)
        self.port.setObjectName("port")
        self.gridLayout.addWidget(self.port, 1, 1, 1, 1)
        self.mail_from = QtWidgets.QLineEdit(self.groupBox)
        self.mail_from.setObjectName("mail_from")
        self.gridLayout.addWidget(self.mail_from, 9, 1, 1, 2)
        self.label_11 = QtWidgets.QLabel(self.groupBox)
        self.label_11.setObjectName("label_11")
        self.gridLayout.addWidget(self.label_11, 11, 0, 1, 1)
        self.server = QtWidgets.QLineEdit(self.groupBox)
        self.server.setObjectName("server")
        self.gridLayout.addWidget(self.server, 0, 1, 1, 2)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 3)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 5, 0, 1, 1)
        self.username = QtWidgets.QLineEdit(self.groupBox)
        self.username.setObjectName("username")
        self.gridLayout.addWidget(self.username, 5, 1, 1, 2)
        self.password = QtWidgets.QLineEdit(self.groupBox)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setObjectName("password")
        self.gridLayout.addWidget(self.password, 6, 1, 1, 2)
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 6, 0, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.groupBox)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 8, 0, 1, 3)
        self.mail_topic = QtWidgets.QLineEdit(self.groupBox)
        self.mail_topic.setObjectName("mail_topic")
        self.gridLayout.addWidget(self.mail_topic, 11, 1, 1, 2)
        self.label_9 = QtWidgets.QLabel(self.groupBox)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 9, 0, 1, 1)
        self.mail_text = QtWidgets.QTextEdit(self.groupBox)
        self.mail_text.setObjectName("mail_text")
        self.gridLayout.addWidget(self.mail_text, 12, 1, 1, 2)
        self.label_12 = QtWidgets.QLabel(self.groupBox)
        self.label_12.setObjectName("label_12")
        self.gridLayout.addWidget(self.label_12, 12, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.groupBox)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 7, 0, 1, 3)
        self.label_13 = QtWidgets.QLabel(self.groupBox)
        self.label_13.setObjectName("label_13")
        self.gridLayout.addWidget(self.label_13, 2, 0, 1, 1)
        self.timeout = QtWidgets.QSpinBox(self.groupBox)
        self.timeout.setMaximum(6000000)
        self.timeout.setProperty("value", 30)
        self.timeout.setObjectName("timeout")
        self.gridLayout.addWidget(self.timeout, 2, 1, 1, 1)
        self.label_14 = QtWidgets.QLabel(self.groupBox)
        self.label_14.setObjectName("label_14")
        self.gridLayout.addWidget(self.label_14, 2, 2, 1, 1)
        self.line = QtWidgets.QFrame(self.groupBox)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 3, 0, 1, 3)
        self.verticalLayout_4.addLayout(self.gridLayout)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.tab_2)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.scrollArea_2 = QtWidgets.QScrollArea(self.tab_2)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 679, 535))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.groupBox_3 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_16 = QtWidgets.QLabel(self.groupBox_3)
        self.label_16.setObjectName("label_16")
        self.gridLayout_3.addWidget(self.label_16, 0, 0, 1, 1)
        self.label_17 = QtWidgets.QLabel(self.groupBox_3)
        self.label_17.setObjectName("label_17")
        self.gridLayout_3.addWidget(self.label_17, 1, 0, 1, 1)
        self.spectra_dir = QtWidgets.QLineEdit(self.groupBox_3)
        self.spectra_dir.setObjectName("spectra_dir")
        self.gridLayout_3.addWidget(self.spectra_dir, 1, 1, 1, 1)
        self.choose_spectr_dir = QtWidgets.QPushButton(self.groupBox_3)
        self.choose_spectr_dir.setObjectName("choose_spectr_dir")
        self.gridLayout_3.addWidget(self.choose_spectr_dir, 1, 2, 1, 1)
        self.price = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.price.setObjectName("price")
        self.gridLayout_3.addWidget(self.price, 0, 1, 1, 2)
        self.label_18 = QtWidgets.QLabel(self.groupBox_3)
        self.label_18.setObjectName("label_18")
        self.gridLayout_3.addWidget(self.label_18, 2, 0, 1, 1)
        self.report_dir = QtWidgets.QLineEdit(self.groupBox_3)
        self.report_dir.setObjectName("report_dir")
        self.gridLayout_3.addWidget(self.report_dir, 2, 1, 1, 1)
        self.choose_report_dir = QtWidgets.QPushButton(self.groupBox_3)
        self.choose_report_dir.setObjectName("choose_report_dir")
        self.gridLayout_3.addWidget(self.choose_report_dir, 2, 2, 1, 1)
        self.verticalLayout_6.addWidget(self.groupBox_3)
        self.groupBox_2 = QtWidgets.QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.choose_log = QtWidgets.QPushButton(self.groupBox_2)
        self.choose_log.setObjectName("choose_log")
        self.gridLayout_2.addWidget(self.choose_log, 3, 2, 1, 1)
        self.zip_dir = QtWidgets.QLineEdit(self.groupBox_2)
        self.zip_dir.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.zip_dir.setObjectName("zip_dir")
        self.gridLayout_2.addWidget(self.zip_dir, 2, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.groupBox_2)
        self.label_7.setObjectName("label_7")
        self.gridLayout_2.addWidget(self.label_7, 2, 0, 1, 1)
        self.main_dir = QtWidgets.QLineEdit(self.groupBox_2)
        self.main_dir.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.main_dir.setObjectName("main_dir")
        self.gridLayout_2.addWidget(self.main_dir, 0, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)
        self.choose_main = QtWidgets.QPushButton(self.groupBox_2)
        self.choose_main.setObjectName("choose_main")
        self.gridLayout_2.addWidget(self.choose_main, 0, 2, 1, 1)
        self.choose_zip = QtWidgets.QPushButton(self.groupBox_2)
        self.choose_zip.setObjectName("choose_zip")
        self.gridLayout_2.addWidget(self.choose_zip, 2, 2, 1, 1)
        self.label_15 = QtWidgets.QLabel(self.groupBox_2)
        self.label_15.setObjectName("label_15")
        self.gridLayout_2.addWidget(self.label_15, 3, 0, 1, 1)
        self.log_dir = QtWidgets.QLineEdit(self.groupBox_2)
        self.log_dir.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.log_dir.setObjectName("log_dir")
        self.gridLayout_2.addWidget(self.log_dir, 3, 1, 1, 1)
        self.verticalLayout_6.addWidget(self.groupBox_2)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.verticalLayout_5.addWidget(self.scrollArea_2)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.tab_3)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.nadplata = QtWidgets.QLineEdit(self.tab_3)
        self.nadplata.setObjectName("nadplata")
        self.gridLayout_4.addWidget(self.nadplata, 3, 1, 1, 1)
        self.label_21 = QtWidgets.QLabel(self.tab_3)
        self.label_21.setObjectName("label_21")
        self.gridLayout_4.addWidget(self.label_21, 3, 0, 1, 1)
        self.saldo = QtWidgets.QLineEdit(self.tab_3)
        self.saldo.setObjectName("saldo")
        self.gridLayout_4.addWidget(self.saldo, 2, 1, 1, 1)
        self.label_19 = QtWidgets.QLabel(self.tab_3)
        self.label_19.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_19.setObjectName("label_19")
        self.gridLayout_4.addWidget(self.label_19, 0, 0, 1, 1)
        self.label_20 = QtWidgets.QLabel(self.tab_3)
        self.label_20.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_20.setObjectName("label_20")
        self.gridLayout_4.addWidget(self.label_20, 6, 0, 1, 1)
        self.notification_text = QtWidgets.QTextEdit(self.tab_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(4)
        sizePolicy.setHeightForWidth(self.notification_text.sizePolicy().hasHeightForWidth())
        self.notification_text.setSizePolicy(sizePolicy)
        self.notification_text.setObjectName("notification_text")
        self.gridLayout_4.addWidget(self.notification_text, 0, 1, 1, 1)
        self.label_22 = QtWidgets.QLabel(self.tab_3)
        self.label_22.setObjectName("label_22")
        self.gridLayout_4.addWidget(self.label_22, 4, 0, 1, 1)
        self.notification_emails = QtWidgets.QTextEdit(self.tab_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.notification_emails.sizePolicy().hasHeightForWidth())
        self.notification_emails.setSizePolicy(sizePolicy)
        self.notification_emails.setObjectName("notification_emails")
        self.gridLayout_4.addWidget(self.notification_emails, 6, 1, 1, 1)
        self.niedoplata = QtWidgets.QLineEdit(self.tab_3)
        self.niedoplata.setObjectName("niedoplata")
        self.gridLayout_4.addWidget(self.niedoplata, 4, 1, 1, 1)
        self.label_24 = QtWidgets.QLabel(self.tab_3)
        self.label_24.setObjectName("label_24")
        self.gridLayout_4.addWidget(self.label_24, 2, 0, 1, 1)
        self.brak_naleznosci = QtWidgets.QLineEdit(self.tab_3)
        self.brak_naleznosci.setObjectName("brak_naleznosci")
        self.gridLayout_4.addWidget(self.brak_naleznosci, 1, 1, 1, 1)
        self.label_23 = QtWidgets.QLabel(self.tab_3)
        self.label_23.setObjectName("label_23")
        self.gridLayout_4.addWidget(self.label_23, 1, 0, 1, 1)
        self.verticalLayout_7.addLayout(self.gridLayout_4)
        self.tabWidget.addTab(self.tab_3, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(2)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.tabWidget, self.scrollArea)
        Dialog.setTabOrder(self.scrollArea, self.server)
        Dialog.setTabOrder(self.server, self.port)
        Dialog.setTabOrder(self.port, self.username)
        Dialog.setTabOrder(self.username, self.password)
        Dialog.setTabOrder(self.password, self.mail_from)
        Dialog.setTabOrder(self.mail_from, self.mail_ans)
        Dialog.setTabOrder(self.mail_ans, self.mail_topic)
        Dialog.setTabOrder(self.mail_topic, self.mail_text)
        Dialog.setTabOrder(self.mail_text, self.scrollArea_2)
        Dialog.setTabOrder(self.scrollArea_2, self.zip_dir)
        Dialog.setTabOrder(self.zip_dir, self.main_dir)
        Dialog.setTabOrder(self.main_dir, self.choose_main)
        Dialog.setTabOrder(self.choose_main, self.choose_zip)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Preferences"))
        self.groupBox.setTitle(_translate("Dialog", "SMTP server settings"))
        self.label.setText(_translate("Dialog", "Server:"))
        self.label_2.setText(_translate("Dialog", "Port:"))
        self.label_10.setText(_translate("Dialog", "Answer to:"))
        self.label_11.setText(_translate("Dialog", "Topic:"))
        self.label_4.setText(_translate("Dialog", "Authentication"))
        self.label_5.setText(_translate("Dialog", "Username:"))
        self.label_6.setText(_translate("Dialog", "Password:"))
        self.label_8.setText(_translate("Dialog", "Message options"))
        self.label_9.setText(_translate("Dialog", "From:"))
        self.label_12.setText(_translate("Dialog", "Text:"))
        self.label_13.setText(_translate("Dialog", "Timeout:"))
        self.label_14.setText(_translate("Dialog", "s"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Dialog", "Mail"))
        self.groupBox_3.setTitle(_translate("Dialog", "Payments:"))
        self.label_16.setText(_translate("Dialog", "Price per hour [PLN]:"))
        self.label_17.setText(_translate("Dialog", "Default spectra directory:"))
        self.choose_spectr_dir.setText(_translate("Dialog", "Choose"))
        self.label_18.setText(_translate("Dialog", "Default reports directory:"))
        self.choose_report_dir.setText(_translate("Dialog", "Choose"))
        self.groupBox_2.setTitle(_translate("Dialog", "Mail module folders:"))
        self.choose_log.setText(_translate("Dialog", "Choose"))
        self.label_7.setText(_translate("Dialog", "Zipped:"))
        self.label_3.setText(_translate("Dialog", "Main:"))
        self.choose_main.setText(_translate("Dialog", "Choose"))
        self.choose_zip.setText(_translate("Dialog", "Choose"))
        self.label_15.setText(_translate("Dialog", "Log file:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Dialog", "General"))
        self.label_21.setText(_translate("Dialog", "Text when >0"))
        self.label_19.setText(_translate("Dialog", "Notification text:"))
        self.label_20.setText(_translate("Dialog", "Default emails:"))
        self.label_22.setText(_translate("Dialog", "Text when <0"))
        self.label_24.setText(_translate("Dialog", "Saldo"))
        self.label_23.setText(_translate("Dialog", "Text when =0"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("Dialog", "Notifications"))

