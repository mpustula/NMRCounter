# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 17:04:57 2018

@author: marcin
"""
import sys
import os.path
import time, datetime
import dateutil.parser as dparser
import re
from pandas import read_csv, DataFrame

from PyQt5 import QtCore, QtGui, QtWidgets

import mainwindow, edit_users, summary, message_box

user_df=read_csv('users.csv',sep=';',index_col='ID')
user_df.sort_values(by=['User'],inplace=True)

class App(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
    
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setupUi(self)
        self.chooseDir.clicked.connect(self.choose_dir)
        self.analyze_button.clicked.connect(self.analyze_files)
        self.find_button.clicked.connect(self.count_files)
        self.users_button.clicked.connect(self.analyze_users)
        self.edit_list_button.clicked.connect(self.edit_users)
        self.del_button.clicked.connect(self.clear_table)
        self.pushButton.clicked.connect(self.group_df)
        self.actionDo_CSV.triggered.connect(self.export_csv)
        self.actionDo_XLS.triggered.connect(self.export_xls)
        self.actionImportuj.triggered.connect(self.import_csv)
        self.found_files=1
        
        self.stop_button.hide()
        
        self.tableWidget.setColumnWidth(0,600)
        self.tableWidget.setColumnWidth(1,200)
        self.tableWidget.setColumnWidth(2,150)
        self.tableWidget.setColumnWidth(3,300)
        self.tableWidget.setColumnWidth(4,300)
        self.tableWidget.setColumnWidth(5,200)
        self.tableWidget.setColumnWidth(6,200)
        self.tableWidget.setColumnWidth(7,100)
        self.tableWidget.setColumnWidth(8,100)
        self.tableWidget.setColumnWidth(9,200)
        self.tableWidget.setColumnWidth(10,100)
        self.tableWidget.setColumnWidth(11,100)
        self.tableWidget.setColumnWidth(12,100)
        
        curr_date=QtCore.QDate.currentDate()
        self.dateEdit_2.setDate(curr_date)
        year=curr_date.year()
        begin_date=QtCore.QDate(year,1,1)
        self.dateEdit.setDate(begin_date)
        
        
    def export_csv(self):
        cwd=os.getcwd()
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, 'Exportuj', cwd, 'CSV (*.csv)')[0]
        if fileName:
            df=self.read_df()
            df.to_csv(fileName,sep=',',index_label='ID')
    
    def export_xls(self):
        cwd=os.getcwd()
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, 'Exportuj', cwd, 'XLS (*.xls)')[0]
        if fileName:
            df=self.read_df()
            df.to_excel(fileName)
            
    def import_csv(self):
        cwd=os.getcwd()
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Otwórz plik', cwd, 'CSV (*.csv)')[0]
        if fileName:
            imported_df=read_csv(fileName,sep=',',index_col='ID')
            rows=self.tableWidget.rowCount()
            if rows>0:
                msg_box=MessageBox(self)
                ans=msg_box.exec_()
                if ans:
                    ans2=msg_box.ans
                    if ans2==1:
                        self.tableWidget.clearContents()
                        self.tableWidget.setRowCount(0)
                    self.fill_from_df(imported_df)
            else:
                self.fill_from_df(imported_df)
                    
    def fill_from_df(self,df):
        brush = QtGui.QBrush(QtGui.QColor(213, 121, 0))
        brush.setStyle(QtCore.Qt.NoBrush)
        df=df.fillna('')
        for i, item in enumerate(df.index.tolist()):
            self.tableWidget.insertRow(i)
            for j, column in enumerate(df):
                #print(column)
                item_text=str(df[column][item])
                print(item_text)
                tab_item=QtWidgets.QTableWidgetItem(item_text)
                if item_text=='__undefined__':
                    tab_item.setForeground(brush)
                self.tableWidget.setItem(i,j,tab_item)
                
    
    def group_df(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        full_df=self.read_df()
        full_df['STime']=full_df['STime'].map(float)
        
        grouped_df=full_df.groupby(['Payer'])['STime'].sum()
        QtWidgets.QApplication.restoreOverrideCursor()
        summary=Summary(self)
        summary.fill_table(grouped_df)
        summary.show()
        
    def read_df(self):
        rows=self.tableWidget.rowCount()
        cols=self.tableWidget.columnCount()
        
        full_df=DataFrame(columns=['Spectrum','Date','Username','User','Payer',
                                   'Start','End','Time','STime','EXP','NS','TD1','TD2'], index=range(rows))
                                   
        
        
        for i in range(rows):
            for j in range(cols):
                item=self.tableWidget.item(i,j)
                if item:
                    full_df.iloc[i,j]=item.text()
                else:
                    full_df.iloc[i,j]=''
                    
        full_df.to_csv('temp/temp.csv',sep=';')
        return full_df
    
    
    def edit_users(self):
        
        users_dialog=EditUsers(self)
        users_dialog.show()       
        
    def clear_table(self):
        msg='Czy na pewno chcesz usunąć wszystkie dane?'
        ans=QtWidgets.QMessageBox.question(self, 'Wyczyść', msg, 
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if ans == QtWidgets.QMessageBox.Yes:
            self.tableWidget.clearContents()
            self.tableWidget.setRowCount(0)
        
    def choose_dir(self):
        
        destDir = QtWidgets.QFileDialog.getExistingDirectory(None, 
                                                         'Wybierz folder do przeanalizowania', 
                                                         os.getcwd(), 
                                                         QtWidgets.QFileDialog.ShowDirsOnly)

        self.dest_dir.setText(destDir)
    
    def set_dates(self):
        self.start=self.dateEdit.date().toPyDate()
        self.end=self.dateEdit_2.date().toPyDate()
        
        #print(self.start,self.end)
        
    def set_found(self,status,num):
        self.found=num
        self.stop_button.hide()
        self.label_found.setText("Znalezionych widm: "+'%d'%self.found)
    
    def count_files(self):
        rootdir=self.dest_dir.text()
        self.set_dates()
        self.stop_button.show()
        
        thread=QtCore.QThread(self)
        worker=self.worker=Worker(rootdir,self.start,self.end)
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
        
    def insert_row(self,row_list):
        rows=self.tableWidget.rowCount()
        self.tableWidget.insertRow(rows)
        for j, item in enumerate(row_list):
            self.tableWidget.setItem(rows,j,item)
        
    def analyze_files(self):
        self.tableWidget.setSortingEnabled(False)
        rootdir=self.dest_dir.text()
        self.set_dates()
        self.stop_button.show()
        
        thread=QtCore.QThread(self)
        worker=self.worker=Worker(rootdir,self.start,self.end,self.found)
        
        
        worker.moveToThread(thread)
        self.stop_button.clicked.connect(self.worker.kill)
        thread.started.connect(worker.analyze_files)
        worker.progress.connect(self.progressBar.setValue)
        worker.status.connect(self.statusbar.showMessage)
        
        #worker.finished.connect(self.set_found)
        worker.return_row.connect(self.insert_row)
        worker.finished.connect(self.an_finished)
        worker.killed.connect(self.an_finished)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        worker.finished.connect(thread.quit)
        thread.start()
        
    def analyze_users(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        i=0
        self.tableWidget.setSortingEnabled(False)
        rows=self.tableWidget.rowCount()
        
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.NoBrush)

        for i in range(rows):
            user_item=self.tableWidget.item(i,2)
            #self.tableWidget.setItem(i,3,QtWidgets.QTableWidgetItem(''))
            #self.tableWidget.setItem(i,4,QtWidgets.QTableWidgetItem(''))
            if user_item:
                user_text=user_item.text()
            else:
                user_text=''
                
            result=Spectrum.find_user(user_text)
            
            for j, item in enumerate(result):
                tab_item=QtWidgets.QTableWidgetItem(item)
                if item=='__undefined__':
                    tab_item.setForeground(brush)
                self.tableWidget.setItem(i,j+3,tab_item)
                
            i=i+1
            progress=i/rows
            self.progressBar.setValue(progress*100)
        self.tableWidget.setSortingEnabled(True)
        QtWidgets.QApplication.restoreOverrideCursor()


class Worker(QtCore.QObject):
    def __init__(self, path, date_from, date_to, found=1, *args, **kwargs):
        QtCore.QObject.__init__(self, *args, **kwargs)
        self.path = path
        self.start = date_from
        self.end = date_to

        self.processed = 0
        self.percentage = 0
        self.found_files=found
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
                    if (file.lower()=='fid' or file.lower()=='ser'):
                        #print(os.path.join(subdir, file))
                        filetime=os.path.getmtime(os.path.join(subdir,file))
                        file_time=datetime.date.fromtimestamp(filetime)
                        if (file_time>=self.start and file_time<=self.end):
                            self.calculate_progress()
                            self.status.emit('Znalezionych widm: '+'%d'%(self.processed))
            
            self.found_files=self.processed
            self.status.emit('Znalezionych widm: '+'%d'%(self.found_files))
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
                    if (file.lower()=='fid' or file.lower()=='ser'):
                        filetime=os.path.getmtime(os.path.join(subdir,file))
                        file_time=datetime.date.fromtimestamp(filetime)
                        if (file_time>=self.start and file_time<=self.end):
                        
                            
                            spectrum_name=QtWidgets.QTableWidgetItem(subdir)
                            spectrum_time=QtWidgets.QTableWidgetItem(
                                time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(filetime)))
                            
                            row_list=[spectrum_name,spectrum_time]
                            
                            spectrum=Spectrum(subdir)
                            
                            brush = QtGui.QBrush(QtGui.QColor(213, 121, 0))
                            brush.setStyle(QtCore.Qt.NoBrush)
                            
                            for j, item in enumerate(spectrum.get_values()):
                                tab_item=QtWidgets.QTableWidgetItem(item)
                                if item=='__undefined__':
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
    
    return_row=QtCore.pyqtSignal(list)
    
class MessageBox(QtWidgets.QDialog, message_box.Ui_Dialog):

    def __init__(self, parent=None):
            super(MessageBox, self).__init__(parent)
            self.setupUi(self)
            self.pushButton_2.clicked.connect(self.add)
            self.pushButton.clicked.connect(self.replace)
            
    def replace(self):
        self.ans=1
        self.accept()
        
    def add(self):
        self.ans=2
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
        
        self.tableWidget.setColumnWidth(0,50)
        
        self.comboBox.addItems(user_df['User'])
        self.comboBox.setCurrentIndex(-1)
        
    def fill_table(self):
        
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(user_df))
        self.tableWidget.setSortingEnabled(0)
        for i, item in enumerate(user_df.index.tolist()):
            user=user_df.loc[item,'User']
            payer_id=int(user_df.loc[item,'PayID'])
            payer=user_df.loc[payer_id,'User']
            pattern=user_df.loc[item,'Patterns']
        
            self.tableWidget.setItem(i,0,QtWidgets.QTableWidgetItem('%d'%(item)))
            self.tableWidget.setItem(i,1,QtWidgets.QTableWidgetItem(user))
            self.tableWidget.setItem(i,2,QtWidgets.QTableWidgetItem(payer))
            self.tableWidget.setItem(i,3,QtWidgets.QTableWidgetItem(pattern))
        
        self.tableWidget.setSortingEnabled(1)
        
    def fill_combo(self):
        self.comboBox.clear()
        self.comboBox.addItems(user_df['User'])
        self.comboBox.setCurrentIndex(-1)
        
    def set_enabled(self,val):
        
        if val:
            self.lineEdit.setEnabled(True)
            self.lineEdit_2.setEnabled(True)
            self.comboBox.setEnabled(True)
            self.pushButton.setEnabled(True)
            self.pushButton_2.setEnabled(True)
        else:
            self.lineEdit.setEnabled(False)
            self.lineEdit_2.setEnabled(False)
            self.comboBox.setEnabled(False)
            self.pushButton.setEnabled(False)
            self.pushButton_2.setEnabled(False)
        
    def click_user(self):
        self.set_enabled(True)
        
        row=self.tableWidget.currentRow()
        curr_index=int(self.tableWidget.item(row, 0).text())
        
        self.label_num.setText('%d'%(curr_index))
        self.lineEdit.setText(user_df.loc[curr_index,'User'])
        self.lineEdit_2.setText(user_df.loc[curr_index,'Patterns'])
        self.comboBox.setEditText(user_df.loc[int(user_df.loc[curr_index,'PayID']),'User'])
        
    def delete_user(self):
        row=self.tableWidget.currentRow()
        curr_index=int(self.tableWidget.item(row, 0).text())
        user_name=user_df.loc[curr_index,'User']
        msg='Czy na pewno chcesz usunąć dane użytkownika "'+user_name+'"?'
        ans=QtWidgets.QMessageBox.question(self, 'Usuń', msg, 
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if ans == QtWidgets.QMessageBox.Yes:
            user_df.drop([curr_index],inplace=True)
            user_df.sort_values(by=['User'],inplace=True)
            user_df.to_csv('users.csv',sep=';',index_label='ID')
            
            self.fill_table()
            self.fill_combo()
            
        
    def new_user(self):
        self.set_enabled(True)
        
        new_index=max(user_df.index.tolist())+1
        self.label_num.setText('%d'%(new_index))
        self.lineEdit.setText('')
        self.lineEdit_2.setText('')
        self.comboBox.setCurrentIndex(-1)
        
    def clear(self):
        self.label_num.setText('')
        self.lineEdit.setText('')
        self.lineEdit_2.setText('')
        self.comboBox.setCurrentIndex(-1)
        self.set_enabled(False)
        
    def save(self):
        index=int(self.label_num.text())
        user_text=self.lineEdit.text()
        patterns=self.lineEdit_2.text()
        if (user_text=='' or patterns==''):
            msg_box=QtWidgets.QMessageBox.critical(self, 'Błąd', 'Uzupełnij brakujące dane!',
                                                   QtWidgets.QMessageBox.Ok)
            return
        else:
            match_user=user_df[user_df['User']==user_text]
            match_pattern=user_df[user_df['Patterns']==patterns]
            if not match_user.empty:
                user_ind=match_user.index.tolist()[0]
                if user_ind!=index:
                    msg_text='Nazwa użytkownika "'+user_text+'" jest już przypisana. Wybierz inną nazwę.'
                    msg_box=QtWidgets.QMessageBox.critical(self, 'Błąd', msg_text,
                                               QtWidgets.QMessageBox.Ok)
                    return
                    
            if not match_pattern.empty:
                pattern_ind=match_pattern.index.tolist()[0]
                if pattern_ind!=index:
                    msg_text='Nazwa "'+patterns+'" jest już przypisana. Wybierz inną nazwę.'
                    msg_box=QtWidgets.QMessageBox.critical(self, 'Błąd', msg_text,
                                               QtWidgets.QMessageBox.Ok)
                    return
                    
                    
            
        payer_text=self.comboBox.currentText()
        if payer_text=='':
            payer_id=index
        else:
            match_df=user_df[user_df['User']==payer_text]
            if not match_df.empty:
                payer_id=int(match_df.index.tolist()[0])
            else:
                msg_box=QtWidgets.QMessageBox.critical(self, 'Błąd', 'Dane w polu "Płatnik" nie pasują do żadnego użytkownika!',
                                                       QtWidgets.QMessageBox.Ok)
                return
            
        user_df.loc[index,'User']=user_text
        user_df.loc[index,'Patterns']=patterns
        user_df.loc[index,'PayID']=int(payer_id)
        

        user_df.sort_values(by=['User'],inplace=True)
        user_df.to_csv('users.csv',sep=';',index_label='ID')
        
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
        
    def fill_table(self,df):
        print(df)
        self.tableWidget.setRowCount(len(df))
        for i,item in enumerate(df.index):
            self.tableWidget.setItem(i,0,QtWidgets.QTableWidgetItem(item))
            sec=df[item]
            td=datetime.timedelta(seconds=sec)
            self.tableWidget.setItem(i,1,QtWidgets.QTableWidgetItem(str(td)))
            self.tableWidget.setItem(i,2,QtWidgets.QTableWidgetItem('%d'%sec))
            
    def bill(self):
        fee=float(self.doubleSpinBox.value())
        
        i=0
        self.tableWidget.setSortingEnabled(False)
        rows=self.tableWidget.rowCount()
        

        for i in range(rows):
            user_item=self.tableWidget.item(i,2)
            if user_item:
                times=float(user_item.text())
                cost=times*fee/3600
                self.tableWidget.setItem(i,3,QtWidgets.QTableWidgetItem('%.2f'%cost))
                
    def export(self):
        cwd=os.getcwd()
        fileName = QtWidgets.QFileDialog.getSaveFileName(self, 'Exportuj', cwd, 'Comma-separated .csv (*.csv);; MS Excel .xls (*.xls)')[0]
        if fileName:
            df=self.read_df()
            if (fileName.endswith('.csv') or fileName.endswith('.CSV')):
                df.to_csv(fileName,sep=',',index_label='ID')
            elif (fileName.endswith('.xls') or fileName.endswith('.XLS')):
                df.to_excel(fileName)
    
            
    def read_df(self):
        rows=self.tableWidget.rowCount()
        cols=self.tableWidget.columnCount()
        
        full_df=DataFrame(columns=['Payer','Time','TimeS','Cost'], index=range(rows))
                                   
        for i in range(rows):
            for j in range(cols):
                item=self.tableWidget.item(i,j)
                if item:
                    full_df.iloc[i,j]=item.text()
                else:
                    full_df.iloc[i,j]=''
                    
        return full_df
    
                    
                    
class Spectrum(object):
    
    def __init__(self,path):
        self.path=path
        self.exp_type=""
        self.ns=0
        self.td1=0
        self.td2=0
        self.msg=""
        self.user_text=''
        self.user=''
        self.payer=''
        self.start_time=None
        self.end_time=None
        self.analyze()
        
        
    def find_user(text):
        
        user_match=user_df[user_df['Patterns'].str.lower()==text.lower()]
        if not user_match.empty:
            user_id=user_match.index.tolist()[0]
            user=user_df.loc[user_id,'User']
            payer_id=int(user_df.loc[user_id,'PayID'])
            payer=user_df.loc[payer_id,'User']
        else:
            user='__undefined__'
            payer='__undefined__'
        
        return (user,payer)
        
    def get_values(self):
        
        times=self.get_times()
        
        return [self.user_text,'','',times['start'],times['end'],
                times['duration'],str(times['dur_s']),self.exp_type,self.ns,self.td1,self.td2]
        
    def get_times(self):
        
        if self.start_time:
            start=datetime.datetime.strftime(self.start_time,'%Y-%m-%d %H:%M:%S %z')
        else:
            start='__undefined__'
         
        if self.end_time:
            end=datetime.datetime.strftime(self.end_time,'%Y-%m-%d %H:%M:%S %z')
        else:
            end='__undefined__'
            
        if (self.start_time and self.end_time):
            self.duration=self.end_time-self.start_time
            duration=str(self.duration)
            dur_s=self.duration.total_seconds()
        else:
            duration='__undefined__'
            dur_s=0
            
        return {'start':start,'end':end,'duration':duration,'dur_s':dur_s}
            
    def analyze(self):
        
        sample_full_name=os.path.split(self.path)[0]
        sample_name=os.path.split(sample_full_name)[1]
        splits=['.','-','_',' ']
        new_name=sample_name
        for item in splits:
            new_name=new_name.split(item)[0]
        user_text=new_name
        
        self.user_text=user_text
        
        try:
            acqus=os.path.join(self.path,'acqus')
            acqus_file=open(acqus, 'r')
        except FileNotFoundError:
            try:
                acqus=os.path.join(self.path,'ACQUS')
                acqus_file=open(acqus, 'r')
            except:
                pass
            
        try:               
            for line in acqus_file:
                if "$EXP=" in line:
                    matchObj=re.search(r'##\$EXP= (.*)',line)
                    if matchObj:
                        exp_type=matchObj.group(1)
                        self.exp_type=exp_type
                if "$NS=" in line:
                    matchObj=re.search(r'##\$NS= (.*)',line)
                    if matchObj:
                        ns=matchObj.group(1)
                        self.ns=ns
                if "$TD=" in line:
                    matchObj=re.search(r'##\$TD= (.*)',line)
                    if matchObj:
                        td=matchObj.group(1)
                        self.td1=td
        except:
            self.ns='__undefined__'
            
        try:
            acqus2=os.path.join(self.path,'acqu2s')
            acqus2_file=open(acqus2, 'r')
        except FileNotFoundError:
            try:
                acqus2=os.path.join(self.path,'ACQU2S')
                acqus2_file=open(acqus2, 'r')
            except:
                pass
            
        try:               
            for line in acqus2_file:
                if "$TD=" in line:
                    matchObj=re.search(r'##\$TD= (.*)',line)
                    if matchObj:
                        td=matchObj.group(1)
                        self.td2=td
        except:
            pass
        
        try:
            audita=os.path.join(self.path,'audita.txt')
            audita_file=open(audita,'r')
        except FileNotFoundError:
            try:
                audita=os.path.join(self.path,'AUDITA.TXT')
                audita_file=open(audita, 'r')
            except:
                pass

        try:            
            audita_text=audita_file.read().replace('\n','')
            audit_list=audita_text.split('##')
            for item in audit_list:
                if "AUDIT TRAIL=" in item:
                    values=item.split(')(')[1]
                    values_list=values.split(',')
                    finished=values_list[1][1:-1]
                    started=values_list[6]
                    try:
                        end_time=datetime.datetime.strptime(finished,'%Y-%m-%d %H:%M:%S.%f %z')
                        self.end_time=end_time
                    except:
                        end_time=None
                    try:
                        start_time_str=started.split('started at')[1].strip()
                        start_time=datetime.datetime.strptime(start_time_str,'%Y-%m-%d %H:%M:%S.%f %z')
                        self.start_time=start_time
                    except:
                        try:
                            acqu=os.path.join(self.path,'acqu')
                            acqu_file=open(acqu, 'r')
                        except FileNotFoundError:
                            try:
                                acqu=os.path.join(self.path,'ACQU')
                                acqu_file=open(acqu, 'r')
                            except:
                                pass
                        
                        for line in acqu_file:
                            if line.startswith("$$"):
                                start_time1=dparser.parse(line,fuzzy=True)
                                break
                        
                        acqu_file.close()
                        
                        try:
                            pulse=os.path.join(self.path,'pulseprogram')
                            pulse_file=open(pulse, 'r')
                        except FileNotFoundError:
                            try:
                                pulse=os.path.join(self.path,'PULSEPROGRAM')
                                pulse_file=open(pulse, 'r')
                            except:
                                pass
                        pulse_file.close()
                        
                        auditatime=os.path.getmtime(audita)
                        audita_time=datetime.datetime.fromtimestamp(auditatime)
                        end_time2=audita_time
                        
                        pulsetime=os.path.getmtime(pulse)
                        pulse_time=datetime.datetime.fromtimestamp(pulsetime)
                        start_time2=pulse_time
                        
                        dif1=self.end_time-start_time1
                        dif2=end_time2-start_time2
                        if dif1==abs(dif1):
                            self.start_time=start_time1
                        elif dif2==abs(dif2):
                            self.start_time=start_time2
                            self.end_time=end_time2
                        else:
                            self.start_time=None
                        
                        

                
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
    notice ="An unhandled exception occurred.\n"
    versionInfo="2.0"
    timeString = time.strftime("%Y-%m-%d, %H:%M:%S")

    errmsg = '%s: \n%s' % (str(excType), str(excValue))
    sections = [timeString,separator, errmsg, separator]
    msg = '\n'.join(sections)
    try:
        f = open(logFile, "a")
        f.write(msg)
        f.write(versionInfo)
        f.close()
    except IOError:
        pass
    errorbox = QtWidgets.QMessageBox()
    errorbox.setText(str(notice)+str(msg))
    errorbox.exec_()


sys.excepthook = excepthookA


def main():
    app = QtWidgets.QApplication(sys.argv)
    
    qt_translator = QtCore.QTranslator()
    qt_translator.load("qt_pl",QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
    app.installTranslator(qt_translator)
    
    #app.setStyle(QtWidgets.QStyleFactory.create('Breeze'))
      
    form = App()
    form.show()
    app.exec_()
    
if __name__ == '__main__':
    main()


        
        