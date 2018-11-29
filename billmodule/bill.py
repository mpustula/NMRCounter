# -*- coding: utf-8 -*-
"""
Created on 28.11.2018 14:50:10

@author: marcin
"""

import datetime
import pandas as pd
import os


class Bill(object):
    def __init__(self):
        self.df=pd.read_csv('data/bills.csv', sep=',', index_col=0)
        self.df.fillna('',inplace=True)

    def save(self):
        self.df.to_csv('data/bills.csv')

    def delete(self,index):
        self.df.drop(index,inplace=True)
        self.save()

    def get(self,index):

        return self.df.loc[index,:]

    def filter(self,payer=None, zlec=None, cr_from=None, cr_to=None, ex_from=None, ex_to=None):
        rdf=self.df
        if payer:
            rdf=rdf[rdf['Payer'] == payer]
        if zlec:
            rdf=rdf[rdf['Zlecenie'] == zlec]
        if cr_from:
            rdf=rdf[rdf['Date'] >= self.format_date(cr_from)]
        if cr_to:
            rdf=rdf[rdf['Date'] <= self.format_date(cr_to)]
        if ex_from:
            rdf = rdf[rdf['To'] >= self.format_date(ex_from)]
        if ex_to:
            rdf = rdf[rdf['From'] <= self.format_date(ex_to)]
        return rdf

    def format_date(self,date):
        return datetime.datetime.strftime(date, '%Y-%m-%d')

    def change(self, index, type, zlec, payer, price, hours, expt, date_from, date_to, uwagi):
        self.insert(index, 'edit', type, zlec, payer, price, hours, expt, date_from, date_to, uwagi)

    def new(self, type, zlec, payer, price, hours, expt, date_from, date_to, uwagi):
        max_id=max(self.df.index.tolist() or [0])
        new_id=max_id+1

        self.insert(new_id, 'new', type, zlec, payer, price, hours, expt, date_from, date_to, uwagi)

    def insert(self, new_id, date, type, zlec, payer, price, hours, expt, date_from, date_to, uwagi):
        if date=='new':
            self.df.loc[new_id,'Date']=self.format_date(datetime.datetime.now())
        self.df.loc[new_id,'Type']=type
        self.df.loc[new_id, 'Zlecenie'] = zlec
        self.df.loc[new_id, 'Payer'] = payer
        self.df.loc[new_id, 'Price'] = price
        self.df.loc[new_id, 'Hours'] = hours
        self.df.loc[new_id, 'Experiments'] = expt
        self.df.loc[new_id, 'From'] = self.format_date(date_from)
        self.df.loc[new_id, 'To'] = self.format_date(date_to)
        self.df.loc[new_id, 'Uwagi'] = uwagi

        self.save()



def main():
    log = LogObject('/home/marcin/Dokumenty/projekty/NMRSpectrumCount/data/logs/')
    log.add('test', 'marcin', 'test@mail', 'nmr@chemia', 'nmr', 'Sent correctly')
    log.save()


if __name__ == '__main__':  # if we're running file directly and not importing it
    main()
