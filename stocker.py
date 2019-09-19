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
    """mysql+pymysql://%s:%s@localhost/stocker?charset=utf8""" % (
            dbAccount["username"], dbAccount["password"]))
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
def showMain():
    return "Main"


@app.route(
    '/api/v0/basic_information/<string:basic_information_id>',
    methods=['GET','POST'])
def handleBasicInfo(basic_information_id):
    if request.method == 'POST':
        # try:
            payload = json.loads(request.data)
            basicInfo = session.query(Basic_information).filter_by(
                id=basic_information_id).one_or_none()
            if basicInfo is not None:
                basicInfo['update_date']=datetime.datetime.now().strftime("%Y-%m-%d") 
                basicInfo['type']=payload['type'],
                basicInfo['公司名稱']=payload['公司名稱'],
                basicInfo['公司簡稱']=payload['公司簡稱'],
                basicInfo['產業類別']=payload['產業類別'],
                basicInfo['外國企業註冊地國']=payload['外國企業註冊地國'],
                basicInfo['住址']=payload['住址'],
                basicInfo['營利事業統一編號']=payload['營利事業統一編號'],
                basicInfo['董事長']=payload['董事長'],
                basicInfo['總經理']=payload['總經理'],
                basicInfo['發言人']=payload['發言人'],
                basicInfo['發言人職稱']=payload['發言人職稱'],
                basicInfo['代理發言人']=payload['代理發言人'],
                basicInfo['總機電話']=payload['總機電話'],
                basicInfo['成立日期']=payload['成立日期'],
                basicInfo['上市上櫃興櫃公開發行日期']=payload['上市上櫃興櫃公開發行日期'],
                basicInfo['普通股每股面額']=payload['普通股每股面額'],
                basicInfo['實收資本額']=payload['實收資本額'],
                basicInfo['已發行普通股數或TDR原發行股數']=payload['已發行普通股數或TDR原發行股數'],
                basicInfo['私募普通股']=payload['私募普通股'],
                basicInfo['特別股']=payload['特別股'],
                basicInfo['編製財務報告類型']=payload['編製財務報告類型'],
                basicInfo['普通股盈餘分派或虧損撥補頻率']=payload['普通股盈餘分派或虧損撥補頻率'],
                basicInfo['普通股年度現金股息及紅利決議層級']=payload['普通股年度現金股息及紅利決議層級'],
                basicInfo['股票過戶機構']=payload['股票過戶機構'],
                basicInfo['過戶電話']=payload['過戶電話'],
                basicInfo['過戶地址']=payload['過戶地址'],
                basicInfo['簽證會計師事務所']=payload['簽證會計師事務所'],
                basicInfo['簽證會計師一']=payload['簽證會計師一'],
                basicInfo['簽證會計師二']=payload['簽證會計師二'],
                basicInfo['英文簡稱']=payload['英文簡稱'],
                basicInfo['英文通訊地址']=payload['英文通訊地址'],
                basicInfo['傳真機號碼']=payload['傳真機號碼'],
                basicInfo['電子郵件信箱']=payload['電子郵件信箱'],
                basicInfo['投資人關係聯絡人']=payload['投資人關係聯絡人'],
                basicInfo['投資人關係聯絡人職稱']=payload['投資人關係聯絡人職稱'],
                basicInfo['投資人關係聯絡電話']=payload['投資人關係聯絡電話'],
                basicInfo['投資人關係聯絡電子郵件']=payload['投資人關係聯絡電子郵件'],
                basicInfo['公司網站內利害關係人專區網址']=payload['公司網站內利害關係人專區網址']
            else:
                basicInfo = Basic_information(
                    id=payload['公司代號'],
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
