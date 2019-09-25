from flask import Flask, request, redirect, url_for
from flask import jsonify, make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Basic_information
import json
import datetime

# Read file databaseAccount.json in directory critical_flie
# then can get database username and password.
with open('./critical_flie/databaseAccount.json') as accountReader:
    dbAccount = json.loads(accountReader.read())

app = Flask(__name__)

engine = create_engine(
    """mysql+pymysql://%s:%s@%s/stocker?charset=utf8""" % (
            dbAccount["username"], dbAccount["password"], dbAccount["ip"]))
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

payload = {
            "id":"1101",
            "公司名稱":"台灣水泥股份有限公司",
            "公司簡稱":"台泥",
            "產業類別":"水泥工業",
            "外國企業註冊地國":"－",
            "住址":"台北市中山北路2段113號",
            "營利事業統一編號":"11913502",
            "董事長":"張安平",
            "總經理":"李鐘培",
            "發言人":"黃健強",
            "發言人職稱":"資深副總經理",
            "代理發言人":"蔡立文",
            "總機電話":"(02)2531-7099",
            "成立日期":"39/12/29",
            "上市上櫃興櫃公開發行日期":"51/02/09",
            "普通股每股面額":"新台幣 10.0000元",
            "實收資本額":56656192040,
            "已發行普通股數或TDR原發行股數":5465619204,
            "私募普通股":0,
            "特別股":200000000,
            "編製財務報告類型":"合併",
            "普通股盈餘分派或虧損撥補頻率":"每年",
            "普通股年度現金股息及紅利決議層級":"股東會",
            "股票過戶機構":"中國信託商業銀行代理部",
            "過戶電話":"66365566",
            "過戶地址":"台北市重慶南路一段83號5樓",
            "簽證會計師事務所":"勤業眾信聯合會計師事務所",
            "簽證會計師一":"翁雅玲",
            "簽證會計師二":"邵志明",
            "英文簡稱":"TCC",
            "英文通訊地址":"No.113/ Sec.2/ Zhongshan N. Rd./Taipei City 104/Taiwan (R.O.C.)",
            "傳真機號碼":"(02)2531-6529",
            "電子郵件信箱":"finance@taiwancement.com",
            "公司網址":"http://www.taiwancement.com",
            "投資人關係聯絡人":"張佳琪",
            "投資人關係聯絡人職稱":"主任",
            "投資人關係聯絡電話":"02-25317099分機20358",
            "投資人關係聯絡電子郵件":"ir@taiwancement.com",
            "公司網站內利害關係人專區網址":"http://www.taiwancement.com/tw/csr/csr5-1.html",
            "type": 'sii'
        }


@app.route('/')
def showMain():
    b = session.query(Basic_information).filter_by(
                id='1101').one_or_none()
    res = b.serialize
    newB = Basic_information()

    print(newB)
    #return jsonify(newB.serialize)
    return jsonify(res)


@app.route(
    '/api/v0/basic_information/<string:basic_information_id>',
    methods=['GET','POST'])
def handleBasicInfo(basic_information_id):
    basicInfo = session.query(Basic_information).filter_by(
        id=basic_information_id).one_or_none()
    if request.method == 'GET':
        return basicInfo.serialize
    elif request.method == 'POST':
        # try:
            payload = json.loads(request.data)
            if basicInfo is not None:
                for index in payload:
                    changeFlag = False
                    if basicInfo[index] != payload[index]:
                        print("%s || %s" % (basicInfo[index], payload[index]))
                        changeFlag = True
                        basicInfo[index] = payload[index]
                if changeFlag:
                    basicInfo['update_date']=datetime.datetime.now().strftime("%Y-%m-%d") 
            else:
                basicInfo = Basic_information(
                    id=basic_information_id,
                    type=payload['type'],
                    公司名稱=payload['公司名稱'],
                    公司簡稱=payload['公司簡稱'],
                    產業類別=payload['產業類別'],
                    外國企業註冊地國=payload['外國企業註冊地國'],
                    住址=payload['住址'],
                    營利事業統一編號=payload['營利事業統一編號'],
                    董事長=payload['董事長'],
                    總經理=payload['總經理'],
                    發言人=payload['發言人'],
                    發言人職稱=payload['發言人職稱'],
                    代理發言人=payload['代理發言人'],
                    總機電話=payload['總機電話'],
                    成立日期=payload['成立日期'],
                    上市上櫃興櫃公開發行日期=payload['上市上櫃興櫃公開發行日期'],
                    普通股每股面額=payload['普通股每股面額'],
                    實收資本額=payload['實收資本額'],
                    已發行普通股數或TDR原發行股數=payload['已發行普通股數或TDR原發行股數'],
                    私募普通股=payload['私募普通股'],
                    特別股=payload['特別股'],
                    編製財務報告類型=payload['編製財務報告類型'],
                    普通股盈餘分派或虧損撥補頻率=payload['普通股盈餘分派或虧損撥補頻率'],
                    普通股年度現金股息及紅利決議層級=payload['普通股年度現金股息及紅利決議層級'],
                    股票過戶機構=payload['股票過戶機構'],
                    過戶電話=payload['過戶電話'],
                    過戶地址=payload['過戶地址'],
                    簽證會計師事務所=payload['簽證會計師事務所'],
                    簽證會計師一=payload['簽證會計師一'],
                    簽證會計師二=payload['簽證會計師二'],
                    英文簡稱=payload['英文簡稱'],
                    英文通訊地址=payload['英文通訊地址'],
                    傳真機號碼=payload['傳真機號碼'],
                    電子郵件信箱=payload['電子郵件信箱'],
                    公司網址=payload['公司網址'],
                    投資人關係聯絡人=payload['投資人關係聯絡人'],
                    投資人關係聯絡人職稱=payload['投資人關係聯絡人職稱'],
                    投資人關係聯絡電話=payload['投資人關係聯絡電話'],
                    投資人關係聯絡電子郵件=payload['投資人關係聯絡電子郵件'],
                    公司網站內利害關係人專區網址=payload['公司網站內利害關係人專區網址'])

            session.add(basicInfo)
            session.commit()

            res = make_response(
                json.dumps('Create Ok!'), 201)
            return res
        # except Exception as ex:
        #     print(ex)
        #     res = make_response(            
        #         json.dumps(
        #             'Failed to upgrade.'), 406)
        #     return res


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
