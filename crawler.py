# coding=utf-8
import requests
import pandas as pd
import json
from datetime import datetime
from io import StringIO


def crawlCriticalInformation(parse_to_json=False):
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
    print("crawler complete.")
    result.encoding = 'utf-8'
    html_df = pd.read_html(StringIO(result.text), header=0)
    print("parsing html to df")
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
    year = str(westernYearIn - 1911)
    month = str(monthIn)

    urlOtcDomestic = "https://mops.twse.com.tw/nas/t21/sii/t21sc03_"\
                     + year + "_" + month + "_0.html"
    urlOtcForiegn = "https://mops.twse.com.tw/nas/t21/sii/t21sc03_"\
                    + year + "_" + month + "_1.html"
    urlSiiDomestic = "https://mops.twse.com.tw/nas/t21/otc/t21sc03_"\
                     + year + "_" + month + "_0.html"
    urlSiiForiegn = "https://mops.twse.com.tw/nas/t21/otc/t21sc03_"\
                    + year + "_" + month + "_1.html"

    urls = [urlOtcDomestic, urlOtcForiegn, urlSiiDomestic, urlSiiForiegn]

    results = pd.DataFrame()
    for url in urls:
        print("crawling...: "+url)
        req = requests.get(url)
        req.encoding = "big5"
        print("parsing html to df")
        html_df = pd.read_html(StringIO(req.text))
        dfs = pd.DataFrame()
        for df in html_df:
            if df.shape[1] == 11:
                dfs = pd.concat([dfs, df], axis=0, ignore_index=True)
        dfs.columns = dfs.columns.droplevel()

        drop_index = []
        for i in dfs.index:
            try:
                int(dfs.iloc[i]["公司代號"])
            except:
                drop_index.append(i)
        dfs = dfs.drop(dfs.index[drop_index])

        results = results.append(dfs)
    return results


def crawlBalanceSheet(companyID, westernYearIn, seasonIn):
    coID = str(companyID)
    year = str(westernYearIn - 1911)
    season = str(seasonIn)

    url = "https://mops.twse.com.tw/mops/web/ajax_t164sb03"
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
        "season": season
    }

    req = requests.post(url, headers)
    req.encoding = "utf-8"
    html_df = pd.read_html(StringIO(req.text))
    results = html_df[1]
    results.columns = results.columns.droplevel([0, 1])

    # drop invalid column
    results = results.iloc[:, 0:3]

    # rename columns
    amount = results.columns[1][0] + "-" + results.columns[1][1]
    percent = results.columns[2][0] + "-" + results.columns[2][1]
    results.columns = results.columns.droplevel(1)
    results.columns = [results.columns[0], amount, percent]

    # drop nan rows
    dropRowIndex = []
    for i in results.index:
        if results.iloc[i].isnull().any():
            dropRowIndex.append(i)
    results = results.drop(results.index[dropRowIndex])

    return results


def crawlIncomeSheet(companyID, westernYearIn, seasonIn):
    coID = str(companyID)
    year = str(westernYearIn - 1911)
    season = str(seasonIn)

    url = "https://mops.twse.com.tw/mops/web/ajax_t164sb04"
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
        "season": season
    }

    req = requests.post(url, headers)
    req.encoding = "utf-8"
    # print(req.text)
    html_df = pd.read_html(StringIO(req.text))
    results = html_df[1]
    results.columns = results.columns.droplevel([0, 1])

    # drop invalid column
    results = results.iloc[:, 0:3]

    # rename columns
    amount = results.columns[1][0] + "-" + results.columns[1][1]
    percent = results.columns[2][0] + "-" + results.columns[2][1]
    results.columns = results.columns.droplevel(1)
    results.columns = [results.columns[0], amount, percent]

    # drop nan rows
    dropRowIndex = []
    for i in results.index:
        if results.iloc[i].isnull().any():
            dropRowIndex.append(i)
    results = results.drop(results.index[dropRowIndex])

    return results


def crawlCashFlow(companyID, westernYearIn, seasonIn):
    coID = str(companyID)
    year = str(westernYearIn - 1911)
    season = str(seasonIn)

    url = "https://mops.twse.com.tw/mops/web/ajax_t164sb05"
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
        "season": season
    }

    req = requests.post(url, headers)
    req.encoding = "utf-8"
    # print(req.text)
    html_df = pd.read_html(StringIO(req.text))
    results = html_df[1]
    results.columns = results.columns.droplevel([0, 1])

    # drop invalid column
    results = results.iloc[:, 0:3]

    # rename columns
    amount = results.columns[1][0] + "-" + results.columns[1][1]
    percent = results.columns[2][0] + "-" + results.columns[2][1]
    results.columns = results.columns.droplevel(1)
    results.columns = [results.columns[0], amount, percent]

    # drop nan rows
    dropRowIndex = []
    for i in results.index:
        if results.iloc[i].isnull().any():
            dropRowIndex.append(i)
    results = results.drop(results.index[dropRowIndex])

    return results


def crawlDailyPrice(datetime):
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
    print('parsor complete.')

    return result


if __name__ == "__main__":
    siiCompany = crawlBasicInformation('sii')
    #otcCompany = crawlBasicInformation('otc')
    print(type(siiCompany))
    #print(otcCompany)
