###### tags: `github`
[![hackmd-github-sync-badge](https://hackmd.io/4f73iJ-oSreKOZ53jg48ag/badge)](https://hackmd.io/4f73iJ-oSreKOZ53jg48ag)

# 台大到勤自動帳號簽到退

**以 python 實作之台大到勤系統自動簽到退程式**

利用爬蟲方式，完成登入計中帳號、進入到勤差假系統、簽到/簽退一連串的流程。配合排程系統設定好需要打卡的時間，程式就能夠自動替你完成打卡。  
  
省去人手打卡所花費的時間及避免忘記打卡所帶來的問題。  

## Requirements
Python 3.7.9  
requests\==2.23.0  
beautifulsoup4\==4.8.2  

## Getting  started
git clone 下載程式到本機端 / 直接從 github [下載壓縮檔](https://github.com/Winedays/ntu_auto_signing/archive/master.zip)
```
git clone https://github.com/Winedays/ntu_auto_signing.git
```

將 `user.conf.sample` 改名成 `user.conf`，打開檔案在第一行填入自己的帳號，第二行填入帳號的密碼
```
<user name>
<passowrd>
```

透過 python 執行程式，當輸入參數為 `signin` 時會執行簽到，參數為 `signout` 時會執行簽退
```python
# 簽到
python auto_signing.py signin
# 簽退
python auto_signing.py signout
```

## Todo
- [ ] 加入隨機延遲，不會每天都在同一個時間打卡
- [ ] 加入 email 通知，打卡失敗時可以提醒你去手動打卡
- [ ] 封裝成執行檔，不需要 python 就可以執行程式
- [ ] 支援一次替多個帳號打卡
- [ ] 自動判斷時間決定打卡行為