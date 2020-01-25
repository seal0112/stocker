from crawler import (
    crawlBasicInformation, crawlMonthlyRevenue,
    crawlBalanceSheet, crawlIncomeSheet, crawlCashFlow,
    crawlSummaryReportStockNo, crawlerDailyPrice
)
from datetime import datetime
import json
import requests
import time
import random
import math

with open('./critical_flie/serverConfig.json') as configReader:
    serverConf = json.loads(configReader.read())


# done
def getBasicInfo(dataType='sii'):
    # dataType: otc, sii, rotc, pub
    data = crawlBasicInformation(dataType)
    data = transformHeaderNoun(data, 'basic_information')

    for i in range(len(data)):
        dataPayload = json.loads(
            data.iloc[i].to_json(force_ascii=False))
        dataPayload['type'] = dataType
        url = \
            "http://%s:%s/api/v0/basic_information/%s"\
            % (serverConf['ip'], serverConf['port'], dataPayload['id'])
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
        url = "http://127.0.0.1:5000/api/v0/month_revenue/%s" % str(
            dataPayload['stock_id'])
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
    except IndexError as ie:
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

    dataPayload['year'] = westernYearIn
    dataPayload['season'] = str(seasonIn)

    incomeSheetApi = "http://127.0.0.1:5000/api/v0/income_sheet/%s" % str(
            companyID)
    res = requests.post(incomeSheetApi, data=json.dumps(dataPayload))
    print(res)

    return {"stock_id": companyID, "status": "ok"}


# done
def updateIncomeSheet(westernYearIn=2019, season=1):
    companyTypes = ['sii', 'otc', 'rotc', 'pub']

    existStockNo = getSummaryStockNoServerExist(
        westernYearIn, season, 'income_sheet')
    validStockNo = getStockNoBasicInfo()

    crawlList = []
    for companyType in companyTypes:
        targetStockNo = getSummaryStockNoFromTWSE('income_sheet', companyType,
                                                westernYearIn, season)
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
            print("cancel stock_id: %s, retry over 3 times." % reCrawler["stock_id"])
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

    for i in range(0,len(stockNums),10):
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

    balanceSheetApi = "http://127.0.0.1:5000/api/v0/balance_sheet/%s" % str(
        companyID)
    res = requests.post(balanceSheetApi, data=json.dumps(dataPayload))
    print(res)


def updateBalanceSheet(westernYearIn=2019, season=1):
    companyTypes = ['sii', 'otc', 'rotc', 'pub']

    existStockNo = getSummaryStockNoServerExist(
        westernYearIn, season, 'balance_sheet')
    validStockNo = getStockNoBasicInfo()

    crawlList = []
    for companyType in companyTypes:
        targetStockNo = getSummaryStockNoFromTWSE('balance_sheet', companyType,
                                                westernYearIn, season)
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
    data = crawlCashFlow(companyID, westernYearIn, seasonIn)
    data = transformHeaderNoun(data, "cashflow")

    print(data)
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
        except Exception as ex:
            print(ex)

    dataPayload['year'] = westernYearIn
    dataPayload['season'] = str(seasonIn)

    cashflowApi = "http://127.0.0.1:5000/api/v0/cash_flow/%s" % str(
        companyID)
    # print(dataPayload)
    res = requests.post(cashflowApi, data=json.dumps(dataPayload))
    print(res)


def updateCashFlow(westernYearIn=2019, season=1):
    companyTypes = ['sii', 'otc', 'rotc', 'pub']

    existStockNo = getSummaryStockNoServerExist(
        westernYearIn, season, 'cashflow')
    validStockNo = getStockNoBasicInfo()
    print("\t" + str(len(existStockNo)) + " existing stocks")

    crawlList = []
    for companyType in companyTypes:
        targetStockNo = getSummaryStockNoFromTWSE('balance_sheet', companyType,
                                                westernYearIn, season)
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
    # print(crawlList)
    print("\t" + str(total) + " stocks to update")
    idx = 0
    for stock in crawlList:
        print("(" + str(idx) + "/" + str(total) + ")" + str(stock), end=' ')
        getCashFlow(stock, westernYearIn, season)
        time.sleep(3 + random.randrange(0, 4))
        idx = idx + 1


# done
def getSummaryStockNoServerExist(
        westernYearIn=2019, seasonIn=2, reportType='balance_sheet'):
    url = "http://127.0.0.1:5000/api/v0/stock_number"
    payload = {}
    payload['year'] = westernYearIn
    payload['season'] = seasonIn
    payload['reportType'] = reportType
    print("exist " + reportType + " " +
          str(westernYearIn) + "Q" + str(seasonIn), end='...')
    res = requests.post(url, data=json.dumps(payload))
    print("done.")
    return json.loads(res.text)


# done
def getSummaryStockNoFromTWSE(
        reportTypes='income_sheet', companyType='sii',
        westernYearIn=2019, seasonIn=3):
    return crawlSummaryReportStockNo(reportTypes, companyType,
                                     westernYearIn, seasonIn)


def getStockNoBasicInfo():
    url = "http://127.0.0.1:5000/api/v0/stock_number"
    print('Basic Infomation', end='...')
    res = requests.get(url)
    print("done.")
    return json.loads(res.text)


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
    for i in range(12,0,-1):
        getMonthlyRevenue(2018, i)

    '''
    usage: update incomeSheet/BalanceSheet
    '''
    # years = [2019]
    # seasons = [3,2,1]

    # for year in years:
    #     for season in seasons:
    #         # UpdateIncomeSheet(year, season)
    #         # UpdateBalanceSheet(year, season)
    #         UpdateCashFlow(year, season)
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

    # getIncomeSheet(1101, 2013, 2)
    # getBalanceSheet(2337, 2019, 2)
    # getCashFlow(4439,2019,3)

    # updateDailyPrice('sii')

