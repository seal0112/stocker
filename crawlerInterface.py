from crawler import (
    crawlBasicInformation, crawlMonthlyRevenue,
    crawlBalanceSheet, crawlIncomeSheet, crawlCashFlow,
    crawlSummaryStockNoFromTWSE, crawlDailyPrice,
    crawlStockCommodity, crawlDelistedCompany
)
from datetime import datetime, timedelta
import json
import requests
import time
import random
import math
import sys
import traceback
import logging
from logging.handlers import TimedRotatingFileHandler
import pandas as pd

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


def getBasicInfo(dataType='sii'):
    # dataType: otc, sii, rotc, pub
    while(True):
        try:
            data = crawlBasicInformation(dataType)
            break
        except Exception as ex:
            print(ex.__class__.__name__, end=" ")
            print("catched. Retrying.")
            continue

    data = transformHeaderNoun(data, 'basic_information')

    for i in range(len(data)):
        dataPayload = json.loads(
            data.iloc[i].to_json(force_ascii=False))
        dataPayload['exchangeType'] = dataType
        url = "http://%s:%s/api/v0/basic_information/%s" % (
            serverConf['ip'],
            serverConf['port'],
            dataPayload['id'])
        res = requests.post(url, data=json.dumps(dataPayload))
        # print('(' + str(i) + '/' + str(len(data)) + ')', end=' ')
        # print(dataPayload['id'], end=' ')
        # print(res)
        # time.sleep(0.05)


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
        # print('(' + str(i) + '/' + str(len(data)) + ')', end=' ')
        # print(dataPayload['stock_id'], end=' ')
        # print(str(westernYearIn) + "-" + str(monthIn), end=' ')
        # print(res)
        # time.sleep(0.05)


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
                if key == "母公司業主淨利":
                    if isinstance(data.loc[key], pd.DataFrame):
                        dataPayload[key] = data.loc[key].iloc[0][0]
                    else:
                        dataPayload[key] = data.loc[key][0]
                else:
                    dataPayload[key] = data.loc[key][0]
                    if not math.isnan(data.loc[key][1])\
                            and key not in ratioIgnore:
                        dataPayload[key+'率'] = round(data.loc[key][1], 2)
            else:
                dataPayload[key] = None
        except Exception as ex:
            print(key)
            print(ex)

    if "母公司業主淨利" not in dataPayload or dataPayload["母公司業主淨利"] is None:
        if "母公司業主淨利" not in data:
            dataPayload["母公司業主淨利"] = dataPayload["本期淨利"]
        elif len(data.loc["母公司業主淨利"]) >= 2:
            dataPayload["母公司業主淨利"] = data.loc["母公司業主淨利"].iloc[0][0]

    # print(dataPayload)
    # The fourth quarter financial statements are annual reports
    # So we must use the data from the first three quarters to subtract them
    # to get the fourth quarter single-quarter financial report.
    if seasonIn == 4:
        preSeasonsData = []
        for season in range(1, 4):
            preData = getFinStatFromServer(
                companyID, westernYearIn, season, 'income_sheet')
            if preData is not None:
                preSeasonsData.append(preData[0])

        for preSeasonData in preSeasonsData:
            for key in incomeSheetKeySel:
                if dataPayload[key] is None:
                    continue
                elif preSeasonData[key] is not None:
                    dataPayload[key] -= preSeasonData[key]

        # Recalculate percentage of specific value
        for key in dataPayload.keys():
            if '率' in key:
                if dataPayload['營業收入合計'] == 0:
                    dataPayload[key] = 0
                elif dataPayload['營業收入合計'] is None:
                    dataPayload[key] = None
                else:
                    dataPayload[key] = round((dataPayload[
                        key.replace('率', '')]/dataPayload['營業收入合計'])*100, 2)

        basicInfoUrl = "http://%s:%s/api/v0/basic_information/%s" % (
            serverConf['ip'], serverConf['port'], companyID)

        basicInfo = requests.get(basicInfoUrl)

        if basicInfo.status_code != 404:
            basicInfoData = json.loads(basicInfo.text)
            if basicInfoData["已發行普通股數或TDR原發行股數"] != 0:
                dataPayload["基本每股盈餘"] = round(
                    dataPayload["母公司業主淨利"]*1000/
                    basicInfoData["已發行普通股數或TDR原發行股數"], 2)

    dataPayload['year'] = westernYearIn
    dataPayload['season'] = str(seasonIn)

    incomeSheetApi = "http://%s:%s/api/v0/income_sheet/%s" % (
            serverConf['ip'],
            serverConf['port'],
            str(companyID))
    res = requests.post(incomeSheetApi, data=json.dumps(dataPayload))

    if res.status_code == 201:
        return {"stock_id": companyID, "status": "ok"}
    else:
        return {"stock_id": companyID, "status": res.status_code}


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
def updateDailyPrice(datetimeIn=datetime.now()):
    # now = datetime.now() - timedelta(days=1)
    # now = datetime(2020,4,15)
    data = crawlDailyPrice(datetimeIn)

    stockTypes = ['sii', 'otc']
    for stockType in stockTypes:
        stockNumsApi = 'http://%s:%s/api/v0/stock_number?type=%s' % (
            serverConf['ip'], serverConf['port'], stockType)
        stockIDs = json.loads(requests.get(stockNumsApi).text)

        for id in stockIDs:
            if stockType == 'sii':
                colCol = '證券代號'
                priceCol = '收盤價'
                priceDiffCol = '漲跌價差'
                priceDiffSignCol = '漲跌(+/-)'
            elif stockType == 'otc':
                colCol = '代號'
                priceCol = '收盤'
                priceDiffCol = '漲跌'

            try:
                dataStock = data[stockType].loc[
                    data[stockType][colCol] == id]
            except:
                break

            dailyInfoApi = 'http://%s:%s/api/v0/daily_information/%s' % (
                serverConf['ip'], serverConf['port'], id)
            dataPayload = {}

            try:
                dataPayload['本日收盤價'] = float(dataStock[priceCol].iloc[0])

                # otc have no priceDiffSignCol column
                if stockType == 'sii':
                    if dataStock[priceDiffSignCol].iloc[0] == '除息':
                        dataPayload['本日漲跌'] = 0
                    elif dataStock[priceDiffSignCol].iloc[0] == '-':
                        dataPayload['本日漲跌'] = float(dataStock[priceDiffCol].iloc[0] * -1)
                    else:
                        dataPayload['本日漲跌'] = float(dataStock[priceDiffCol].iloc[0])
                else:
                    dataPayload['本日漲跌'] = float(dataStock[priceDiffCol].iloc[0])
            except ValueError as ve:
                print("%s get into ValueError with %s"% (id, ve))
            except IndexError as ie:
                print("%s get into IndexError with %s"% (id, ie))
            except Exception as ex:
                print(ex)
                print(id)
                print(dataStock)
                print("!!!!!!!!!!!!!!!!!")
            else:
                requests.post(dailyInfoApi, data=json.dumps(dataPayload))


def getBalanceSheet(
        companyID=2330, westernYearIn=2019, seasonIn=2):
    try:
        data = crawlBalanceSheet(companyID, westernYearIn, seasonIn)
    except ConnectionError as ce:
        return {"stock_id": companyID, "status": ce.args[0]}
    except IndexError:
        return {"stock_id": companyID, "status": 'IndexError'}
    except Exception as e:
        return {"stock_id": companyID, "status": e.args[0]}

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

    if res.status_code == 201:
        return {"stock_id": companyID, "status": "ok"}
    else:
        return {"stock_id": companyID, "status": res.status_code}


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
    exceptList = []

    for idx, stock in enumerate(crawlList):
        print("(" + str(idx) + "/" + str(total) + ")", end=' ')
        crawlerResult = getBalanceSheet(stock, westernYearIn, season)
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
        reCrawler = getBalanceSheet(
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


def updateDelistedCompany():
    companyTypes = ['sii', 'otc']
    for companyType in companyTypes:
        data = crawlDelistedCompany(companyType)
        for d in data:
            serverBasicInfoApi = "http://%s:%s/api/v0/basic_information/%s" % (
                serverConf['ip'], serverConf['port'], d)
            requests.patch(serverBasicInfoApi)


def updateStockCommodity():
    data = crawlStockCommodity()
    serverStockCommodityApi = "http://%s:%s/api/v0/stock_commodity/" % (
        serverConf['ip'], serverConf['port'])
    for index, row in data.iterrows():
        dataPayload = {}
        if row["標準型證券股數"] in [2000, 100]:
            if row["標準型證券股數"] == 2000:
                dataPayload["stock_future"] = row["是否為股票期貨標的"]==u"\u25CF"
                dataPayload["stock_option"] = row["是否為股票選擇權標的"]==u"\u25CF"
            elif row["標準型證券股數"] == 100:
                dataPayload["small_stock_future"] = row["是否為股票期貨標的"]==u"\u25CF"

            dataPayload["stock_id"] = row["證券代號"]
            res = requests.post(
                    "%s%s" % (serverStockCommodityApi, dataPayload['stock_id']),
                    data=json.dumps(dataPayload))


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


def getFinStatFromServer(
        stock_id,
        westernYear,
        season,
        reportTypes='income_sheet',):
    finStatApi = "http://%s:%s/api/v0/%s/%s?mode=single&year=%s&season=%s" % (
        serverConf['ip'], serverConf['port'], reportTypes,
        stock_id, westernYear, season)

    data = requests.get(finStatApi)
    if data.status_code == 404:
        return None
    else:
        return data.json()


def dailyRoutineWork():
    # 差財報三表, shareholder可以禮拜六抓
    for type in companyTypes:
        getBasicInfo(type)
    updateDelistedCompany()
    updateStockCommodity()

    updateDailyPrice()

    now = datetime.now()
    if now.month-1 == 0:
        getMonthlyRevenue(now.year-1, 12)
    else:
        getMonthlyRevenue(now.year, now.month-1)

    updateIncomeSheet(2020, 1)


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
    # '''
    # for year in range(2019, 2012, -1):
    #     for i in range(12, 0, -1):
    #         getMonthlyRevenue(year, i)

    '''
    usage: update incomeSheet/BalanceSheet
    '''
    # years = [2019]
    # seasons = [1, 2, 3, 4]

    # for year in range(2017, 2012, -1):
    #     for season in seasons:
    #         updateIncomeSheet(year, season)

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
    dailyRoutineWork()
