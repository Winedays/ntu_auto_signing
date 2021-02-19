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
testuser # <user name> 改成帳號
123456  # <passowrd> 改成密碼
```

`config.ini` 檔案用於設定隨機時間打卡功能，`RandomDelay = True` 時將啟用延遲打卡功能，延遲時間每次隨機決定且上限為 `MaxDelayTime (mins)`。
- e.g. `MaxDelayTime = 5`，於 8 點執行程式，將隨機在 8:00~8:05 分打卡

透過 python 執行程式，當輸入參數為 `signin` 時會執行簽到，參數為 `signout` 時會執行簽退
```python
# 簽到
python auto_signing.py signin
# 簽退
python auto_signing.py signout
```

## 排程設定
必須要在程式所在的目錄執行程式，否則 `user.conf` 檔的讀取會出錯  
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
- 加入 email 通知，打卡失敗時可以提醒你去手動打卡
- 封裝成執行檔，不需要 python 就可以執行程式
- 支援一次替多個帳號打卡
- 自動判斷時間決定打卡行為