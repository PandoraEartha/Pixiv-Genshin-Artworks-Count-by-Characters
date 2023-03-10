# coding=utf-8
import re
import os
import sys
import math
import requests
import threading
import matplotlib.pyplot as mp
import matplotlib
from matplotlib.offsetbox import AnnotationBbox,OffsetImage


def sortListAlongWithInformation(informationList1,informationList2,List):
    pairs1=zip(List,informationList1)
    z1=[x for _,x in sorted(pairs1,reverse=False)]
    pairs2=zip(List,informationList2)
    z2=[x for _,x in sorted(pairs2,reverse=False)]
    return z1,z2,sorted(List,reverse=False)


def download(linkAndName):
    downloadEd=requests.get(linkAndName[0],headers=headerWiki)
    poolSemaphore.release()
    with open('./icons/'+linkAndName[1]+'.png','wb+') as pngBin:
        pngBin.write(downloadEd.content)
    pngBin.close()


def imageSet(EnglishNamesSorted,numberList,Axes,Limit,a,b):
    nameIndex=-1
    for name in EnglishNamesSorted:
        nameIndex+=1
        xInXybox=math.ceil(a*numberList[nameIndex]+b)
        if xInXybox<=Limit:
            continue
        ImBin=mp.imread('./icons/'+re.sub('([a-z])([A-Z])','\g<1> \g<2>',name)+'.png')
        ImageBox=OffsetImage(ImBin)
        AB=AnnotationBbox(ImageBox,(0,nameIndex),xybox=[xInXybox,0],xycoords='data',boxcoords="offset points")
        Axes.add_artist(AB)
        if nameIndex>=len(EnglishNamesSorted):
            break


def getColors(EnglishNamesSorted,Elements,Colors):
    color=[]
    for name in EnglishNamesSorted:
        color.append(Colors[Elements[re.sub('([a-z])([A-Z])','\g<1> \g<2>',name)]])
    return color


def getGenderAndRating(EnglishNames):
    HTML=requests.get('https://genshin-impact.fandom.com/wiki/Character/List').text
    Gender={}
    Rating={}
    MaleCount=0
    FemaleCount=0
    FiveStarCount=0
    FourStarCount=0
    for name in EnglishNames:
        if name=='Aether':
            Gender[name]='Male'
            Rating[name]=5
            MaleCount+=1
            FiveStarCount+=1
            continue
        if name=='Lumine':
            Gender[name]='Female'
            Rating[name]=5
            FemaleCount+=1
            FiveStarCount+=1
            continue
        N=re.sub('([a-z])([A-Z])','\g<1> \g<2>',name)
        toRE_InDef=re.compile('" title="'+N+'".*?img alt="(\d) Stars".*?title="Category:.*?(Female|Male) Characters">',re.S)
        preGender=re.search(toRE_InDef,HTML).group(2)
        if preGender=='Male':
            MaleCount+=1
        else:
            FemaleCount+=1
        Gender[name]=preGender
        preRating=int(re.search(toRE_InDef,HTML).group(1))
        if preRating==5:
            FiveStarCount+=1
        else:
            FourStarCount+=1
        Rating[name]=int(re.search(toRE_InDef,HTML).group(1))
    return Gender,MaleCount,FemaleCount,Rating,FiveStarCount,FourStarCount


with open('statistics.PandoraWork') as statisticsBin:
    statistics=statisticsBin.read()
statisticsBin.close()

chineseNames=re.findall('(.*?):.*?-------------------------------------\n',statistics,re.S)
englishNames=re.findall('([A-Za-z]+):.*?-------------------------------------\n',statistics,re.S)
if os.path.exists('./icons'):
    iconFiles=os.listdir('./icons')
else:
    os.mkdir('./icons')
    iconFiles=[]

total=re.findall('\(合计\): (\d+)\n',statistics)
R18Rate=re.findall('R18率: ([\d.]+)\n',statistics)
R18Count=[]
for rateIndex in range(len(R18Rate)):
    R18Rate[rateIndex]=float(R18Rate[rateIndex])
    total[rateIndex]=int(total[rateIndex])
    R18Count.append(math.floor(R18Rate[rateIndex]*total[rateIndex]))

chineseNamesSorted,englishNamesSorted,totalSorted=sortListAlongWithInformation(chineseNames,englishNames,total)
chineseNamesR18Count,englishNamesR18Count,R18CountSorted=sortListAlongWithInformation(chineseNames,englishNames,R18Count)
chineseNamesR18Rate,englishNamesR18Rate,R18RateSorted=sortListAlongWithInformation(chineseNames,englishNames,R18Rate)

with open('en',encoding='utf-8') as informationBin:
    information=informationBin.read()
informationBin.close()

headerWiki={
    "user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Cache-Control":"no-cache"
}

pngLinks=[]
elements={}
colorsDictionary={'Light':(255/255,255/255,255/255),'Pyro':(250/255,120/255,59/255),'Hydro':(97/255,192/255,250/255),'Anemo':(96/255,219/255,178/255),'Electro':(179/255,141/255,193/255),'Dendro':(159/255,201/255,36/255),'Cryo':(165/255,214/255,230/255),'Geo':(255/255,227/255,0/255)}
if os.path.exists('colorHTML'):
    with open('colorHTML') as colorsBin:
        colorHTML=colorsBin.read()
    colorsBin.close()
else:
    colorHTML=requests.get('https://genshin-builds.com/characters',headers=headerWiki).text
    with open('colorHTML','w+',encoding='utf-8') as colorsBin:
        colorsBin.write(colorHTML)
    colorsBin.close()

for i in range(len(englishNamesSorted)):
    if englishNamesSorted[i]!='Lumine' and englishNamesSorted[i]!='Aether':
        englishNamesSorted[i]=re.sub('([a-z])([A-Z])','\g<1> \g<2>',englishNamesSorted[i])
        toRE=re.compile('"name":"'+englishNamesSorted[i]+'","element":"(.*?)"')
        elements[englishNamesSorted[i]]=re.search(toRE,colorHTML).group(1)
        if not englishNamesSorted[i]+'.png' in iconFiles:
            toRE=re.compile('\{title:"'+englishNamesSorted[i]+'",icon:"(.*?png)"')
            pngLinks.append([re.sub('\\\\u002F','/',re.search(toRE,information).group(1)),englishNamesSorted[i]])
    else:
        elements['Lumine']='Light'
        elements['Aether']='Light'

colorsTotal=getColors(englishNamesSorted,elements,colorsDictionary)
colorsR18Count=getColors(englishNamesR18Count,elements,colorsDictionary)
colorsR18Rate=getColors(englishNamesR18Rate,elements,colorsDictionary)

threadList=[]
poolSemaphore=threading.BoundedSemaphore(16)
for pngLink in pngLinks:
    poolSemaphore.acquire()
    threadI=threading.Thread(target=download,args=[pngLink])
    threadI.start()
    threadList.append(threadI)

for threadI in threadList:
    threadI.join()

genshinFont=matplotlib.font_manager.FontProperties(fname='原神0.82.ttf')
mp.rcParams['axes.unicode_minus']=False
mp.rcParams['figure.figsize']=(30,180)

if True:
    figure,axes=mp.subplots(1,1)
    patch=axes.patch
    patch.set_color((32/255,33/255,42/255))
    Barh=mp.barh(chineseNamesSorted,totalSorted,color=colorsTotal)
    mp.xlim(0,int(math.ceil(totalSorted[-1]/3000)*3000))
    matplotlib.pyplot.xticks(fontproperties=genshinFont,fontsize=70)
    matplotlib.pyplot.yticks(fontproperties=genshinFont,fontsize=70)
    mp.bar_label(Barh,labels=totalSorted,fontproperties=genshinFont,fontsize=40,color='white',padding=20)
    imageSet(englishNamesSorted,totalSorted,axes,106,0.06205,-57)
    mp.title('ARTWORKS ON PIXIV PER CHARACTER',fontproperties=genshinFont,fontsize=80)
    mp.savefig('visualized_total.png',bbox_inches='tight')

if True:
    mp.rcParams['figure.figsize']=(45,180)
    figure,axes=mp.subplots(1,1)
    patch=axes.patch
    patch.set_color((32/255,33/255,42/255))
    Barh=mp.barh(chineseNamesR18Rate,R18RateSorted,color=colorsR18Rate)
    matplotlib.pyplot.xticks(fontproperties=genshinFont,fontsize=70)
    matplotlib.pyplot.yticks(fontproperties=genshinFont,fontsize=70)
    mp.bar_label(Barh,labels=[int(x*1000)/1000 for x in R18RateSorted],fontproperties=genshinFont,fontsize=40,color='white',padding=20)
    imageSet(englishNamesR18Rate,R18RateSorted,axes,0,6307,-45)
    mp.title('R18 RATE OF ARTWORKS ON PIXIV PER CHARACTER',fontproperties=genshinFont,fontsize=80)
    mp.savefig('visualized_R18Rate.png',bbox_inches='tight')

if True:
    mp.rcParams['figure.figsize']=(45,180)
    figure,axes=mp.subplots(1,1)
    patch=axes.patch
    patch.set_color((32/255,33/255,42/255))
    Barh=mp.barh(chineseNamesR18Count,R18CountSorted,color=colorsR18Count)
    matplotlib.pyplot.xticks(fontproperties=genshinFont,fontsize=70)
    matplotlib.pyplot.yticks(fontproperties=genshinFont,fontsize=70)
    mp.bar_label(Barh,labels=R18CountSorted,fontproperties=genshinFont,fontsize=40,color='white',padding=20)
    imageSet(englishNamesR18Count,R18CountSorted,axes,106,0.2875,-55)
    mp.title('R18 COUNT OF ARTWORKS ON PIXIV PER CHARACTER',fontproperties=genshinFont,fontsize=80)
    mp.savefig('visualized_R18Count.png',bbox_inches='tight')

gender,maleCount,femaleCount,rating,star5count,star4count=getGenderAndRating(englishNamesR18Count)
maleWorksCount=0
femaleWorksCount=0
for name in gender.keys():
    N=re.sub('([a-z])([A-Z])','\g<1> \g<2>',name)
    if gender[name]=='Female':
        femaleWorksCount+=totalSorted[englishNamesSorted.index(N)]
    else:
        maleWorksCount+=totalSorted[englishNamesSorted.index(N)]

if True:
    mp.rcParams['figure.figsize']=(20,20)
    figure,axes=mp.subplots(1,1)
    patch=axes.patch
    Pie=mp.pie([maleWorksCount,femaleWorksCount],explode=(0.1,0),labels=['Male','Female'],colors=["#82C4E4","#FFC0CB"],textprops={'fontproperties':genshinFont,'fontsize':45},autopct='%1.2f%%',startangle=-30)
    mp.title('GENDER RATION OF ARTWORKS',fontproperties=genshinFont,fontsize=50)
    mp.savefig('visualized_GenderRation.png',bbox_inches='tight')

if True:
    mp.rcParams['figure.figsize']=(20,20)
    figure,axes=mp.subplots(1,1)
    Bar=mp.bar(['Male','Female'],[maleWorksCount/maleCount,femaleWorksCount/femaleCount],color=["#82C4E4","#FFC0CB"])
    matplotlib.pyplot.xticks(fontproperties=genshinFont,fontsize=50)
    matplotlib.pyplot.yticks(fontproperties=genshinFont,fontsize=30)
    mp.bar_label(Bar,labels=[str(int(maleWorksCount/maleCount*1000)/1000),str(int(femaleWorksCount/femaleCount*1000)/1000)],fontsize=45,fontproperties=genshinFont)
    mp.title('AVERAGE ARTWORKS BY GENDER',fontproperties=genshinFont,fontsize=50)
    mp.savefig('visualized_GenderAverage.png',bbox_inches='tight')


if True:
    mp.rcParams['figure.figsize']=(20,20)
    figure,axes=mp.subplots(1,1)
    patch=axes.patch
    Sum=sum(totalSorted)
    for i in range(len(chineseNamesSorted)):
        if totalSorted[i]/Sum>0.0274:
            chineseNamesSortedPart=chineseNamesSorted[i:]
            totalSortedPart=totalSorted[i:]
            colorsTotalPart=colorsTotal[i:]
            chineseNamesSortedPart.append('其它角色')
            totalSortedPart.append(sum(totalSorted[:i]))
            colorsTotalPart.append((180/255,180/255,180/255))
            break

    Pie=mp.pie(totalSortedPart,labels=chineseNamesSortedPart,colors=colorsTotalPart,textprops={'fontproperties':genshinFont,'fontsize':30},autopct='%1.2f%%',startangle=-30,wedgeprops={'edgecolor':'gray','linewidth':2})
    mp.title('ARTWORKS RATION BY CHARACTERS',fontproperties=genshinFont,fontsize=50)
    mp.savefig('visualized_ArtworksRation.png',bbox_inches='tight')


star5WorksCount=0
star4WorksCount=0
for name in rating.keys():
    N=re.sub('([a-z])([A-Z])','\g<1> \g<2>',name)
    if rating[name]==5:
        star5WorksCount+=totalSorted[englishNamesSorted.index(N)]
    else:
        star4WorksCount+=totalSorted[englishNamesSorted.index(N)]

if True:
    mp.rcParams['figure.figsize']=(20,20)
    figure,axes=mp.subplots(1,1)
    patch=axes.patch
    Pie=mp.pie([star5WorksCount,star4WorksCount],explode=(0.1,0),labels=['5 Stars','4 Stars'],colors=["#CF8439","#9C80C7"],textprops={'fontproperties':genshinFont,'fontsize':45},autopct='%1.2f%%',startangle=30)
    mp.title('RATING RATION OF ARTWORKS',fontproperties=genshinFont,fontsize=50)
    mp.savefig('visualized_RatingRation.png',bbox_inches='tight')

if True:
    mp.rcParams['figure.figsize']=(20,20)
    figure,axes=mp.subplots(1,1)
    patch=axes.patch
    Bar=mp.bar(['5 Stars','4 Stars'],[star5WorksCount/star5count,star4WorksCount/star4count],color=["#CF8439","#9C80C7"])
    matplotlib.pyplot.xticks(fontproperties=genshinFont,fontsize=50)
    matplotlib.pyplot.yticks(fontproperties=genshinFont,fontsize=30)
    mp.bar_label(Bar,labels=[str(int(star5WorksCount/star5count*1000)/1000),str(int(star4WorksCount/star4count*1000)/1000)],fontsize=45,fontproperties=genshinFont)
    mp.title('AVERAGE ARTWORKS BY RATING',fontproperties=genshinFont,fontsize=50)
    mp.savefig('visualized_RatingAverage.png',bbox_inches='tight')


femaleR18Rate=0
maleR18Rate=0
femaleR18Count=0
maleR18Count=0
for name in gender.keys():
    if gender[name]=='Female':
        femaleR18Rate+=R18RateSorted[englishNamesR18Rate.index(name)]
        femaleR18Count+=R18CountSorted[englishNamesR18Count.index(name)]
    else:
        maleR18Rate+=R18RateSorted[englishNamesR18Rate.index(name)]
        maleR18Count+=R18CountSorted[englishNamesR18Count.index(name)]

if True:
    mp.rcParams['figure.figsize']=(20,20)
    figure,axes=mp.subplots(1,1)
    patch=axes.patch
    Pie=mp.pie([maleR18Count,femaleR18Count],explode=(0.1,0),labels=['Male','Female'],colors=["#82C4E4","#FFC0CB"],textprops={'fontproperties':genshinFont,'fontsize':45},autopct='%1.2f%%',startangle=-30)
    mp.title('R18 ARTWORKS COUNT BY GENDER',fontproperties=genshinFont,fontsize=50)
    mp.savefig('visualized_R18CountGender.png',bbox_inches='tight')

if True:
    mp.rcParams['figure.figsize']=(20,20)
    figure,axes=mp.subplots(1,1)
    Bar=mp.bar(['Male','Female'],[maleR18Rate/maleCount,femaleR18Rate/femaleCount],color=["#82C4E4","#FFC0CB"])
    matplotlib.pyplot.xticks(fontproperties=genshinFont,fontsize=50)
    matplotlib.pyplot.yticks(fontproperties=genshinFont,fontsize=30)
    mp.bar_label(Bar,labels=[str(int(maleR18Rate/maleCount*1000)/1000),str(int(femaleR18Rate/femaleCount*1000)/1000)],fontsize=45,fontproperties=genshinFont)
    mp.title('R18 RATION BY GENDER',fontproperties=genshinFont,fontsize=50)
    mp.savefig('visualized_R18GenderAverageRation.png',bbox_inches='tight')