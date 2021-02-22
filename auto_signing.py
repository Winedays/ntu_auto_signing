import os
import json
import argparse
import requests
import sys
import configparser
import random
import time
import traceback
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# set Argument
def setArgument() :
    parser = argparse.ArgumentParser()
    # position argument
    parser.add_argument("action", type=str, choices=["signin", "signout"], help = "action of sign in or sign out.")
    args = parser.parse_args()
    return args

# read user config
def readCongif( file: str ) :
    with open( file , 'r' , encoding="utf-8" ) as f :
        user = f.readline().strip()
        password = f.readline().strip()
    userDict = {'user': user, 'pass': password}  # {'user': <name>, 'pass': <password>} 
    return userDict

# prepare mail message & send it
def sendErrorMessageMail( checkMessage: str, messageDict: str, mailConfig: dict ) :
    mailDict = {'host': None, 'user': None, 'password': None, 'sender': None,
                'subject': None, 'from': None, 'to': None, 'body': None}
    mail_subject = "NTU Auto Singing Wraning Massage"
    
    # read mail config
    mailDict['host'] = mailConfig['Host']
    mailDict['port'] = int(mailConfig['TlsPort'])
    mailDict['user'] = mailConfig['User']
    mailDict['password'] = mailConfig['Password']
    
    # set mail message
    mailDict['sender'] = "NTU Auto Singing"
    mailDict['subject'] = "NTU Auto Singing Massage (%s)" % checkMessage
    mailDict['from'] = mailConfig['User']
    mailDict['to'] = mailConfig['User']
    bodyText = ""
    if 'd' in messageDict :
        bodyText += 'NTU Auto Singing got warning or error message at %s\n\n' % str(messageDict['d'])
    else :
        bodyText += 'NTU Auto Singing got unknow request from MyNTU\n\n'
    if 'msg' in messageDict :
        bodyText += 'System Message :%s\n\n' % str(messageDict['msg'])
    bodyText += 'Request Json :\n%s' % str(messageDict)
    mailDict['body'] = bodyText
    
    # send mail
    sendMail( mailDict )
    return ;
    
# send error massage mail
def sendMail( mailDict: dict ) :
    mail_host = mailDict['host']
    mail_port = int(mailDict['port'])
    mail_user = mailDict['user']
    mail_pass = mailDict['password']

    # mail massage
    msg = MIMEMultipart()
    msg['From'] = mailDict['from'] # "counter programe"
    msg['To'] = mailDict['to'] # "test"
    msg['Subject'] = mailDict['subject']
    body = mailDict['body']

    msg.attach(MIMEText(body, 'plain'))
    # send mail
    server = smtplib.SMTP(mail_host, mail_port)
    server.starttls()
    server.login(mail_user, mail_pass)
    text = msg.as_string()
    server.sendmail(msg['From'], msg['To'], text)
    server.quit()
    print( "Error Massage Mail Sent to " + mailDict['to'] )
    return ;

# login
def loginMyntu( session , userInfo ) :
    website = "https://my.ntu.edu.tw/"
    
    # get ASP.NET_SessionId & citrix_ns_id at myntu
    request = session.get( website, headers = session.headers )
    if request.status_code != 200:
        raise Exception("Login Error: please check your network connection!")
    # aspnet_cookies = request.cookies
    # aspnet_session_id = aspnet_cookies.get("ASP.NET_SessionId")
    # citrix_ns_id = aspnet_cookies.get("citrix_ns_id")

    # direction to login page , get portal direction with "ec"
    url = "https://my.ntu.edu.tw/attend/ssi.aspx?type=login" #"https://my.ntu.edu.tw/login.aspx"
    session.headers['Host'] = 'my.ntu.edu.tw'
    session.headers['Referer'] = 'https://my.ntu.edu.tw/attend/ssi.aspx'
    # params = {"type":"login"}
    request = session.get(url, headers = session.headers, cookies = session.cookies, allow_redirects=False)
    if request.status_code != 302:
        raise Exception("Login Error: please check your network connection!")
    request.encoding = 'utf-8'
    redirects = urljoin( website, request.headers["Location"] )
    
    # get PHPSESSID from s/login2/p6.php
    request = session.get(redirects, headers = session.headers, cookies = session.cookies, allow_redirects=False)
    if request.status_code != 302:
        raise Exception("Login Error: please check your network connection!")
    redirects = request.headers["Location"]
    
    session.headers['Host'] = 'web2.cc.ntu.edu.tw'
    session.headers['Referer'] = 'https://my.ntu.edu.tw/attend/ssi.aspx'
    request = session.get(redirects, headers = session.headers, cookies = session.cookies, allow_redirects=False)
    if request.status_code != 302:
        raise Exception("Login Error: please check your network connection!")
    # php_cookies = requests.cookies
    # php_sessid = php_cookies.get("PHPSESSID")
    
    # login myntu
    url = "https://web2.cc.ntu.edu.tw/p/s/login2/p1.php"
    session.headers['Host'] = 'web2.cc.ntu.edu.tw'
    session.headers['Origin'] = 'https://web2.cc.ntu.edu.tw'
    session.headers['Referer'] = 'https://web2.cc.ntu.edu.tw/p/s/login2/p1.php'
    session.headers['Content-Type'] = 'application/x-www-form-urlencoded'
    
    userInfo['Submit'] = '登入' # 登入,%E7%99%BB%E5%85%A5
    request = session.post(url, data=userInfo, headers = session.headers, cookies = session.cookies, allow_redirects=False)
    if request.status_code != 302:
        raise Exception("Login Error: please check your network connection!")
    request.encoding = 'utf-8'
    redirects = request.headers["Location"]

    # redirects to portal with 'sess' , get attend sys. redirects link
    session.headers['Host'] = 'my.ntu.edu.tw'
    session.headers.pop('Origin', None)
    session.headers.pop('Content-Type', None)
    request = session.post(redirects, headers = session.headers, cookies = session.cookies, allow_redirects=False)
    if request.status_code != 302:
        raise Exception("Login Error: please check your network connection!")
    redirects = request.headers["Location"]

    # redirects to attend system page & login by myntu
    request = session.get(redirects, headers = session.headers, cookies = session.cookies, allow_redirects=False)
    if request.status_code != 302:
        raise Exception("Login Error: please check your network connection!")
    redirects = urljoin( website, request.headers["Location"] ) # directs to attend system page after login
    
    session.headers.pop('Referer', None)
    return redirects

# sign in
def signIn( session ) :
    website = "https://my.ntu.edu.tw/attend/"
    
    url = "https://my.ntu.edu.tw/attend/ajax/signInR2.ashx"
    session.headers['Host'] = 'my.ntu.edu.tw'
    session.headers['Origin'] = 'https://my.ntu.edu.tw'
    session.headers['Referer'] = 'https://my.ntu.edu.tw/attend/ssi.aspx'
    session.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
    session.headers['X-Requested-With'] = 'XMLHttpRequest'
    
    # 簽到
    data = {'type': 6, 't': 1, 'otA': 0} 
    request = session.post(url, data=data, headers = session.headers, cookies = session.cookies)
    if request.status_code != 200 :
        raise Exception("SignIn Error: please check your network connection!")
    messageStr = request.text
    messageDict = json.loads( messageStr.replace("\r","").replace("\n","") )
    messageDict = messageDict[0]
    # requests.text example : [{'t': 1, 'msg': '簽退成功(r2)。', 'd': '2020-11-23 17:59:59', 'on': '2020-11-23 08:59:59', 'off': '2020-11-23 17:59:59', 'name': 'XXX(T0000)', 'ws': '08:00', 'we': '17:00', 'wb': '60'}]
    return messageDict

# sign out
def signOut( session ) :
    website = "https://my.ntu.edu.tw/attend/"
    
    # headers
    url = "https://my.ntu.edu.tw/attend/ajax/signInR2.ashx"
    session.headers['Host'] = 'my.ntu.edu.tw'
    session.headers['Origin'] = 'https://my.ntu.edu.tw'
    session.headers['Referer'] = 'https://my.ntu.edu.tw/attend/ssi.aspx'
    session.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
    session.headers['X-Requested-With'] = 'XMLHttpRequest'
    
    # 簽退
    data = {'type': 6, 't': 2, 'otA': 0} 
    request = session.post(url, data=data, headers = session.headers, cookies = session.cookies)
    if request.status_code != 200 :
        raise Exception("SignOut Error: please check your network connection!")
    messageStr = request.text
    messageDict = json.loads( messageStr.replace("\r","").replace("\n","") )
    messageDict = messageDict[0]
    # requests.text example : [{'t': 1, 'msg': '簽退成功(r2)。', 'd': '2020-11-23 17:59:59', 'on': '2020-11-23 08:59:59', 'off': '2020-11-23 17:59:59', 'name': 'XXX(T0000)', 'ws': '08:00', 'we': '17:00', 'wb': '60'}]
    return messageDict
    
# check is sign in/out success & return error massage if failed
def checkSignSuccess( messageDict ) :
    checkDict = {'success': False, 'massage': ""}
    if 't' not in messageDict :
        checkDict['massage'] = "Wraning: Got a unknow request."
    elif messageDict['t'] == 1 :
        checkDict['success'] = True
    else :  # 't' != 1 
        if "不需上班" in messageDict['msg'] :
            checkDict['massage'] = "Error: Today is non-working day"
        elif "請先簽到" in messageDict['msg'] :
            checkDict['massage'] = "Error: Sign out failed - No sign in record"
        elif "本日至遲須於" in messageDict['msg'] :
            checkDict['massage'] = "Error: Sign out failed - Too late to sign out"
        else :
            checkDict['massage'] = "Error: Sign in/out failed"
    return checkDict ;
    
if __name__ == "__main__" :
    # get argument & config
    args = setArgument()
    action = args.action
    config = configparser.ConfigParser()
    config.read("config.ini")
    if "TIME_DELAY" not in config :
        raise Exception("Config Error: section \"TIME_DELAY\" not find.")
    randomDelay = config["TIME_DELAY"]["RandomDelay"].lower()
    maxDelayTime = float(config["TIME_DELAY"]["MaxDelayTime"])
    
    # load user info.
    userDict = readCongif( "./user.conf" )
    
    # set delay time
    if randomDelay == "true" :
        delay = random.random() * maxDelayTime * 60  # secs
        time.sleep( delay )  # delay before singin/signout
    
    messageDict = None
    checkDict = None
    try :
        # create session
        session = requests.Session()
        session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
        session.headers['Connection'] = 'keep-alive'
        
        # login myntu
        attendPages = loginMyntu( session , userDict )
        
        # check is login success
        session.headers['Host'] = 'my.ntu.edu.tw'
        session.headers['Referer'] = 'https://web2.cc.ntu.edu.tw/p/s/login2/p1.php'
        # back to attend sys. page
        request = session.get(attendPages, headers = session.headers, cookies = session.cookies)
        if request.status_code != 200:
            raise Exception("Login Error: please check your network connection!")
        soup = BeautifulSoup(request.text, 'html.parser')
        # check is signin/signout btn. exisit
        btnDiv = soup.find("div", "jumbotron mid bc jumbotronfix")
        if not btnDiv :
            raise Exception("Login Error: please check your user name or password!")
        btnList = btnDiv.find_all('a')
        if len(btnList) != 2 :
            raise Exception("Login Error: please check your user name or password!")
        
        # signin / signout
        if btnList[0].get("id") == "btSign" and btnList[1].get("id") == "btSign2" :
            # viewState = soup.find("input", id="__VIEWSTATE", type="hidden").get("value")
            # viewStateGenerator = soup.find("input", id="__VIEWSTATEGENERATOR", type="hidden").get("value")
            
            if action == "signin" :
                messageDict = signIn(session);
            elif action == "signout" :
                messageDict = signOut(session);
            else :
                messageDict = {'t': -1, "msg": "Wrong Signing Action"}
            print(messageDict)
            # check is signing success
            checkDict = checkSignSuccess( messageDict )
            
    except Exception as e :
        checkDict['success'] = False
        checkDict['massage'] = "Exception Error : " + str(e)
        messageDict = {'t': -1, "msg": traceback.format_exc()}
        print("Exception Error : " + str(e))
        print(traceback.format_exc())
        
    finally :
        if not checkDict['success'] and "MAIL" in config and config["MAIL"]["SendWraningMail"].lower() == "true" :
            try :
                sendErrorMessageMail( checkDict['massage'], messageDict, config["MAIL"] )
            except Exception as e_mail :
                print("Exception Error : " + str(e_mail))
                print(traceback.format_exc())
