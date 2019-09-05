from crawler import crawlBasicInformation

def getBasicInfo(dataType='sii'):
    data = crawlBasicInformation(dataType)

    #dfHeader = data.iloc[0,:]
    #print(dfHeader)
    fileName = "test_%s.csv" % dataType
    with open(fileName, 'w', encoding='utf8') as fo:
        for idx, row in data.iterrows():
            if row[0]=='1402':
                print(",".join(row))
            stri = ",".join(row)+'\n'
            fo.write(stri)
            

if __name__ == '__main__':
    getBasicInfo('sii')
