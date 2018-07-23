import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from time import sleep
import os
import zipfile

class MailSender(object):
    def __init__(self,server,port,timeout):
        self.server=server
        self.port=port
        self.timeout=timeout
        
        self.server_obj=None
        
    def connect(self):
        try:
            server = smtplib.SMTP(self.server,self.port,timeout=self.timeout)
            connect_ans=server.connect(self.server,self.port)
        except:
            return (0,'Error: cannot establish server connection')
        else:
            print(connect_ans)
            ehlo=server.ehlo()
            print(ehlo)
            tls_ans=server.starttls()
            print(tls_ans)
            self.server_obj=server
            return (1,'Connected')
            
            
            
    def login(self,username,password):
        if self.server_obj:
            try:
                login_ans=self.server_obj.login(username,password)
            except smtplib.SMTPAuthenticationError:
                return (0, 'Authentication error')
            else:
                print(login_ans)
                return (1,'Logged succesfully')
        else:
            return (0,'You have to connect to server first.')
            
    def close(self):
        
        if self.server_obj:
            self.server_obj.close()
            return (1,'')
        else:
            return (0, 'Not connected')
            
    def check_mail(self,mail):
        if (mail and '@' in mail):
            return True
        else:
            return False
            
    def send(self,send_to,send_from, subject, text, files=None,reply_to=''):
        
        assert isinstance(send_to, list)
        
        for item in send_to:
            is_valid=self.check_mail(item)
            if not is_valid:
                return (0,'E-mail address incorrect')
                
        if reply_to:
            is_valid=self.check_mail(reply_to)
            if not is_valid:
                return (0,'Ans-TO e-mail address incorrect')
        
        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = COMMASPACE.join(send_to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject
        if reply_to:
            msg.add_header('Reply-To', reply_to)
            #msg.add_header('Return-Path',reply_to)
        msg.attach(MIMEText(text))
    
        for f in files or []:
            with open(f, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=basename(f)
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
            
            msg.attach(part)
            
        try:
            ans=self.server_obj.sendmail(send_from, send_to, msg.as_string())
            print(ans)
            return (1,ans)
        except:
            import traceback
            ans=traceback.format_exc()
            ans_last=ans.strip().split('\n')[-1]
            print(ans)
            return (0,ans_last)
        #sleep(5)
        #ans='mail ready to send'


class Compressor(object):
    def __init__(self,folder,zip_dir):
        self.folder=folder
        self.zip_dir=zip_dir
        self.spectrum_name=os.path.basename(self.folder)+'.zip'
        self.zip_path=os.path.join(self.zip_dir,self.spectrum_name)
        
    def zip_spectrum(self):
        if not os.path.exists(self.zip_dir):
            return (0,'The zip directory does not exist!')
        if os.path.exists(self.folder):
            #print(self.zip_path)
            zipf = zipfile.ZipFile(self.zip_path, 'w', zipfile.ZIP_DEFLATED)
            self.zipdir(self.folder, zipf)
            zipf.close()
            return (1,self.zip_path)
        else:
            return (0,'The directory to be compressed does not exist!')
        
    def zipdir(self,path, ziph):
        # ziph is zipfile handle
        rootdir=os.path.basename(path)
        for root, dirs, files in os.walk(path):
            for file in files:
                filepath=os.path.join(root, file)
                parentpath=os.path.relpath(filepath,path)
                arcname=os.path.join(rootdir,parentpath)
                ziph.write(filepath,arcname)
                

def main_m():
    server=input('Server: ')
    port=input('Port: ')
    
    sender=MailSender(server,port)
    sender.connect()
    
    login=input('login:')
    password=input('password')
    
    sender.login(login,password)
    print('login')
    sender.send(['marcin.pustula@doctoral.uj.edu.pl'],'marcin.pustula@doctoral.uj.edu.pl','test message','message')
    print('message sent')

def main_c():
    folder=input('Folder to zip:')
    zip_dir=input('Dir for zipped files:')
    
    compressor=Compressor(folder,zip_dir)
    ans=compressor.zip_spectrum()
    print(ans)
    print('Done!')
    
if __name__ == '__main__':              # if we're running file directly and not importing it
    main_m()
