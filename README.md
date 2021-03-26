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

修改 `config.ini` 檔案設定，`[TIME_DELAY]` 用於設定延遲打卡功能，當 `RandomDelay = True` 時將啟用，延遲時間每次隨機決定且上限為 `MaxDelayTime (mins)`。`[MAIL]` 用於設定 email 通知，將 `User` 及 `Password` 改為自己的 gmail 帳號密碼。`[USER]` 為 MyNTU 帳號資料，將 `UserName` 及 `Password` 改為自己的帳號密碼。
```
[TIME_DELAY]
# delay time in mins
RandomDelay = true
MaxDelayTime = 5

[MAIL]
Host = smtp.gmail.com
TlsPort = 587
User = <gmail 帳號>@gmail.com
Password = <gmail 密碼>

[USER]
UserName = <myntu 帳號>
Password = <myntu 密碼>
```


透過 python 執行程式，當輸入參數為 `signin` 時會執行簽到，參數為 `signout` 時會執行簽退
```python
# 簽到
python auto_signing.py signin
# 簽退
python auto_signing.py signout
```

## 延遲打卡功能
延遲打卡功能用於避免每天都在相同的時間點打卡，令程式每天的打卡時間具有隨機性，當此功能啟用時程式將在執行後隨機延遲一定的時間後才會進行打卡動作，透過設定 `MaxDelayTime` 能指定最大延遲時間 (分鐘)  
* e.g.`RandomDelay = true, MaxDelayTime = 5`，於 8 點執行程式，將隨機在 8:00~8:05 分打卡

## Email 通知功能
Email 通知功能用於在程式打卡失敗時發送 email 進行通知，提醒使用者打卡失敗並提供相關的錯誤信息，此功能預設使用 gmail 信箱進行通知，若需要使用其他信箱，需自行更改合適的 `Host` 及 `TlsPort` 設定

## 排程設定
必須要在程式所在的目錄執行程式，否則 `config.ini` 檔的讀取會出錯  
請自行注意 python 環境的相關問題
* Linux
    * 以 cron 設定固定時間執行程式
    * crontab設定  
    ```shell
    # 文件格式說明
    # ┌──分鐘（0 - 59）
    # │  ┌──小時（0 - 23）
    # │  │  ┌──日（1 - 31）
    # │  │  │  ┌─月（1 - 12）
    # │  │  │  │  ┌─星期（0 - 6，表示从周日到周六）
    # │  │  │  │  │
    # *  *  *  *  * 被執行的命令
    15 8 * * 1-5 cd /home/auto_sign && python3 /home/auto_sign/auto_signing.py signin ;
    20 17 * * 1-5 cd /home/auto_sign && python3 /home/auto_sign/auto_signing.py signout ;
    ```

## Todo
- ~~加入隨機延遲，不會每天都在同一個時間打卡~~
- ~~加入 email 通知，打卡失敗時可以提醒你去手動打卡~~
- 封裝成執行檔，不需要 python 就可以執行程式
- 自動判斷時間決定打卡行為