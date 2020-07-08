# Stocker

## Crawler and Back-End for Taiwan stocks
Stocker是一個使用```爬蟲(Crawler)```抓取台灣上市櫃股票財報並使用```後端程式(Flask)```存入資料庫(MariaDB)的專案，資料庫的選用可以依照個人喜好選擇其他SQL類型資料庫

前端可以和[react-stocker](https://github.com/seal0112/react-stocker)一起搭配使用

## Prerequisites

請事先安裝好python3以及SQL database
- [python3](https://www.python.org/downloads/)
- [SQL (MySQL/MariaDB, PostgreSQL, SQLite)]()

## Installation


```shell
$ git clone https://github.com/seal0112/stocker.git
$ cd stocker/
```

#### 安裝virtual environment
```shell
$ pip install virtualenv
```

#### 建立虛擬環境
```shell
$ virtualenv venv
```

#### 啟動虛擬環境
在 Windows 系統中，使用：
```shell
venv\Scripts\activate.bat
```
在 Unix 或 MacOS 系統，使用：
```shell
$ source venv/bin/activate
```

#### 安裝需要的module
```shell
$ pip install -r requirements.txt
```

#### 初始化migrati
````shell
$ flask db init
$ flask db migrate -m "commit message"
$ flask db upgrade
````

#### 啟動
```shell
$ gunicorn wsgi:app
$ gunicorn --bind=0.0.0.0:5000 wsgi:app # 指定host以及port
```

#### 測試用的啟動, 程式更動時會重啟
```shell
$ gunicorn --reload wsgi:app
```

## Configuration
因個人電腦設定的不同, 請自行在Stocker資料夾下建立一個```critical_flie```資料夾
並放上兩個檔案
- databaseAccount.json
- serverConfig.json

格式如下
databaseAccount.json
```js
{
    "username": $USERNAME,
    "password": $PASSWORD,
    "ip": $DATABASE_IP
}
```
serverConfig.json
```js
{
    "ip": $IP,
    "port": $PORT
}
```
**$** 請自行填上個人電腦上的設定

## License
MIT