# -*- coding: utf-8 -*-
"""
Created on Wed May 23 21:16:12 2018

@author: marcin
"""

import datetime
import pandas as pd
import os


class LogObject(object):
    def __init__(self,log_dir):
        today=datetime.datetime.today()
        year=today.year
        month=today.month
        file_name='%02.d'%(month)+'-'+'%d'%(year)+'.log'
        file_path=os.path.join(log_dir,file_name)
        self.path=file_path
        self.open_log()
        
    def open_log(self):
        try:
            df=pd.read_csv(self.path,index_col='index')
        except:
            df=pd.DataFrame(columns=['index','time','spectrum','user','address','from','by','status'])
            df.to_csv(self.path,index='index')
        self.df=df
        
    def add(self,spectrum,user,address,frommail,by,status):
        indexes=self.df.index.tolist() or [0]
        ind=max(indexes)+1
        self.df.loc[ind,'time']=datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d %H:%M:%S')
        self.df.loc[ind,'spectrum']=spectrum
        self.df.loc[ind,'user']=user
        self.df.loc[ind,'address']=address
        self.df.loc[ind,'from']=frommail
        self.df.loc[ind,'by']=by
        self.df.loc[ind,'status']=status
        
    def save(self):
        self.df.to_csv(self.path)
        
        
def main():
    log=LogObject('/home/marcin/Dokumenty/programy/NMRSpectrumCount/data/logs/')        


if __name__ == '__main__':              # if we're running file directly and not importing it
    main()