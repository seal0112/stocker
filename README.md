# Stocker

## Crawler and Back-End for Taiwan stocks
Stocker是一個使用```爬蟲(Crawler)```抓取台灣上市櫃股票財報並使用```後端程式(Flask)```存入資料庫(MariaDB)的專案，資料庫的選用可以依照個人喜好選擇其他SQL類型資料庫

## Prerequisites

請事先安裝好python3以及SQL database
- [python3](https://www.python.org/downloads/)
- [SQL (MySQl, PostgreSQL)]()

## Installation


```shell
$ git clone https://github.com/seal0112/stocker.git
$ cd stocker/
```

#### 安裝virtual environment
```shell
$ pip3 install virtualenv
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

#### 啟動
```shell
$ python3 stocker.py
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