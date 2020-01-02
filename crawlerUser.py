from crawler import crawlBasicInformation
from crawler import crawlBalanceSheet
from crawler import crawlCashFlow
from crawler import crawlIncomeSheet
from crawler import crawlMonthlyRevenue
from crawler import crawlSummaryReportStockNo
import datetime
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

    """# API(v0): basic_information test case
    payload = {
            "id": "1101",
            "公司名稱": "台灣水泥股份有限公司",
            "公司簡稱": "台泥",
            "產業類別": "水泥工業",
            "外國企業註冊地國": "－",
            "住址": "台北市中山北路2段113號",
            "營利事業統一編號": "11913502",
            "董事長": "張安平",
            "總經理": "李鐘培",
            "發言人": "黃健強",
            "發言人職稱": "資深副總經理",
            "代理發言人": "蔡立文",
            "總機電話": "(02)2531-7099",
            "成立日期": "39/12/29",
            "上市上櫃興櫃公開發行日期": "51/02/09",
            "普通股每股面額": "新台幣 10.0000元",
            "實收資本額": 56656192040,
            "已發行普通股數或TDR原發行股數": 5465619204,
            "私募普通股": 0,
            "特別股": 200000000,
            "編製財務報告類型": "合併",
            "普通股盈餘分派或虧損撥補頻率": "每年",
            "普通股年度現金股息及紅利決議層級": "股東會",
            "股票過戶機構": "中國信託商業銀行代理部",
            "過戶電話": "66365566",
            "過戶地址": "台北市重慶南路一段83號5樓",
            "簽證會計師事務所": "勤業眾信聯合會計師事務所",
            "簽證會計師一": "翁雅玲",
            "簽證會計師二": "邵志明",
            "英文簡稱": "TCC",
            "英文通訊地址": "No.113/ Sec.2/ Zhongshan N. Rd./\
            Taipei City 104/Taiwan (R.O.C.)",
            "傳真機號碼": "(02)2531-6529",
            "電子郵件信箱": "finance@taiwancement.com",
            "公司網址": "http://www.taiwancement.com",
            "投資人關係聯絡人": "張佳琪",
            "投資人關係聯絡人職稱": "主任",
            "投資人關係聯絡電話": "02-25317099分機20358",
            "投資人關係聯絡電子郵件": "ir@taiwancement.com",
            "公司網站內利害關係人專區網址": "http://www.taiwancement.com/tw/csr/csr5-1.html",
            "type": 'sii'
        }

    print(payload['id'])
    url = 'http://localhost:5000/api/v0/basic_information/%s' % payload['id']
    res = requests.post(url, data=json.dumps(payload))
    """

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
    # protype version is done.

    # url = "http://localhost:5000/api/v0/sotck_number"
    # payload = requests.get(url)
    # stock_num = json.loads(payload.text)

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
    # TODO
    # data = crawlBalanceSheet(companyID, westernYearIn, seasonIn)

    aDict = {}
    url = "http://127.0.0.1:5000/api/v0/sotck_number"
    payload = requests.get(url)
    stock_num = json.loads(payload.text)

    for i in stock_num:
        print(i['id'])
        stockNum = i['id']
        try:
            data = crawlCashFlow(i['id'], westernYearIn, seasonIn)
        except Exception as ex:
            print(ex)
            data = None

        if data is None:
            time.sleep(5 + random.randrange(-3, 3))
            continue
        data.set_index("會計項目", inplace=True)
        data = data.reset_index()

        for i in data.index:
            if data.iloc[i][0] not in aDict:
                aDict[str(data.iloc[i][0])] = [stockNum]
            else:
                tempList = aDict[str(data.iloc[i][0])]
                tempList.append(stockNum)
                aDict[str(data.iloc[i][0])] = tempList

        time.sleep(4 + random.randrange(-3, 3))

    # data = crawlIncomeSheet(companyID, westernYearIn, seasonIn)
    # print(data)
    # data.set_index("會計項目", inplace=True)
    # data = data.reset_index()
    # for i in data.index:
    #     print(i, data.iloc[i][0])
    #     aSet.add(data.iloc[i][0])
    print(aDict)
    keys = sorted(aDict.keys())
    aDict = {i: aDict[i] for i in keys}

    fileName = "cashflow_title_with_no.csv"
    with open(fileName, 'w', encoding='utf8') as fo:
        for item in aDict:
            stri = item + ':\t'
            for num in aDict[item]:
                stri = stri + num + ', '
            stri += '\n'
            fo.write(stri)


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
