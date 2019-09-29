from crawler import crawlBasicInformation
from crawler import crawlMonthlyRevenue
import json
import requests


def getBasicInfo(dataType='sii'):
    data = crawlBasicInformation(dataType)

    # 讀取noun_conversion時請記得使用 if key in dict 檢查是否需要替換key值
    with open('./noun_conversion/basic_information.json') as basic_information:
        basicInfoNounConvers = json.loads(basic_information.read())

    # Use noun_conversion file: basic_information.json
    # to change specific index in Dataframe.
    columns = data.columns
    new_index = []
    for idx, column in enumerate(columns):
        if basicInfoNounConvers.get(column) is not None:
            new_index.append(basicInfoNounConvers.get(column))
        else:
            new_index.append(column)
    data.columns = new_index

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
    res = requests.post(url, data=json.dumps(payload))"""

    for i in range(len(data)):
        dataPayload = json.loads(
            data.iloc[i].to_json(force_ascii=False))
        url = "http://localhost:5000/api/v0/\
        basic_information/%s" % dataPayload['id']
        res = requests.post(url, data=json.dumps(dataPayload))
        break


def getMonthlyRevenue(westernYearIn=2019, monthIn=8):
    data = crawlMonthlyRevenue(westernYearIn, monthIn)
    year = westernYearIn
    month = monthIn

    # 讀取noun_conversion時請記得使用 if key in dict 檢查是否需要替換key值
    with open('./noun_conversion/month_revenue.json') as month_revenue:
        monthReveNounConvers = json.loads(month_revenue.read())

    columns = data.columns
    new_index = []
    for idx, column in enumerate(columns):
        if monthReveNounConvers.get(column) is not None:
            new_index.append(monthReveNounConvers.get(column))
        else:
            new_index.append(column)
    data.columns = new_index

    # print(data.columns)
    # fileName = "revenue_%d-%d.csv" % (year, month)
    # with open(fileName, 'w', encoding='utf8') as fo:
    #     fo.write(",".join(data.columns)+"\n")
    #     for idx, row in data.iterrows():
    #         stri = ""
    #         for i in row:
    #             i=str(i).replace(',', '，')
    #             stri+=i+','
    #         stri+='\n'
    #         fo.write(stri)

    for i in range(len(data)):
        dataPayload = json.loads(data.iloc[i].to_json(force_ascii=False))
        # print(dataPayload)
        dataPayload['year'] = year
        dataPayload['month'] = str(month)
        url = "http://localhost:5000/api/v0/month_revenue/%s" % str(
            dataPayload['stock_id'])
        print(url)
        print(dataPayload)
        res = requests.post(url, data=json.dumps(dataPayload))
        break


if __name__ == '__main__':
    getBasicInfo('sii')
    # getMonthlyRevenue(2019, 8)
