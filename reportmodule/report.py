# -*- coding: utf-8 -*-
"""
Created on Wed May 23 21:16:12 2018

@author: marcin
"""
import datetime
import os
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate, Spacer
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class DFConnector(object):
    def __init__(self,result_file,init_files):
        self.result=result_file
        self.files=init_files
        self.dfs=[]
        
    def merge(self):
        for file in self.files:
            name=os.path.basename(file).split('.')[0]
            print(name)
            df=pd.read_csv(file,index_col=0)
            df.rename(index=str,columns={"Cost":name},inplace=True)
            df=df[name].fillna(0)
            print(df)
            
            self.dfs.append(df)
        
        merged_df=pd.concat(self.dfs,axis=1)
        
        merged_df.to_csv(self.result)

class Generator(object):
    def __init__(self,path,title,date_from,date_to,price,data_df=None,full_df=None):
        self.path=path
        self.title=title
        self.date_from=date_from
        self.date_to=date_to
        self.price=price
        self.total_count=0
        self.total_sec=0
        self.data_df=data_df
        
        self.full_df=full_df
        
        self.data_list=[]

        ############################################################zmienione pod windows
        
        self.dir=os.getcwd()
        #print('Working dir: ',self.dir)
        
        roboto_font=os.path.join(self.dir,"fonts\Roboto\Roboto-Regular.ttf")
        pdfmetrics.registerFont(TTFont("Roboto Regular",roboto_font))
        
        roboto_bold=os.path.join(self.dir,"fonts\Roboto\Roboto-Bold.ttf")
        pdfmetrics.registerFont(TTFont("Roboto Bold",roboto_bold))
        
        roboto_cond=os.path.join(self.dir,"fonts\Roboto_Condensed\RobotoCondensed-Regular.ttf")
        pdfmetrics.registerFont(TTFont("Roboto Condensed Regular",roboto_cond))
        
        
    @staticmethod
    def _header_footer(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()
        
        styles.add(ParagraphStyle(name='MainStyle',
                                       fontName='Roboto Regular',
                                       fontSize=8,
                                       leading=8))
 
        #Header
        header = Paragraph('Pracownia Spektroskopii NMR', styles['MainStyle'])
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + 1.5*doc.topMargin)
        
        current_time=datetime.datetime.now()
        c_time=current_time.strftime("%Y-%m-%d %H:%M:%S")
        #Footer
        footer = Paragraph('Dokument wygenerowano '+c_time, styles['MainStyle'])
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, 15*mm)
 
        # Release the canvas
        canvas.restoreState()
        
    def save_df(self):
        self.data_df.to_csv(self.path.split('.')[0]+'.csv')
        
    def calculate_df(self):
        self.data_df.sort_values(by='Times',inplace=True)
        self.total_count=self.data_df['Count'].sum()
        self.total_sec=self.data_df['Times'].sum()
        
        for item in self.data_df.index.tolist():
            self.data_list.append([item,self.data_df.loc[item,'Count'],
                                   self.timeformat(self.data_df.loc[item,'Times']),
                                   '%.2f'%self.data_df.loc[item,'Cost']])
                                   
    def filter_full_df(self,payer):
        full_list=[]
        df=self.full_df[self.full_df['Payer']==payer]
        df=df[['Spectrum','Date','User','STime','EXP','NS']]
        df.sort_values(by=['User','Date'],inplace=True)
        
        
        for item in df.index.tolist():
            path=df.loc[item,'Spectrum']
            #print(path)
            sample_full_name=os.path.split(path)[0]
            #print(sample_full_name)
            sample_name=os.path.split(sample_full_name)[1]
            
            
            date=df.loc[item,'Date'].split()[0]
            user=df.loc[item,'User']
            ftime=self.timeformat(df.loc[item,'STime'])
            exp=df.loc[item,'EXP']
            ns='%d'%df.loc[item,'NS']
            
            list_item=[sample_name,date,user,ftime,ns,exp]
            
            full_list.append(list_item)
            
        return full_list
                                   
    def calculate_users(self):
        users_list=[]
        for item in self.data_df.index.tolist():
            user_data=self.data_df.loc[item,'Users']
            for item2 in user_data:
                item2[2]=self.timeformat(float(item2[3]))
                del(item2[3])
            users_list.append([item,user_data])
        
        return users_list[::-1]
            
    def timeformat(self,times):
        td=datetime.timedelta(seconds=times)
        hours=times/3600
        return '%0.2f'%hours+' h ('+str(td).split('.')[0]+')'
        
    def partial_report(self,path,payer,count,time,table):
        
        style = getSampleStyleSheet()
        width, height = A4
        
        doc = SimpleDocTemplate(path,pagesize=A4,
                        rightMargin=72,leftMargin=72,
                        topMargin=72,bottomMargin=72)
                        
        style_sheet = getSampleStyleSheet()
        style_sheet.add(ParagraphStyle(name='MainStyle',
                                       fontName='Roboto Regular',
                                       fontSize=10,
                                       leading=12))

        style_sheet.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
        
        cont=[]
        
        title_str='<font name="Roboto Bold" size="12">Podsumowanie rozliczenia pomiarów zleconych</font>'
        title_par=Paragraph(title_str,style=style["Normal"])
        
        cont.append(title_par)
        cont.append(Spacer(1,12*mm))
        
        info_data=[["Płatnik:",payer],
                   ['Rodzaj zlecenia:',self.title],
                   ['Za okres:', self.date_from+' - '+self.date_to],
                   ['Stawka 1h pomiaru [PLN]:','%.2f'%self.price]]
                   
        info_table=Table(info_data,[60*mm,100*mm],4*[8*mm],hAlign='LEFT')
        
        summ_data=[['Całkowita liczba zarejestrowanych widm:',count],
                   ['Całkowity czas trwania:', self.timeformat(time)],
                   ['Koszt całkowity [PLN]:','%.2f'%(time/3600*self.price)]]
                   
        summ_table=Table(summ_data,[80*mm,100*mm],3*[8*mm],hAlign='LEFT')
        
        info_table.setStyle(TableStyle([('FONT',(0,0),(1,2),'Roboto Regular'),
                                        ('FONT',(1,0),(1,2),'Roboto Bold')]))
        summ_table.setStyle(TableStyle([('FONT',(0,0),(1,2),'Roboto Regular'),
                                        ('FONT',(1,0),(1,2),'Roboto Bold')]))
        
        cont.append(info_table)
        cont.append(Spacer(1,10*mm))
        cont.append(summ_table)
        cont.append(Spacer(1,10*mm))
        
        det_str='<font name="Roboto Bold" size="10">Rozliczenie szczegółowe z podziałem na użytkowników:</font>'
        det_par=Paragraph(det_str,style=style["Normal"])
                
        cont.append(Spacer(1,12*mm))
        cont.append(det_par)
        cont.append(Spacer(1,5*mm))
        
        cont.append(table)
        cont.append(Spacer(1,6*mm))
        
        full_str='<font name="Roboto Bold" size="10">Pełne dane dotyczące zarejestrowanych widm:</font>'
        full_par=Paragraph(full_str,style=style["Normal"])
                
        cont.append(Spacer(1,6*mm))
        cont.append(full_par)
        cont.append(Spacer(1,5*mm))
        
        data=self.filter_full_df(payer)
              
        header=['Nazwa próbki','Data','Użytkownik','Czas trwania','Skany','Eksperyment']
        data.append(header)
        
        data_len=len(data)


        col_width=width-doc.leftMargin-doc.rightMargin-300
      
        t=Table(data[::-1],[col_width,45,70,60,25,100],data_len*[4*mm],hAlign='LEFT')

        t.setStyle(TableStyle([('BACKGROUND',(0,0),(5,0),colors.grey),
                               ('FONT',(0,0),(-1,-1),'Roboto Condensed Regular'),
                               ('FONTSIZE',(0,0),(-1,-1),7),
                               ('ALIGN',(0,0),(-1,-1),'LEFT'),
                               ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                               ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                               ('BOX', (0,0), (-1,-1), 0.25, colors.black)]))


        cont.append(t)
        
        
            
        doc.build(cont,onFirstPage=self._header_footer,onLaterPages=self._header_footer,canvasmaker=NumberedCanvas)
        
    def generate_report(self):
        self.save_df()
        self.calculate_df()
        style = getSampleStyleSheet()
        width, height = A4
        
        doc = SimpleDocTemplate(self.path,pagesize=A4,
                        rightMargin=72,leftMargin=72,
                        topMargin=72,bottomMargin=72)
                        
        style_sheet = getSampleStyleSheet()
        style_sheet.add(ParagraphStyle(name='MainStyle',
                                       fontName='Roboto',
                                       fontSize=10,
                                       leading=12))

        style_sheet.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
                        
        cont=[]
        
        title_str='<font name="Roboto Bold" size="12">Podsumowanie rozliczenia pomiarów zleconych</font>'
        title_par=Paragraph(title_str,style=style["Normal"])
        
        cont.append(title_par)
        cont.append(Spacer(1,12*mm))
        
        info_data=[['Rodzaj zlecenia:',self.title],
                   ['Za okres:', self.date_from+' - '+self.date_to],
                   ['Stawka 1h pomiaru [PLN]:','%.2f'%self.price]]
                   
        info_table=Table(info_data,[60*mm,100*mm],3*[8*mm],hAlign='LEFT')
        
        summ_data=[['Całkowita liczba zarejestrowanych widm:',self.total_count],
                   ['Całkowity czas trwania:', self.timeformat(self.total_sec)],
                   ['Koszt całkowity [PLN]:','%.2f'%(self.total_sec/3600*self.price)]]
                   
        summ_table=Table(summ_data,[80*mm,100*mm],3*[8*mm],hAlign='LEFT')
        
        info_table.setStyle(TableStyle([('FONT',(0,0),(1,2),'Roboto Regular'),
                                        ('FONT',(1,0),(1,2),'Roboto Bold')]))
        summ_table.setStyle(TableStyle([('FONT',(0,0),(1,2),'Roboto Regular'),
                                        ('FONT',(1,0),(1,2),'Roboto Bold')]))
        
        cont.append(info_table)
        cont.append(Spacer(1,10*mm))
        cont.append(summ_table)
        cont.append(Spacer(1,10*mm))
        
        #tabela
        
        data=self.data_list
              
        header=['Płatnik','Liczba widm','Czas trwania','Opłata [PLN]']
        data.append(header)
        
        data_len=len(data)
      
        t=Table(data[::-1],[50*mm,25*mm,50*mm,30*mm],data_len*[8*mm],hAlign='LEFT')

        t.setStyle(TableStyle([('BACKGROUND',(0,0),(3,0),colors.grey),
                               ('FONT',(0,0),(-1,-1),'Roboto Regular'),
                               ('ALIGN',(0,0),(-1,-1),'LEFT'),
                               ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                               ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                               ('BOX', (0,0), (-1,-1), 0.25, colors.black)]))


        cont.append(t)
        
        #tabele_szczegolowe
        
        det_str='<font name="Roboto Bold" size="10">Rozliczenie szczegółowe:</font>'
        det_par=Paragraph(det_str,style=style["Normal"])
                
        cont.append(Spacer(1,12*mm))
        cont.append(det_par)
        cont.append(Spacer(1,12*mm))
        
        for item in self.calculate_users():
            payer_str='<font name="Roboto Bold" size="10">%s</font>'%item[0]
            payer_par=Paragraph(payer_str,style=style["Normal"])
            users=item[1]
            header=['Użytkownik','Liczba widm','Czas trwania']
            users.append(header)
            
            users_len=len(users)
            u=Table(users[::-1],[50*mm,25*mm,50*mm],users_len*[8*mm],hAlign='LEFT')
            u.setStyle(TableStyle([('BACKGROUND',(0,0),(2,0),colors.grey),
                               ('FONT',(0,0),(-1,-1),'Roboto Regular'),
                               ('ALIGN',(0,0),(-1,-1),'LEFT'),
                               ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                               ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                               ('BOX', (0,0), (-1,-1), 0.25, colors.black)]))
                               
            cont.append(payer_par)                   
            cont.append(u)
            cont.append(Spacer(1,12*mm))
            
            partial_name=self.path.split('.')[0].replace(' ','_')+'_'+item[0].replace(', ','_')+'.pdf'
            
            self.partial_report(partial_name,item[0],self.data_df.loc[item[0],'Count'],
                                self.data_df.loc[item[0],'Times'],u)
            
            
            
                
        doc.build(cont,onFirstPage=self._header_footer,onLaterPages=self._header_footer,canvasmaker=NumberedCanvas)
        
        
    def standardFonts(self):
        """
        Create a PDF with all the standard fonts
        """
        for enc in ['MacRoman', 'WinAnsi']:
            canv = canvas.Canvas(
                    'StandardFonts_%s.pdf' % enc,
                    )
            canv.setPageCompression(0)
     
            x = 0
            y = 744
            for faceName in pdfmetrics.standardFonts:
                if faceName in ['Symbol', 'ZapfDingbats']:
                    encLabel = faceName+'Encoding'
                else:
                    encLabel = enc + 'Encoding'
     
                fontName = faceName + '-' + encLabel
                pdfmetrics.registerFont(pdfmetrics.Font(fontName,
                                            faceName,
                                            encLabel)
                            )
     
                canv.setFont('Times-Bold', 18)
                canv.drawString(80, y, fontName)
     
                y -= 20
     
                alpha = "abcdefghijklmnopqrstuvwxyz"
                canv.setFont(fontName, 14)
                canv.drawString(x+85, y, alpha)
     
                y -= 20
     
            canv.save()
        
        


class NumberedCanvas(canvas.Canvas):


    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
 

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
 

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
 
 
    def draw_page_number(self, page_count):
        # Change the position of this to wherever you want the page number to be
        self.drawRightString(190 * mm, 15 * mm,
        "Strona %d/%d" % (self._pageNumber, page_count))
        

        
def main():
    #title=input('Title')
    #dfrom=input('From:')
    #dto=input("To:")
    #price=input("Price per hour:")
    
    #report_generator=Generator("test.pdf",'Zmieniacz 2018','01-01-2018','30-06-2018',5)
    #report_generator.generate_report()
    
    concatenator=DFConnector('tests/lip_wrz2018/total.csv',['tests/lip_wrz2018/Zmieniacz.csv','tests/lip_wrz2018/Musielak.csv','tests/lip_wrz2018/zlecenia.csv','tests/lip_wrz2018/NMR300.csv'])
    concatenator.merge()
    
if __name__ == '__main__':              # if we're running file directly and not importing it
    main()
