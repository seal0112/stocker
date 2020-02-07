from crawler import (
    crawlBasicInformation, crawlMonthlyRevenue,
    crawlBalanceSheet, crawlIncomeSheet, crawlCashFlow,
    crawlSummaryStockNoFromTWSE, crawlerDailyPrice
)
from datetime import datetime
import json
import requests
import time
import random
import math
import sys
import traceback
import logging
from logging.handlers import TimedRotatingFileHandler

with open('./critical_flie/serverConfig.json') as configReader:
    serverConf = json.loads(configReader.read())

companyTypes = ['sii', 'otc', 'rotc', 'pub']


# logging setting
log_filename = datetime.now().strftime("log/crawler %Y-%m-%d.log")
fileHandler = TimedRotatingFileHandler(
    log_filename, when='D', interval=1,
    backupCount=30, encoding='UTF-8', delay=False, utc=False)
logger = logging.getLogger()
BASIC_FORMAT = '%(asctime)s %(levelname)- 8s in %(module)s: %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)


# done
def getBasicInfo(dataType='sii'):
    # dataType: otc, sii, rotc, pub
    data = crawlBasicInformation(dataType)
    data = transformHeaderNoun(data, 'basic_information')

    for i in range(len(data)):
        dataPayload = json.loads(
            data.iloc[i].to_json(force_ascii=False))
        dataPayload['type'] = dataType
        url = "http://%s:%s/api/v0/basic_information/%s" % (
            serverConf['ip'],
            serverConf['port'],
            dataPayload['id'])
        res = requests.post(url, data=json.dumps(dataPayload))
        print('(' + str(i) + '/' + str(len(data)) + ')', end=' ')
        print(dataPayload['id'], end=' ')
        print(res)
        time.sleep(0.05)


# done
def transformHeaderNoun(data, fileName):
    """this method is used to transefer header noun.

    Use receive fileName to get noun_conversion file,
    and use direction going to decide to replace the columns or index.

    Args:
        data: dataframe from crawler.
        file: a string of noun_conversion file.

    Return:
        dataframe

    Raises:
        Exception: An error occurred.
    """
    if data is None:
        return {}

    direction = {
        "basic_information": "columns",
        "month_revenue": "columns",
        "income_sheet": "index",
        "balance_sheet": "index",
        "cashflow": "index"
    }

    with open(
            './noun_conversion/%s.json' % fileName,
            encoding='utf-8') as converFile:
        nounConvers = json.loads(converFile.read())

    if direction[fileName] == 'columns':
        headers = data.columns
    elif direction[fileName] == 'index':
        headers = data.index

    # 讀取noun_conversion時請記得使用 if key in dict 檢查是否需要替換key值
    new_headers = []
    for idx, header in enumerate(headers):
        if nounConvers.get(header) is not None:
            new_headers.append(nounConvers.get(header))
        else:
            new_headers.append(header)

    if direction[fileName] == 'columns':
        data.columns = new_headers
    elif direction[fileName] == 'index':
        data.index = new_headers

    return data


# done
def getMonthlyRevenue(westernYearIn=2013, monthIn=1):
    # year, month: start at 2013, 1
    data = crawlMonthlyRevenue(westernYearIn, monthIn)
    data = transformHeaderNoun(data, 'month_revenue')

    for i in range(len(data)):
        dataPayload = json.loads(data.iloc[i].to_json(force_ascii=False))
        dataPayload['year'] = westernYearIn
        dataPayload['month'] = str(monthIn)
        url = "http://%s:%s/api/v0/month_revenue/%s" % (
            serverConf['ip'],
            serverConf['port'],
            str(dataPayload['stock_id']))
        res = requests.post(url, data=json.dumps(dataPayload))
        print('(' + str(i) + '/' + str(len(data)) + ')', end=' ')
        print(dataPayload['stock_id'], end=' ')
        print(str(westernYearIn) + "-" + str(monthIn), end=' ')
        print(res)
        time.sleep(0.05)


# done
def getIncomeSheet(companyID=1101, westernYearIn=2019, seasonIn=1):
    try:
        data = crawlIncomeSheet(companyID, westernYearIn, seasonIn)
    except ConnectionError as ce:
        return {"stock_id": companyID, "status": ce.args[0]}
    except IndexError:
        return {"stock_id": companyID, "status": 'IndexError'}
    except Exception as e:
        return {"stock_id": companyID, "status": e.args[0]}

    data = transformHeaderNoun(data, 'income_sheet')

    dataPayload = {}
    # Key-select is used to select the data to be saved.
    with open(
            './data_key_select/income_sheet_key_select.txt',
            encoding='utf-8') as income_sheet_key_select:
        incomeSheetKeySel = set(
            line.strip() for line in income_sheet_key_select)

    # ratioIgnore is used to ignore the proportion of data
    # that does not need to be stored in the database.
    ratioIgnore = set(["營業收入合計", "營業成本合計", "營業外收入及支出合計"])

    # if the key is in key_select file, then put data into datapayload
    # if key need to store ration,
    # key+'率' becomes the new key value for store
    for key in incomeSheetKeySel:
        try:
            if key in data.index:
                dataPayload[key] = data.loc[key][0]
                if not math.isnan(data.loc[key][1])\
                        and key not in ratioIgnore:
                    dataPayload[key+'率'] = round(data.loc[key][1], 2)
            else:
                dataPayload[key] = None
        except Exception as ex:
            print(ex)

    if seasonIn == 4:
        preSeasonsData = []
        for season in range(1, 4):
            time.sleep(4 + random.randrange(0, 2))
            preDataPayload = {}
            preData = crawlIncomeSheet(companyID, westernYearIn, season)
            preData = transformHeaderNoun(preData, 'income_sheet')
            for key in incomeSheetKeySel:
                try:
                    if key in preData.index:
                        preDataPayload[key] = preData.loc[key][0]
                    else:
                        preDataPayload[key] = None
                except Exception as ex:
                    print(ex)
            preSeasonsData.append(preDataPayload)

        for preSeasonData in preSeasonsData:
            for key in preSeasonData.keys():
                if preSeasonData[key] is not None:
                    dataPayload[key] -= preSeasonData[key]

        for key in dataPayload.keys():
            if '率' in key:
                dataPayload[key] = round((dataPayload[
                    key.replace('率', '')]/dataPayload['營業收入合計'])*100, 2)
        print(dataPayload)

    dataPayload['year'] = westernYearIn
    dataPayload['season'] = str(seasonIn)

    incomeSheetApi = "http://%s:%s/api/v0/income_sheet/%s" % (
            serverConf['ip'],
            serverConf['port'],
            str(companyID))
    res = requests.post(incomeSheetApi, data=json.dumps(dataPayload))

    return {"stock_id": companyID, "status": "ok"}


# done
def updateIncomeSheet(westernYearIn=2019, season=1):
    existStockNo = getSummaryStockNoServerExist(
        westernYearIn, season, 'income_sheet')
    validStockNo = getStockNoBasicInfo()

    crawlList = []
    for companyType in companyTypes:
        targetStockNo = crawlSummaryStockNoFromTWSE(
            'income_sheet', companyType, westernYearIn, season)
        if len(targetStockNo) == 0:
            continue
        if len(existStockNo) != 0:
            for no in targetStockNo:
                if str(no) not in existStockNo and\
                   str(no) in validStockNo:
                    crawlList.append(no)
        else:
            crawlList.extend(targetStockNo)

    total = len(crawlList)
    exceptList = []

    for idx, stock in enumerate(crawlList):
        print("(" + str(idx) + "/" + str(total) + ")", end=' ')
        crawlerResult = getIncomeSheet(stock, westernYearIn, season)
        print(crawlerResult['stock_id'], crawlerResult['status'])
        if crawlerResult["status"] == 'IndexError':
            time.sleep(60)
        if crawlerResult["status"] != 'ok':
            exceptList.append({
                "stock_id": crawlerResult["stock_id"],
                "retry_times": 0
            })
        time.sleep(3.5 + random.randrange(0, 2))

    while(len(exceptList)):
        reCrawler = getIncomeSheet(
            exceptList[0]["stock_id"], westernYearIn, season)
        if reCrawler["status"] == 'ok':
            del exceptList[0]
        elif exceptList[0]["retry_times"] == 2:
            print("cancel stock_id: %s, retry over 3 times."
                  % reCrawler["stock_id"])
            del exceptList[0]
        else:
            tmpStock = exceptList.pop(0)
            tmpStock["retry_times"] = tmpStock["retry_times"]+1
            exceptList.append(tmpStock)
        time.sleep(3.5 + random.randrange(0, 2))


# need to update feature
def updateDailyPrice(type='sii'):
    stockNumsApi = 'http://%s:%s/api/v0/stock_number?type=%s' % (
        serverConf['ip'], serverConf['port'], type)
    stockNums = json.loads(requests.get(stockNumsApi).text)

    serverDailyInfoApi = "http://%s:%s/api/v0/daily_information/" % (
        serverConf['ip'], serverConf['port'])

    for i in range(0, len(stockNums), 10):
        data = crawlerDailyPrice(stockNums[i:i+10], type)
        for d in data:
            res = requests.post(
                "%s%s" % (serverDailyInfoApi, d['stock_id']),
                data=json.dumps(d))
        time.sleep(1.5)


# done
def getBalanceSheet(
        companyID=2330, westernYearIn=2019, seasonIn=2):
    data = crawlBalanceSheet(companyID, westernYearIn, seasonIn)
    data = transformHeaderNoun(data, "balance_sheet")

    dataPayload = {}
    with open(
            './data_key_select/balance_sheet_key_select.txt',
            encoding='utf-8') as balance_sheet_key_select:
        balanceSheetKeySel = set(
            line.strip() for line in balance_sheet_key_select)

    for key in balanceSheetKeySel:
        try:
            if key in data.index:
                dataPayload[key] = data.loc[key][0]
            else:
                dataPayload[key] = None
        except Exception as ex:
            print(ex)

    dataPayload['year'] = westernYearIn
    dataPayload['season'] = str(seasonIn)

    balanceSheetApi = "http://%s:%s/api/v0/balance_sheet/%s" % (
        serverConf['ip'],
        serverConf['port'],
        str(companyID))
    res = requests.post(balanceSheetApi, data=json.dumps(dataPayload))
    print(res)


def updateBalanceSheet(westernYearIn=2019, season=1):
    existStockNo = getSummaryStockNoServerExist(
        westernYearIn, season, 'balance_sheet')
    validStockNo = getStockNoBasicInfo()

    crawlList = []
    for companyType in companyTypes:
        targetStockNo = crawlSummaryStockNoFromTWSE(
            'balance_sheet', companyType, westernYearIn, season)
        if len(targetStockNo) == 0:
            continue
        if len(existStockNo) != 0:
            for no in targetStockNo:
                if str(no) not in existStockNo and\
                   str(no) in validStockNo:
                    crawlList.append(no)
        else:
            crawlList.extend(targetStockNo)

    total = len(crawlList)
    idx = 0
    for stock in crawlList:
        print("(" + str(idx) + "/" + str(total) + ")", end=' ')
        getBalanceSheet(stock, westernYearIn, season)
        time.sleep(3 + random.randrange(0, 4))
        idx = idx + 1


# done
def getCashFlow(
        companyID=2330, westernYearIn=2019, seasonIn=2):
    try:
        data = crawlCashFlow(companyID, westernYearIn, seasonIn)
    except Exception as e:
        return {"stock_id": companyID, "status": e.args[0]}

    data = transformHeaderNoun(data, "cashflow")

    # print(data)
    dataPayload = {}
    with open(
            './data_key_select/cashflow_key_select.txt',
            encoding='utf-8') as cashflow_key_select:
        cashflowKeySel = set(
            line.strip() for line in cashflow_key_select)

    for key in cashflowKeySel:
        try:
            if key in data.index:
                dataPayload[key] = int(data.loc[key][0])
            else:
                dataPayload[key] = None
        except KeyError as ke:
            if ke.args[0] == 0:
                dataPayload[key] = int(data.loc[key].iloc[0])
        except Exception as ex:
            # print(ex.__class__.__name__)
            # print(sys.exc_info())
            # raise ex
            return {"stock_id": companyID, "status": ex.__class__.__name__}
            # TODO: write into log file

    dataPayload['year'] = westernYearIn
    dataPayload['season'] = str(seasonIn)

    cashflowApi = "http://%s:%s/api/v0/cash_flow/%s" % (
        serverConf['ip'],
        serverConf['port'],
        str(companyID))

    idx = 0
    while(True):
        try:
            res = requests.post(cashflowApi, data=json.dumps(dataPayload))
            break
        except Exception as ex:
            if idx == 5:
                print("Retry fail exceed %d times, abort." % (idx+1))
                res = ""
                break
            else:
                print(ex.__class__.__name__)
                time.sleep(10)

    print(res, end=" ")

    return {"stock_id": companyID, "status": "ok"}


def updateCashFlow(westernYearIn=2019, season=1):
    existStockNo = getSummaryStockNoServerExist(
        westernYearIn, season, 'cashflow')
    validStockNo = getStockNoBasicInfo()
    print("\t" + str(len(existStockNo)) + " existing stocks")

    crawlList = []
    for companyType in companyTypes:
        targetStockNo = crawlSummaryStockNoFromTWSE(
            'balance_sheet', companyType, westernYearIn, season)
        if len(targetStockNo) == 0:
            continue
        if len(existStockNo) != 0:
            for no in targetStockNo:
                if str(no) not in existStockNo and\
                   str(no) in validStockNo:
                    crawlList.append(no)
        else:
            crawlList.extend(targetStockNo)

    total = len(crawlList)
    print("\t" + str(total) + " stocks to update")
    exceptList = []

    for idx, stock in enumerate(crawlList):
        print("(" + str(idx) + "/" + str(total) + ")" + str(stock), end=' ')
        crawlerResult = getCashFlow(stock, westernYearIn, season)
        print(crawlerResult['status'])
        if crawlerResult["status"] == "IndexError":
            time.sleep(60)
        if crawlerResult["status"] != "ok":
            exceptList.append({
                "stock_id": crawlerResult["stock_id"],
                "retry_times": 0
            })
        time.sleep(4 + random.randrange(0, 4))

    while(len(exceptList)):
        # print("(len=" + str(len(exceptList)) + ")", end=" ")
        print("Retry " + str(exceptList[0]["stock_id"])
              + " " + str(exceptList[0]["retry_times"]), end=" ")
        reCrawler = getCashFlow(
            exceptList[0]["stock_id"], westernYearIn, season)
        if reCrawler["status"] == "ok":
            print("ok")
            del exceptList[0]
        elif exceptList[0]["retry_times"] == 2:
            print("cancel stock_id: %s, retry over 3 times."
                  % reCrawler["stock_id"])
            logger.error("cancel stock_id: %s in %s-%s, retry exceeded."
                         % (reCrawler["stock_id"], westernYearIn, season))
            del exceptList[0]
        else:
            print("retry")
            tmpStock = exceptList.pop(0)
            tmpStock["retry_times"] = tmpStock["retry_times"]+1
            exceptList.append(tmpStock)
        time.sleep(4 + random.randrange(0, 4))


# done
def getSummaryStockNoServerExist(
        westernYearIn=2019, seasonIn=2, reportType='balance_sheet'):
    url = "http://%s:%s/api/v0/stock_number" % (
        serverConf['ip'],
        serverConf['port'])
    payload = {}
    payload['year'] = westernYearIn
    payload['season'] = seasonIn
    payload['reportType'] = reportType
    print("exist " + reportType + " " +
          str(westernYearIn) + "Q" + str(seasonIn), end='...')
    res = requests.post(url, data=json.dumps(payload))
    print("done.")
    return json.loads(res.text)


def getStockNoBasicInfo():
    url = "http://%s:%s/api/v0/stock_number" % (
        serverConf['ip'], serverConf['port'])
    print('Basic Infomation', end='...')
    res = requests.get(url)
    print("done.")
    return json.loads(res.text)


def dailyRoutineWork():
    # 差財報三表, shareholder可以禮拜六抓
    for type in companyTypes:
        getBasicInfo(type)

    updateDailyPrice('sii')
    updateDailyPrice('otc')

    now = datetime.now()
    print(now.year, now.month-1)
    if now.month-1 == 0:
        getMonthlyRevenue(now.year-1, 12)
    else:
        getMonthlyRevenue(now.year, now.month-1)

    updateIncomeSheet(2019, 4)


if __name__ == '__main__':
    '''
    usage: get basic information
    '''
    # getBasicInfo('sii')
    # getBasicInfo('otc')
    # getBasicInfo('rotc')
    # getBasicInfo('pub')

    '''
    usage: get monthly revenue
    '''
    # for year in range(2018,2012,-1):
    #     for i in range(12,0,-1):
    #         getMonthlyRevenue(year, i)

    '''
    usage: update incomeSheet/BalanceSheet
    '''
    # years = [2019]
    # seasons = [2, 1]

    # for year in years:
    #     for season in seasons:
    #         # updateIncomeSheet(year, season)
    #         # updateBalanceSheet(year, season)
    #         UpdateCashFlow(year, season)

    # years = [2015, 2014, 2013, 2012]
    # seasons = [1, 2, 3, 4]
    # for year in years:
    #     for season in seasons:
    #         updateCashFlow(year, season)

    # start = datetime.now()
    # year = 2013
    # reportType = 'income_sheet'
    # seasons = [1, 2, 3, 4]

    # for season in seasons:
    # updateIncomeSheet(2018, 4)

    # end = datetime.now()
    # print("start time: " + str(start))
    # print("end time: " + str(end))
    # print("time elapse: " + str(end-start))

    # getIncomeSheet(3443, 2019, 4)
    # getBalanceSheet(2337, 2019, 2)

    # getCashFlow()
    # updateDailyPrice('sii')

    dailyRoutineWork()
