#coding=utf-8
import os
import requests
headers={
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'zh-CN,zh;q=0.9',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Connection': 'keep-alive',
                        'Cookie': 'kw_token=WPVJHJO2KD',
                        'csrf': 'WPVJHJO2KD',
                        'Host': 'kuwo.cn',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'same-origin',
                        'Referer': 'https://kuwo.cn/search/list'
        }
url_0 = "https://kuwo.cn/api/www/search/searchMusicBykeyWord?key={0}&pn=1&rn=30&httpsStatus=1&reqId=88432c31-fe6f-11ea-bfec-2f45c636f613".format("林俊杰")
res_0 = requests.get(url_0, headers=headers)
res_0 = res_0.json()
# print(res_0)
music_list = res_0["data"]["list"]
print(music_list[0]['pic'])


