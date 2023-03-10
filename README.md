# Pixiv-Genshin-Artworks-Count-by-Characters
Count Genshin Impact Artworks/Fanarts by Characters on Pixiv/统计Pixiv上各角色同人图数量

## About

Use Python and Requests to Count Artworks of Genshin Impact Characters, and visualization using Matplotlib.

## Usage

0.Please use you cookie and put it into headerPixiv1,headerPixiv2,headerPixiv3,headerPixiv4 etc. 
![48391678422421_ pic](https://user-images.githubusercontent.com/98176983/224223384-3c387bba-9911-4ed5-b90b-c010475dc866.jpg)

0.And then modify List headerPixiv and sleepTime.
![48401678422558_ pic](https://user-images.githubusercontent.com/98176983/224223646-7120b21d-c4ea-4be5-bee6-ba1787cdc6d4.jpg)

1.Run main.py

This may take hours because [Pixiv](https://www.pixiv.net/) dose not welcome creeper, it may block a user's cookie for several minutes, and that is why you may need a few cookies.

Note: main.py can read its generated file(statistics.PandoraWork, plain text) and continue running from the character you suspended.

main.py need language files, the source code from 

[English](https://genshin.hoyoverse.com/en/character/mondstadt?char=0), 

[繁體中文](https://genshin.hoyoverse.com/zh-tw/character/mondstadt?char=0), 

[日本語](https://genshin.hoyoverse.com/ja/character/mondstadt?char=0), 

[Korean](https://genshin.hoyoverse.com/ko/character/mondstadt?char=0) and 

[简体中文](https://ys.mihoyo.com/main/character/mondstadt?char=0).

If you want to update Characters List, please store these source code as 'en','zh-tw','ja','ko' and 'main'.

Note: on [简体中文](https://ys.mihoyo.com/main/character/mondstadt?char=0), the order of 刻晴(Keqing) adn 七七(Qiqi) is wrong.

2.Run visualization.py

if you just wann to see the results, just download the PNG files, no need to run main.py and visualization.py.

## Q&A

Why need more than one cookies?

Becasue Pixiv does not welcome creeper, it will block one cookie if it send many connections in a short period of time for a few minutes.

What is rawData and what does checkRawData.py do?

rawData is the full content that Pixiv responses, you need to change storeRawData=False into storeRawData=True in main.py if you want to keep rawData. 

These Raw Data will be stored into 'rawData' finder.

And you need to write your own checkRawData.py to satisfy your requirement.
