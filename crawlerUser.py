from crawler import crawlBasicInformation

def getBasicInfo(dataType='sii'):
    data = crawlBasicInformation(dataType)

    #dfHeader = data.iloc[0,:]
    #print(dfHeader)
    fileName = "test_%s.csv" % dataType
    with open(fileName, 'w', encoding='utf8') as fo:
        for idx, row in data.iterrows():
            stri = ','.join(row)+'\n'
            fo.write(stri)
            
    # 讀取noun_conversion時請記得使用 if key in dict 檢查是否需要替換key值
            

if __name__ == '__main__':
    getBasicInfo('sii')
