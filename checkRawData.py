import re

with open('./rawData/刻晴.rawData') as rawBin:
    raw=rawBin.read()
rawBin.close()

ids=re.findall("\n\{'id': '(\d+)'.*?},",raw)
for a in range(len(ids)-1):
    for b in range(a+1,len(ids)):
        if ids[a]==ids[b]:
            print(ids[a])
