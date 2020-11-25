import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# read user config
def readCongif( file ) :
    with open( file , 'r' , encoding="utf-8" ) as f :
        user = f.readline().strip()
        password = f.readline().strip()
    userDict = {'user': user, 'pass': password}  # {'user': <name>, 'pass': <password>} 
    return userDict

# login
def loginMyntu( session , userInfo ) :
    #headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
    website = "https://my.ntu.edu.tw/"
    
    # get ASP.NET_SessionId & citrix_ns_id at myntu
    request = session.get(website, headers = session.headers)
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
    data = {'type': 6, 't': 2, 'otA': 0} 
    request = session.post(url, data=data, headers = session.headers, cookies = session.cookies)
    if request.status_code != 200 :
        raise Exception("SignIn Error: please check your network connection!")
    messageStr = request.text
    messageDict = json.loads( messageStr.replace("\r","").replace("\n","") )
    messageDict = messageDict[0]
    request = session.post(url, data=data, headers = session.headers, cookies = session.cookies, allow_redirects=False)
    

# sign out
def signout( session ) :
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
    
if __name__ == "__main__" :  
    
    # load user info.
    userDict = readCongif( "./user.conf" )
    
    try :
        # create session
        session = requests.Session()
        session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
        session.headers['Connection'] = 'keep-alive'
        # login myntu
        attendPages = loginMyntu( session , userDict )
        
        # check is login sucess
        session.headers['Host'] = 'my.ntu.edu.tw'
        session.headers['Referer'] = 'https://web2.cc.ntu.edu.tw/p/s/login2/p1.php'
        # back to attend sys. page
        request = session.get(attendPages, headers = session.headers, cookies = session.cookies)
        if request.status_code != 200:
            raise Exception("Login Error: please check your network connection!")
        soup = BeautifulSoup(request.text, 'html.parser')
        # check is sigin/signout btn. exisit
        btnDiv = soup.find("div", "jumbotron mid bc jumbotronfix")
        if not btnDiv :
            raise Exception("Login Error?: please check your user name or password!")
        btnList = btnDiv.find_all('a')
        if len(btnList) != 2 :
            raise Exception("Login Error?: please check your user name or password!")
        
        # signin / signout
        if btnList[0].get("id") == "btSign" and btnList[1].get("id") == "btSign2" :
            viewState = soup.find("input", id="__VIEWSTATE", type="hidden").get("value")
            viewStateGenerator = soup.find("input", id="__VIEWSTATEGENERATOR", type="hidden").get("value")
        
            # signIn();
            messageDict = signout(session);
            print(messageDict)
            pass
    
    except Exception as e :
        print(e)
        # raise Exception("Exception Error as "+e)