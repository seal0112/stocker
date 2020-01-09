from crawler import (
    crawlBasicInformation, crawlMonthlyRevenue,
    crawlBalanceSheet, crawlIncomeSheet, crawlCashFlow,
    crawlSummaryReportStockNo
)
from datetime import datetime
import json
import requests
import time
import random
import math


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
            "http://127.0.0.1:5000/api/v0/basic_information/%s"\
            % dataPayload['id']
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
        "income_sheet": "index"
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
    data = crawlIncomeSheet(companyID, westernYearIn, seasonIn)
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


# done
def UpdateIncomeSheet(westernYearIn=2019, season=1):
    companyTypes = ['sii', 'otc', 'rotc', 'pub']

    existStockNo = getSummaryStockNoServerExist(year, season, 'income_sheet')
    validStockNo = getStockNoBasicInfo()

    crawlList = []
    for companyType in companyTypes:
        targetStockNo = getSummaryStockNoTarget('income_sheet', companyType,
                                                year, season)
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
        getIncomeSheet(stock, year, season)
        time.sleep(3 + random.randrange(0, 4))
        idx = idx + 1


# TODO
def getBalanceSheet(
        companyID=2330, westernYearIn=2019, seasonIn=2):
    pass


# TODO
def getCashFlow(
        companyID=2330, westernYearIn=2019, seasonIn=2):
    pass


# done
def getSummaryStockNoServerExist(
        westernYearIn=2019, seasonIn=2, reportType='balance_sheet'):
    url = "http://127.0.0.1:5000/api/v0/stock_number"
    payload = {}
    payload['year'] = westernYearIn
    payload['season'] = seasonIn
    payload['reportType'] = reportType
    print("exist " + reportType + " " +
          str(year) + "Q" + str(seasonIn), end='...')
    res = requests.post(url, data=json.dumps(payload))
    print("done.")
    return json.loads(res.text)


# done
def getSummaryStockNoTarget(
        reportTypes='income_sheet', companyType='sii',
        westernYearIn=2019, seasonIn=3):
    return crawlSummaryReportStockNo(reportTypes, companyType,
                                     westernYearIn, seasonIn)


def getStockNoBasicInfo():
    url = "http://127.0.0.1:5000/api/v0/stock_number"
    print('basic info', end='...')
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
    getMonthlyRevenue(2019, 12)

    '''
    usage: update incomeSheet/BalanceSheet
    '''
    # start = datetime.now()
    # year = 2013
    # reportType = 'income_sheet'
    # seasons = [1, 2, 3, 4]

    # for season in seasons:
    #     UpdateIncomeSheet(year, season)

    # end = datetime.now()
    # print("start time: " + str(start))
    # print("end time: " + str(end))
    # print("time elapse: " + str(end-start))

    # getIncomeSheet(1101, 2013, 2)
    # getBalanceSheet(2337, 2019, 2)
    # getCashFlow()
