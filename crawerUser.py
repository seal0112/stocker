from crawler import crawlBasicInformation

def getBasicInfo():
    data = crawlBasicInformation('sii')

    dfHeader = data.iloc[0,:]
    #print(dfHeader)
    with open('test.csv', 'w', encoding='utf8') as fo:
        for idx, row in data.iterrows():
            stri = ",".join(row)+'\n'
            fo.write(stri)
            


if __name__ == '__main__':
    getBasicInfo()
