# -*- coding: utf-8 -*-
"""
Created on Wed May 23 21:16:12 2018

@author: marcin
"""
import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate, Spacer
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class Generator(object):
    def __init__(self,path,title,date_from,date_to,price,data_df=None):
        self.path=path
        self.title=title
        self.date_from=date_from
        self.date_to=date_to
        self.price=price
        self.total_count=0
        self.total_sec=0
        self.data_df=data_df
        
        self.data_list=[]

        
        
        self.dir='/home/marcin/Dokumenty/projekty/NMRSpectrumCount/mail_test/'
        
        
        roboto_font=r"/home/marcin/Dokumenty/projekty/NMRSpectrumCount/fonts/Roboto/Roboto-Regular.ttf"
        pdfmetrics.registerFont(TTFont("Roboto Regular",roboto_font))
        
        roboto_bold=r"/home/marcin/Dokumenty/projekty/NMRSpectrumCount/fonts/Roboto/Roboto-Bold.ttf"
        pdfmetrics.registerFont(TTFont("Roboto Bold",roboto_bold))
        
        
    @staticmethod
    def _header_footer(canvas, doc):
        # Save the state of our canvas so we can draw on it
        canvas.saveState()
        styles = getSampleStyleSheet()
 
        #Header
        header = Paragraph('', styles['Normal'])
        w, h = header.wrap(doc.width, doc.topMargin)
        header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin)
        
 
        # Footer
        footer = Paragraph('', styles['Normal'])
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.leftMargin, h)
 
        # Release the canvas
        canvas.restoreState()
        
    def calculate_df(self):
        self.data_df.sort_values(by='Times',inplace=True)
        self.total_count=self.data_df['Count'].sum()
        self.total_sec=self.data_df['Times'].sum()
        
        for item in self.data_df.index.tolist():
            self.data_list.append([item,self.data_df.loc[item,'Count'],
                                   self.timeformat(self.data_df.loc[item,'Times']),
                                   '%.2f'%self.data_df.loc[item,'Cost']])
                                   
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
        
    def generate_report(self):
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
#    
#        canv=canvas.Canvas("form.pdf", pagesize=A4,bottomup=0)
#        canv.setLineWidth(.3)
#        canv.setFont('Roboto Regular', 10)
#         
#        canv.drawString(30,50,'Pracownia Spektroskopii NMR')
#        #canv.drawString(30,735,'Wydział Chemii UJ')
#        canv.drawString(500,50,"12/12/2010")
#        canv.line(30,53,width-30,53)
#
#
#        canv.drawString(30,100,"Rodzaj zlecenia: ") 
#        canv.drawString(30,120,"Za okres: ")
#        
#        
#        canv.drawString(30,160,"Opłata za 1h pomiaru [PLN]: ")
#        
#        canv.drawString(30,200,"Całkowita liczba zarejestrowanych widm: ")
#        canv.drawString(30,220,"Całkowity czas trwania: ")
#        canv.drawString(30,240,"Całkowity koszt [PLN]: ")
#        
#        canv.drawString(30,300,"Rozliczenie ")
#        
#        
#        canv.setFont('Roboto Bold', 10)
#        
#        canv.drawString(120,100,self.title)
#        canv.drawString(120,120,self.date_from+' - '+self.date_to)
        
        title_str='<font name="Roboto Bold" size="12">Podsumowanie rozliczenia pomiarów zleconych</font>'
        title_par=Paragraph(title_str,style=style["Normal"])
        
        
        
        
#        title_par.wrapOn(canv,width,height)
#        title_par.drawOn(canv,30, 80, mm)
        
        
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
            
            
            
                
        doc.build(cont,onFirstPage=self._header_footer,onLaterPages=self._header_footer,canvasmaker=NumberedCanvas)
        
#        t_str='<font name="Roboto Bold" size="10">%s</font>'%self.title
#        
#        t_par=Paragraph(t_str,style=style['Normal'])
#        t_par.wrapOn(canv,width,height)
#        t_par.drawOn(canv,120, 100, mm)
#        
#        
#        
#        czas_str=('<font name="Roboto Bold" size="10">%s - %s</font>')%(self.date_from,self.date_to)
#        
#        
#        
#        c_par=Paragraph(czas_str,style=style['Normal'])
#        c_par.wrapOn(canv,width,height)
#        c_par.drawOn(canv,120, 120, mm)
         
        #canv.save()
        
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
    
    report_generator=Generator('Zmieniacz 2018','01-01-2018','30-06-2018',5)
    report_generator.generate_report()
    
if __name__ == '__main__':              # if we're running file directly and not importing it
    main()
