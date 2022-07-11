from flask_restx import Api, Namespace, Resource, fields

namespace = Namespace('basic_information', 
                'Basic Information Related Endpoint')

basicInfoModel = namespace.model('BasicInfo (Response/Create/Update)', {
    'id': fields.String(
        description = 'Company ID of basic information'
    ),
    'update_date':fields.String(
        description = 'Latest update date'
    ),
    'exchangeType':fields.String(
        description = 'Stock exchage types',
        enum = ['sii', 'otc', 'rotc', 'pub', 'delist']
    ),
    '上市上櫃興櫃公開發行日期':fields.String(),
    '代理發言人':fields.String(),
    '住址':fields.String(),
    '傳真機號碼':fields.String(),
    '公司名稱':fields.String(),
    '公司簡稱':fields.String(),
    '公司網址':fields.String(),
    '外國企業註冊地國':fields.String(),
    '實收資本額':fields.String(),
    '已發行普通股數或TDR原發行股數':fields.String(),
    '成立日期':fields.String(),
    '投資人關係聯絡人':fields.String(),
    '投資人關係聯絡人職稱':fields.String(),
    '投資人關係聯絡電子郵件':fields.String(),
    '投資人關係聯絡電話':fields.String(),
    '普通股年度現金股息及紅利決議層級':fields.String(),
    '普通股每股面額':fields.String(),
    '普通股盈餘分派或虧損撥補頻率':fields.String(),
    '營利事業統一編號':fields.String(),
    '特別股':fields.String(),
    '產業類別':fields.String(),
    '發言人':fields.String(),
    '發言人職稱':fields.String(),
    '私募普通股':fields.String(),
    '簽證會計師一':fields.String(),
    '簽證會計師事務所':fields.String(),
    '簽證會計師二':fields.String(),
    '編製財務報告類型':fields.String(),
    '總機電話':fields.String(),
    '總經理':fields.String(),
    '股票過戶機構':fields.String(),
    '英文簡稱':fields.String(),
    '英文通訊地址':fields.String(),
    '董事長':fields.String(),
    '過戶地址':fields.String(),
    '過戶電話':fields.String(),
    '電子郵件信箱':fields.String()
})