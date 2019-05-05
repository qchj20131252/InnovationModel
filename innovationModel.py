from pymongo import MongoClient

def get_mongodb_connection():
    client = MongoClient("ip","port")
    db_auth = client.admin
    db_auth.authenticate('id', 'psd')
    db = client["db_name"]
    return db

def get_maxValue(scoreDict):
    maxValue = 0
    for value in list(scoreDict.values()):
        if value > maxValue:
            maxValue = value
    return maxValue

def get_scoreDict(scoreDict,res,businessScore):
    for r in res:
        companyName = r["companyName"]
        if companyName in  businessScore:
            if companyName in scoreDict:
                scoreDict[companyName] = scoreDict[companyName] + 1
            else:
                scoreDict[companyName] = 1

def normalization(maxValue,scoreDict):
    for com in scoreDict:
        scoreDict[com] = scoreDict[com]/maxValue*100

def print_maxAndMin(scoreDict):
    max = 0
    min = 100
    for a in scoreDict:
        if max < scoreDict[a]:
            max = scoreDict[a]
        if min > scoreDict[a]:
            min = scoreDict[a]
    print(max)
    print(min)

if __name__ == '__main__':
    db = get_mongodb_connection()
    collection = db["company_profile"]
    results = collection.find()
    businessScore = {}
    maxCapital = 0.0
    for r in results:
        registeredCapital = r["registeredCapital"]
        if maxCapital < registeredCapital:
            maxCapital = registeredCapital
        if registeredCapital < 0:
            businessScore[r["companyName"]] = 100
            continue
        businessScore[r["companyName"]] = registeredCapital
    for com in businessScore:
        businessScore[com] = businessScore[com]/maxCapital*100
    print("businessScore")
    print_maxAndMin(businessScore)
    print(businessScore)
    print(len(businessScore))


    # 著作权创新分数
    #存储著作权创新分数
    copyrightScore = {}
    copyright_res1 = db["software_copyright"].find()
    copyright_res2 = db["work_copyright"].find()
    get_scoreDict(copyrightScore,copyright_res1,businessScore)
    get_scoreDict(copyrightScore,copyright_res2,businessScore)
    maxCopyrightCount = get_maxValue(copyrightScore)
    normalization(maxCopyrightCount,copyrightScore)
    print("copyright")
    print_maxAndMin(copyrightScore)
    print(copyrightScore)
    print(len(copyrightScore))

    #科技文献创新分数
    literature_res = db["company_literature"].find()
    #存储科技文献创新分数
    literatureScore = {}
    get_scoreDict(literatureScore,literature_res,businessScore)
    maxLiteratureCount = get_maxValue(literatureScore)
    normalization(maxLiteratureCount,literatureScore)
    print("literature")
    print_maxAndMin(literatureScore)
    print(literatureScore)
    print(len(literatureScore))

    #商标创新分数
    trade_res = db["trade"].find()
    #储存商标创新分数
    tradeScore = {}
    get_scoreDict(tradeScore,trade_res,businessScore)
    maxTradeCount = get_maxValue(tradeScore)
    normalization(maxTradeCount,tradeScore)
    print("trade")
    print_maxAndMin(tradeScore)
    print(tradeScore)
    print(len(tradeScore))

    #专利创新分数
    patent_res = db["patent"].find()
    #储存专利创新分数
    patentScore = {}
    for r in patent_res:
        value = 0
        appli_num = r["appli_num"]
        if appli_num[2] == "2":
            if appli_num[6] == "3":
                value = 20
            elif appli_num[6] == "2":
                value = 30
            else:
                value = 50
        else:
            if appli_num[4] == "3":
                value = 20
            elif appli_num[4] == "2":
                value = 30
            else:
                value = 50
        companyName = r["companyName"]
        if companyName in patentScore:
            patentScore[companyName] = patentScore[companyName] + value
        else:
            patentScore[companyName] = value

    maxPatentCount = get_maxValue(patentScore)
    normalization(maxPatentCount,patentScore)
    print("patent")
    print_maxAndMin(patentScore)
    print(patentScore)
    print(len(patentScore))


    for s in businessScore:
        businessScore[s] = businessScore[s] * 0.3
        if s in copyrightScore:
            businessScore[s] = businessScore[s] + copyrightScore[s] * 0.2
        if s in tradeScore:
            businessScore[s] = businessScore[s] + tradeScore[s] * 0.1
        if s in literatureScore:
            businessScore[s] = businessScore[s] + literatureScore[s] * 0.2
        if s in patentScore:
            businessScore[s] = businessScore[s] + patentScore[s] * 0.2
    maxScore = get_maxValue(businessScore)
    normalization(maxScore,businessScore)
    print("all")
    print_maxAndMin(businessScore)
    print(businessScore)
    print(len(businessScore))

    collection2 = db["companyInfo"]
    results2 = collection2.find()
    for r in results2:
        companyName = r["companyName"]
        newvalues = {"$set":{"value":businessScore[companyName]}}
        collection2.update_one(r,newvalues)


