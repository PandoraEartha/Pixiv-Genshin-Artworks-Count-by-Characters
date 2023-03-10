# coding=utf-8
import requests
import re
import os
import json
import time
import sys
import threading
import math


def contentToCSV(C,character):
    csv=['TITLE(LINK),R18,TAGS,ARTIST(LINK)']
    for EC in C:
        EC=re.sub('"',"'",EC)
        try:
            preInformation='"=HYPERLINK(""https://www.pixiv.net/artworks/'\
                           +re.search("\{'id': '(\d+?)'",EC).group(1)+\
                           '"",""'\
                           +re.search("'title': '(.*?)'",EC).group(1)\
                           +'"")",'\
                           +re.search("'xRestrict': (\d)",EC).group(1)\
                           +',"'\
                           +re.sub("'",'',re.search("'tags': \[(.*?)]",EC).group(1))\
                           +'",'\
                           +'"=HYPERLINK(""https://www.pixiv.net/users/'\
                           +re.search("'userId': '(\d+?)'",EC).group(1)\
                           +'"",""'\
                           +re.search("'userName': '(.*?)'",EC).group(1)\
                           +'"")"'
        except:
            print('WRONG INFORMATION FORMAT: '+EC)
            preInformation=re.search("\{'id': '(\d+?)'",EC).group(1)+',WRONG FORMANT,WRONG FORMANT,WRONG FORMANT'
        csv.append(preInformation)
    characterNameMerged='_'.join(character)
    with open(characterNameMerged+'.csv','w+') as csvBin:
        csvBin.write('\n'.join(csv))
    csvBin.close()


def removeDuplicationAndKeepOrder(List,additionalElement):
    duplications=[]
    innerList=[additionalElement]+List
    for a in range(len(innerList)):
        for b in range(a+1,len(innerList)):
            if innerList[a]==innerList[b]:
                if b not in duplications:
                    duplications.append(b)

    duplications=sorted(duplications)
    popCount=0
    for duplication in duplications:
        innerList.pop(duplication-popCount)
        popCount+=1

    return innerList[1:]


def minIndex(List):
    toReturn=0
    index=0
    Min=List[0]
    for item in List:
        if item<=Min:
            Min=item
            toReturn=index
        index+=1

    return toReturn


def standardize(preList):
    List=preList[:]
    for i in range(len(List)):
        if ' ' in List[i]:
            List[i]=re.sub(' ','',List[i])
        if "\\u" in List[i]:
            List[i]=re.sub('\\\\u[A-Za-z0-9]+','',List[i])

    return List


def specialHanding(listA,toChecks,toAppends):
    toReturn=listA[:]
    for toCheck in toChecks:
        if toCheck in listA:
            toReturn.append(toAppends[toChecks.index(toCheck)])
    return toReturn


def tagStatistics(NAMES):
    global allNamesExceptChinese
    global characterIndex
    global allNames
    global judgeTag
    global nextHeader
    global sleepTime
    preStatistics=[]
    contentListGlobal=[]
    R18Count=0
    for name in NAMES:
        rawContent=[]
        name=re.sub(' ','',name)
        page=1
        reTry=True
        reTryTimes=0
        contentCount=0
        contentListLanguage=[]
        totalNotEmpty=0
        while reTry:
            requestURL='https://www.pixiv.net/ajax/search/artworks/'+name+'?word='+name+'&order=date_d&mode=all&p='+str(page)+'&s_mode=s_tag_full&type=all&lang=zh&version=1bb9c95cd9cbc108a16ddf9fea198f3210ac5053'
            try:
                Get=requests.session()
                Get.keep_alive=False
                request=Get.get(requestURL,headers=headerPixiv[nextHeader])
                content=json.loads(request.text)
                contentList=re.findall("(\{'id': '\d+', 'title':.*?'tags'.*?userName.*?},)",str(content))
                total=int(re.search("'total': (\d+), ",str(content)).group(1))
                if total>0 and page==1:
                    totalNotEmpty=total
                contentCount+=len(contentList)
                if (contentCount<totalNotEmpty and not contentList) or (not contentList and page==1) or (len(contentList)>total):
                    sleepTime[nextHeader]+=20
                    raise Exception
                if page==1:
                    maxPage=math.ceil(totalNotEmpty/len(contentList))
                sleepTime[nextHeader]=5
                if storeRawData:
                    rawContent.append(name+' FOR PAGE '+str(page)+': \n'+str(content)+'\n\n')
                    rawContent.append('PAGE CONTENT COUNT: '+str(len(contentList)))
                    rawContent.append('\n'.join(contentList)+'\n------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n\n')
                for eachContent in contentList:
                    judgePass=False
                    for eachName in allNames:
                        if eachName!=name:
                            if eachName.lower() in eachContent.lower():
                                judgePass=True
                                break
                    if not judgePass:
                        for toJudge in judgeTag:
                            if toJudge.lower() in eachContent.lower():
                                judgePass=True
                                break
                    if judgePass:
                        contentListLanguage.append(eachContent)
                        if eachContent not in contentListGlobal:
                            contentListGlobal.append(eachContent)
                            if "'xRestrict': 1" in eachContent:
                                R18Count+=1
                page+=1
                reTryTimes=0
                if page>maxPage:
                    reTry=False
            except:
                print('FAILED: '+name+' IN PAGE '+str(page))
                nextHeader=minIndex(sleepTime)
                time.sleep(sleepTime[nextHeader])
                reTryTimes+=1
                if reTryTimes==6 and page==1:
                    reTry=False
                    fails.append(CE+': '+requestURL)
        if storeRawData:
            with open('./rawData/'+name+'.rawData','w+') as rawBin:
                rawBin.write('\n'.join(rawContent))
            rawBin.close()
        preStatistics.append(name+': '+str(len(contentListLanguage)))
    poolSemaphore.release()
    preStatistics.append(NAMES[0]+'(合计): '+str(len(contentListGlobal)))
    if len(contentListGlobal)>0:
        preStatistics.append(NAMES[0]+' R18率: '+str(R18Count/len(contentListGlobal)))
    else:
        preStatistics.append(NAMES[0]+' R18率: 0')
    preStatistics.append('-------------------------------------\n')
    contentToCSV(contentListGlobal,NAMES)
    for preStatistic in preStatistics:
        print(preStatistic)
    lock.acquire()
    if os.path.exists('statistics.PandoraWork'):
        with open('statistics.PandoraWork') as statisticsBinOpen_Inner:
            statisticsOpen_Inner=statisticsBinOpen_Inner.read()
        statisticsBinOpen_Inner.close()
    else:
        statisticsOpen_Inner='-------------------------------------\n'
    with open('statistics.PandoraWork','w+') as statisticsBin:
        statisticsBin.write(statisticsOpen_Inner+'\n'.join(preStatistics))
    statisticsBin.close()
    lock.release()


headerWiki={
    "user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Cache-Control":"no-cache"
}
headerPixiv1={
    "referer": "https://www.pixiv.net/",
    "user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Cookie": PUT YOUR COOKIE HERE PLEASE
    "Cache-Control":"no-cache"
}
headerPixiv2={
    "referer": "https://www.pixiv.net/",
    "user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Cookie": PUT YOUR COOKIE HERE PLEASE
    "Cache-Control":"no-cache"
}
headerPixiv3={
    "referer": "https://www.pixiv.net/",
    "user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Cookie": PUT YOUR COOKIE HERE PLEASE
    "Cache-Control":"no-cache"
}
headerPixiv4={
    "referer": "https://www.pixiv.net/",
    "user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Cookie": PUT YOUR COOKIE HERE PLEASE
    "Cache-Control":"no-cache"
}
nextHeader=0

# MODIFY headerPixiv AND sleepTime IF YOU USE LESS OR MORE COOKIES
# MODIFY headerPixiv AND sleepTime IF YOU USE LESS OR MORE COOKIES
# MODIFY headerPixiv AND sleepTime IF YOU USE LESS OR MORE COOKIES
headerPixiv=[headerPixiv1,headerPixiv2,headerPixiv3,headerPixiv4]
sleepTime=[5,5,5,5]

languages=['en','zh-tw','ja','ko']
countries=['mondstadt','liyue','inazuma','sumeru']
preNameChinese=[]
languageNames=[]
with open('main') as languageMainHTML_Bin:
    languageMainHTML=languageMainHTML_Bin.read()
languageMainHTML_Bin.close()
nameChinese=re.findall('\{title:"(.*?)",',languageMainHTML)

for language in languages:
    with open(language) as languageHTML_Bin:
        languageHTML=languageHTML_Bin.read()
    languageHTML_Bin.close()
    languageNames.append(standardize(re.findall('\{title:"(.*?)",',languageHTML)))

nextCountry=0
allNames=[]
allNamesExceptChinese=[]
for nameIndex in range(len(nameChinese)):
    allNamesExceptChinese.append(removeDuplicationAndKeepOrder([languageNames[nextCountry][nameIndex],languageNames[nextCountry+1][nameIndex],languageNames[nextCountry+2][nameIndex],languageNames[nextCountry+3][nameIndex]],nameChinese[nameIndex]))
    allNamesExceptChinese[-1]=specialHanding(allNamesExceptChinese[-1],['KamisatoAyaka','KaedeharaKazuha','SangonomiyaKokomi','AratakiItto','YaeMiko','KamisatoAyato'],['绫华','万叶','心海','一斗','神子','绫人'])
    allNames=allNames+[nameChinese[-1]]+allNamesExceptChinese[-1]

# LUMINE AND AETHER SPECIAL HANDING
nameChinese.append('荧')
nameChinese.append('空')
allNamesExceptChinese.append(['Lumine','熒','蛍','루미네','蛍(原神)','莹'])
allNamesExceptChinese.append(['Aether','空','空','아이테르','空(原神)'])

allNames.append('荧')
allNames.append('空')
for LumineName in allNamesExceptChinese[-2]:
    allNames.append(LumineName)
for AetherName in allNamesExceptChinese[-1]:
    allNames.append(AetherName)

fails=[]
judgeTag=['原神','Genshin','Impact','米哈游','米哈遊','HoYoLAB','원신','HOYOVERSE','miHoYo','蒙德','璃月','须弥','稻妻','枫丹','纳塔','至冬','提瓦特','Mondstadt','Liyue','Inazuma','Sumeru','Fontaine','Natlan','Snezhnaya','爷','派蒙','Paimon','旅行者','履刑者','屑','森林书','兰纳罗','双子','愚人众','Traveller','Traveler','雷音权现','七星','水','火','岩','冰','风','雷','草','タル蛍','雷电影','雷电真','雷電影','黄金梦乡','深渊','Abyss','七圣召唤','Twins','崩坏','星穹铁道','爱莉希雅','Elysia','女仆','旅人','Travel','公子','捷德','风花节','海灯节','纠缠','Wish','Pull','海祈岛','珊瑚宫','渊下宫','尘歌','萍姥姥','龙脊雪山','苍风高地','风啸山坡','明冠山地','坠星山谷','珉林','璃沙郊','云来海','碧水原','甜甜花','层岩巨渊','Status','天理','琪亚娜','食岩之罚','仙跳墙','佛跳墙','野菇鸡肉串','珊瑚宫','心海','Pyro','Cyro','Hydro','Nature','Anemo','Geo','Dendro','Electro','Swirl','原石','Primogem','Jade','God','Fate','Intertwined','纠缠之缘','Serenitea','Artifact','圣遗物','博士','doctor','同人']

if os.path.exists('statistics.PandoraWork'):
    with open('statistics.PandoraWork') as statisticsBinOpen:
        statisticsOpen=statisticsBinOpen.read()
    statisticsBinOpen.close()
    if len(statisticsOpen) and '-------------------------------------\n' in statisticsOpen:
        processed=re.findall('-------------------------------------\n(.*?): \d+\n','-------------------------------------\n'+statisticsOpen)
    else:
        processed=[]
else:
    statisticsOpen=''
    processed=[]

for p in processed:
    allNamesExceptChinese.pop(nameChinese.index(p))
    nameChinese.remove(p)

lock=threading.Lock()
threadList=[]
characterIndex=0
poolSemaphore=threading.BoundedSemaphore(4)
storeRawData=False
for CE in nameChinese:
    time.sleep(1)
    poolSemaphore.acquire()
    threadI=threading.Thread(target=tagStatistics,args=[[CE]+allNamesExceptChinese[characterIndex]])
    threadI.start()
    threadList.append(threadI)
    characterIndex+=1
    if not characterIndex%6:
        sleepTime=[5]*len(headerPixiv)

for threadI in threadList:
    threadI.join()

with open('fails.PandoraWork','w+') as failsBin:
    failsBin.write('\n'.join(fails))
failsBin.close()
