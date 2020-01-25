# coding=utf-8
import requests
import pandas as pd
import json
import time
import random
from datetime import datetime
from io import StringIO


def crawlCriticalInformation(parse_to_json=False):
    '''
    @description:
        爬取當日重大訊息，並整理留下與財報相關的訊息
    @return:
        dataFrame/json (wrt parm parse_to_json)
    @param:
        parse_to_json => boolean (default: False)
    '''
    res = requests.get('https://mops.twse.com.tw/mops/web/ajax_t05sr01_1')
    res.encode = 'utf-8'
    dfs = pd.read_html(StringIO(res.text), header=0, flavor='bs4')
    ret = pd.DataFrame()

    if len(dfs) == 1:
        return ret
    # code, name, date, content

    # print(dfs[1])

    file = open('criticalInfo.json', 'r', encoding='utf-8')
    settings = json.loads(file.read())
    file.close()

    criteria_pos = settings["criteria_pos"]
    criteria_neg = settings["criteria_neg"]

    for index in range(0, len(dfs[1])):
        match = False
        for crp in criteria_pos:
            match = match or (dfs[1].iloc[index]['主旨'].find(crp) != -1)
            for crn in criteria_neg:
                if dfs[1].iloc[index]['主旨'].find(crn) != -1:
                    match = False

            if(match):
                try:
                    tmp = dfs[1].iloc[index]
                    ret = ret.append(tmp)
                except Exception as err:
                    print(err)
                    break
    if parse_to_json:
        colHeader = list(ret.columns.values)
        colHeader.pop(0)
        rowHeader = list(ret.index)
        # print(dfs.loc[rowHeader[1]])

        dataArr = []

        for i in rowHeader:
            try:
                tmpDict = {}
                for k in colHeader:
                    if k == '公司代號':
                        tmpDict[k] = str(int(ret.loc[i][k]))
                    else:
                        tmpDict[k] = ret.loc[i][k]
                dataArr.append(tmpDict)
            except Exception as err:
                print(err)

        ret = json.dumps(dataArr)
    return ret


def crawlBasicInformation(companyType):
    """
    @description:
        爬取上市/上櫃/興櫃/公開發行個股的基本資料
    @return:
        dataFrame (sorted basicInfo)
    @param:
        companyType => string("sii", "otc", "rotc", "pub")
    """
    url = "https://mops.twse.com.tw/mops/web/ajax_t51sb01"
    headers = {
        'User-Agent': """Mozilla/5.0
                      (Macintosh; Intel Mac OS X 10_10_1)
                      AppleWebKit/537.36 (KHTML, like Gecko)
                      Chrome/39.0.2171.95 Safari/537.36""",
        'Content-Type': 'application/x-www-form-urlencoded',
        'encodeURIComponent': '1',
        'step': '1',
        'firstin': '1',
        'off': '1',
        'TYPEK': companyType,
    }
    result = requests.get(url, headers)
    print("crawling basicInfo " + companyType, end='...')
    result.encoding = 'utf-8'
    html_df = pd.read_html(StringIO(result.text), header=0)
    print("done.")
    ret = html_df[0]

    # take out all special char out
    ret = ret.replace(r'\,', '/', regex=True)
    ret = ret.fillna("0")

    # remove invalid row
    drop_index = []
    for i in ret.index:
        if ret.iloc[i]["公司代號"] == "公司代號":
            drop_index.append(i)
    ret = ret.drop(ret.index[drop_index])

    return ret


def crawlMonthlyRevenue(westernYearIn, monthIn):
    """
    @description:
        爬取上市/上櫃公司月營收
    @return:
        dataFrame (sorted monthly revenue)
    @param:
        westernYearIn => int (西元年)
        monthIn => int
    """
    year = str(westernYearIn - 1911)
    month = str(monthIn)

    urlSiiDomestic = {
                        "url": "https://mops.twse.com.tw/nas/t21/sii/t21sc03_"\
                                     + year + "_" + month + "_0.html",
                        "type": "SiiDomestic"
                     }
    urlSiiForiegn = {
                        "url": "https://mops.twse.com.tw/nas/t21/sii/t21sc03_"\
                                    + year + "_" + month + "_1.html",
                        "type":  "SiiForiegn"
                    }
    urlOtcDomestic = {
                        "url": "https://mops.twse.com.tw/nas/t21/otc/t21sc03_"\
                                    + year + "_" + month + "_0.html",
                        "type": "OtcDomestic"
                    }
    urlOtcForiegn = {
                        "url": "https://mops.twse.com.tw/nas/t21/otc/t21sc03_"\
                                    + year + "_" + month + "_1.html",
                        "type": "OtcForiegn"
                    }

    urls = [urlSiiDomestic, urlSiiForiegn, urlOtcDomestic, urlOtcForiegn]

    results = pd.DataFrame()
    print(str(westernYearIn) + "-" + str(monthIn))

    for url in urls:
        print("crawling monthlyRevenue " + url["type"], end='...')
        req = requests.get(url["url"], timeout=10)
        req.encoding = "big5"
        print("done.")

        try:
            html_df = pd.read_html(StringIO(req.text))
        except ValueError:
            print('%s no %s month revenue data for %s/%s'
                % (datetime.date.today().strftime("%Y-%m-%d"),
                   url["type"],
                   westernYearIn,
                   monthIn))
        else:
            dfs = pd.DataFrame()
            for df in html_df:
                if df.shape[1] == 11:
                    dfs = pd.concat([dfs, df], axis=0, ignore_index=True)
            dfs.columns = dfs.columns.droplevel()

            drop_index = []
            for i in dfs.index:
                try:
                    int(dfs.iloc[i]["公司代號"])
                except Exception:
                    drop_index.append(i)
            dfs = dfs.drop(dfs.index[drop_index])
            dfs = dfs.drop(columns=['公司名稱'])

            results = results.append(dfs)

    return results


def crawlBalanceSheet(companyID, westernYearIn, seasonIn):
    """
    @description:
        爬取個股每季的資產負債表
    @return:
        dataFrame (sorted balance sheet)
    @param:
        companyID => int
        westernYearIn => int (西元年)
        monthIn => int (1, 2...11, 12)
    """
    coID = str(companyID)
    year = str(westernYearIn - 1911)
    season = str(seasonIn)

    url = "https://mops.twse.com.tw/mops/web/ajax_t164sb03"

    if companyID == '0009A0' or\
       (int(companyID) not in range(2800, 2900) and
            int(companyID) not in range(5800, 5900)):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "encodeURIComponent": "1",
            "step": "1",
            "firstin": "1",
            "off": "1",
            "queryName": "co_id",
            "inpuType": "co_id",
            "TYPEK": "all",
            "isnew": "false",
            "co_id": coID,
            "year": year,
            "season": season,
            "Connection": "close"
        }
    else:
        headers = {
            'step': '2',
            'year': year,
            'season': season,
            'co_id': coID,
            'firstin': '1',
            "Connection": "close"
        }

    req = requests.post(url, headers)
    req.encoding = "utf-8"
    try:
        html_df = pd.read_html(StringIO(req.text))
        results = html_df[len(html_df)-1]
    except Exception as ex:
        print(ex)
        return []

    results.columns = results.columns.droplevel([0, 1])

    # drop invalid column
    results = results.iloc[:, 0:3]
    # rename columns
    amount = results.columns[1][0] + "-" + results.columns[1][1]
    percent = results.columns[2][0] + "-" + results.columns[2][1]
    results.columns = results.columns.droplevel(1)
    results.columns = [results.columns[0], amount, percent]

    resultsCopy = results.copy()
    resultsCopy.set_index("會計項目", inplace=True)

    # drop nan rows
    dropRowIndex = []
    for i in results.index:
        if resultsCopy.iloc[i].isnull().all():
            dropRowIndex.append(i)
    results = results.drop(results.index[dropRowIndex])
    results = results.set_index(results.columns[0])

    return results


def crawlIncomeSheet(companyID, westernYearIn, seasonIn):
    """
    @description:
        爬取個股每季的損益表
    @return:
        dataFrame (sorted income sheet)
    @param:
        companyID => int
        westernYearIn => int (西元年)
        monthIn => int (1,2...11,12)
    """
    coID = str(companyID)
    year = str(westernYearIn - 1911)
    season = str(seasonIn).zfill(2)

    url = "https://mops.twse.com.tw/mops/web/ajax_t164sb04"

    if companyID == '0009A0' or\
       (int(companyID) not in range(2800, 2900) and
            int(companyID) not in range(5800, 5900)):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "encodeURIComponent": "1",
            "step": "1",
            "firstin": "1",
            "off": "1",
            "queryName": "co_id",
            "inpuType": "co_id",
            "TYPEK": "all",
            "isnew": "false",
            "co_id": coID,
            "year": year,
            "season": season,
            "Connection": "close"
        }
    else:
        headers = {
            'step': '2',
            'year': year,
            'season': season,
            'co_id': coID,
            'firstin': '1',
            "Connection": "close"
        }

    print("crawling incomeSheet " + str(coID), end=" ")
    print(str(westernYearIn) + "Q" + str(season), end="...")
    req = requests.post(url, headers)
    req.encoding = "utf-8"
    # print(req.text)
    try:
        html_df = pd.read_html(StringIO(req.text))
        results = html_df[len(html_df)-1]
    except Exception as ex:
        print(ex)
        # TODO
        # if ex is no table found, then put null datq into database.
        return []
    print("done.")

    results.columns = results.columns.droplevel([0, 1])
    # drop invalid column
    results = results.iloc[:, 0:3]

    # rename columns
    amount = results.columns[1][0] + "-" + results.columns[1][1]
    percent = results.columns[2][0] + "-" + results.columns[2][1]
    results.columns = results.columns.droplevel(1)
    results.columns = [results.columns[0], amount, percent]

    resultsCopy = results.copy()
    resultsCopy.set_index("會計項目", inplace=True)

    # drop nan rows
    dropRowIndex = []
    for i in results.index:
        if resultsCopy.iloc[i].isnull().all():
            dropRowIndex.append(i)
    results = results.drop(results.index[dropRowIndex])
    results = results.set_index(results.columns[0])

    return results


def crawlCashFlow(companyID, westernYearIn, seasonIn, recursiveBreak=False):
    """
    @description:
        爬取個股每季的現金流量表
    @return:
        dataFrame (sorted cash flow)
    @param:
        companyID => int
        westernYearIn => int (西元年)
        monthIn => int (1,2...11,12)
        recursiveBreak => boolean
    """
    coID = str(companyID)
    year = str(westernYearIn - 1911)
    season = str(seasonIn)

    url = "https://mops.twse.com.tw/mops/web/ajax_t164sb05"

    if companyID == '0009A0' or\
       (int(companyID) not in range(2800, 2900) and
            int(companyID) not in range(5800, 5900)):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "encodeURIComponent": "1",
            "step": "1",
            "firstin": "1",
            "off": "1",
            "queryName": "co_id",
            "inpuType": "co_id",
            "TYPEK": "all",
            "isnew": "false",
            "co_id": coID,
            "year": year,
            "season": season,
            "Connection": "close"
        }
    else:
        headers = {
            'step': '2',
            'year': year,
            'season': season,
            'co_id': coID,
            'firstin': '1',
            "Connection": "close"
        }

    while(True):
        try:
            # print(headers)
            req = requests.post(url, data=headers, timeout=(2,15))
            req.encoding = "utf-8"
            print(req)
            html_df = pd.read_html(StringIO(req.text))
            print(html_df[1].loc[0])
            results = html_df[1]
            break
        except Exception as ex:
            delay = 3 + random.randrange(0, 4)
            print(type(ex), ex.args[0])
            print("\n  ", end="")
            print(type(ex).__name__, end=" ")
            print("catched. Retry in %s sec." % (delay))
            time.sleep(delay)

    # drop invalid column
    results = results.iloc[:, 0:2]

    # rename columns
    amount = results.columns[1][0] + "-" + results.columns[1][1]
    results.columns = results.columns.droplevel(1)
    results.columns = [results.columns[0], amount]

    # drop nan rows
    dropRowIndex = []
    for i in results.index:
        if results.iloc[i].isnull().any():
            dropRowIndex.append(i)
    results = results.drop(results.index[dropRowIndex])

    # set row name
    results = results.set_index(results.columns[0])

    if recursiveBreak:
        return results

    # transfer accumulative cashflow into single season
    if seasonIn != 1:
        prev = crawlCashFlow(companyID, westernYearIn, seasonIn-1, True)
        for index in results.index:
            try:
                results.loc[index] = results.loc[index][0] - prev.loc[index][0]
            except Exception as ex:
                pass

    return results


def crawlDailyPrice(datetime):
    """
    @description:
        爬取上市/上櫃每日股價，並以dict回傳
    @return:
        dataFrame in Dictionary (access with "sii", "otc")
    @param:
        datetime => datetime
    """
    dateSii = datetime.strftime("%Y%m%d")
    # dateSii = '"' + "20190909" + '"'
    urlSii = "https://www.twse.com.tw/exchangeReport/"\
        + "MI_INDEX?response=html&date="\
        + dateSii + "&type=ALLBUT0999"

    dateOtc = str(datetime.year-1911) + "/"\
        + str(datetime.month).zfill(2) + "/"\
        + str(datetime.day).zfill(2)
    # dateOtc = "108/09/09"
    urlOtc = "https://www.tpex.org.tw/web/stock/aftertrading/"\
        + "daily_close_quotes/stk_quote_result.php?l=zh-tw"\
        + "&o=htm&d=" + dateOtc + "&s=0,asc,0"

    print("crawling sii daily price.")
    print(urlSii)
    reqSii = requests.get(urlSii)
    reqSii.encoding = 'utf-8'
    print("parsing sii daily price.")
    resultSii = pd.read_html(StringIO(reqSii.text))
    resultSii = resultSii[8]
    resultSii.columns = resultSii.columns.droplevel([0, 1])

    print("crawling otc daily price.")
    print(urlOtc)
    reqOtc = requests.get(urlOtc)
    reqOtc.encoding = 'utf-8'
    print("parsing otc daily price")
    resultOtc = pd.read_html(StringIO(reqOtc.text))
    resultOtc = resultOtc[0]
    resultOtc.columns = resultOtc.columns.droplevel(0)

    results = {'sii': resultSii, 'otc': resultOtc}

    return results


def crawlShareholderCount(companyID, datetime):
    """
    @description:
        爬取千張持股股東人數，通常在週五
    @return:
        dataFrame
    @param:
        datetime => datetime
    """
    coID = str(companyID)
    date = datetime.strftime("%Y%m%d")

    url = "https://www.tdcc.com.tw/smWeb/QryStockAjax.do"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "scaDates": date,
        "scaDate": date,
        "SqlMethod": "StockNo",
        "StockNo": coID,
        "REQ_OPR": "SELECT",
        "clkStockNo": coID
    }

    print('crawling shareholderCount')
    req = requests.post(url, headers)
    req.encoding = 'big5'
    print('crawler complete.')

    print('parsing data')
    html_df = pd.read_html(StringIO(req.text))
    result = html_df[6]
    print('parse complete.')

    return result


def crawlSummaryReportStockNo(
        reportTypes='income_sheet',
        companyType='sii',
        westernYearIn=2019,
        seasonIn=3):
    """this method is used to crawler entire income sheet stock number.
    According to the received parameter type, westernYearIn and seasonIn,
    Go to the specific website and crawler stock number
    that has released the income sheet.

    Args:
        type: a string of stock(sii, otc)
        westernYearIn: Year of the West
        seasonIn: Financial quarter(1, 2, 3, 4)

    Return:
        result: a list with stock numbers inside

    Raises:
        Exception: no table in request result or others things.
    """
    season = str(seasonIn).zfill(2)
    print(reportTypes + " " + companyType + " summary "
        + str(westernYearIn) + 'Q' + str(season), end='...')
    year = str(westernYearIn - 1911)

    if reportTypes is 'balance_sheet':
        url = "https://mops.twse.com.tw/mops/web/ajax_t163sb05"
    else:
        url = 'https://mops.twse.com.tw/mops/web/ajax_t163sb04'

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "1",
        "off": "1",
        "isQuery": 'Y',
        "TYPEK": companyType,
        "year": year,
        "season": season,
    }

    while(True):
        try:
            req = requests.post(url, headers, timeout=(2,25))
            req.encoding = "utf-8"
            html_df = pd.read_html(StringIO(req.text))
            print("done.")
            break
        except Exception as ex:
            delay = 3 + random.randrange(0, 4)
            print("  ", end="")
            print(type(ex).__name__, end=" ")
            print("catched. Retry in %s sec." % (delay))
            time.sleep(delay)

    stockNums = []
    for idx in range(1, len(html_df)):
        # print(html_df[idx].as_matrix(columns=html_df[idx].columns['公司名稱':]))
        stockNums += list(html_df[idx]['公司代號'])
    time.sleep(3 + random.randrange(0, 4))
    return stockNums


def crawlerDailyPrice(stockNums, type='sii'):
    """
    stock num: tse_1101.tw/otc_3455.tw
    type: sii / otc
    """
    typeTransform = {
        'sii': 'tse',
        'otc': 'otc'
    }
    print(type, stockNums)
    url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?"\
          + "delay=0&_=1552123547443&ex_ch="

    stockNums = ["%s_%s.tw" % (
        typeTransform[type], stockNum) for stockNum in stockNums]
    stockNumStr = "|".join(stockNums)

    data = requests.get(url+stockNumStr)
    data = json.loads(data.text)

    idAndPrice = []
    for i in data['msgArray']:
        try:
            idAndPrice.append({'stock_id': i['c'], "股價": i['z']})
        except Exception as ex:
            print("%s %s"% (i['c'], ex))

    return idAndPrice


if __name__ == "__main__":
    # siiCompany = crawlBasicInformation('sii')
    # otcCompany = crawlBasicInformation('otc')
    # print(type(siiCompany))
    # print(otcCompany)
    # crawlSummaryReportStockNo('income_sheet', 'sii', 2019, 1)
    # crawlIncomeSheet(2801, 2013, 1)
    crawlerDailyPrice('otc')
