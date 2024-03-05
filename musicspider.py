#coding=utf-8
import os
import requests
 
 
 
class KuWomusic():
    def __init__(self):
        self.headers2={
            'Referer': 'https://kuwo.cn/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        }
        self.headers={
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
        self.singer = [] 
        self.song = [] 
        self.rid = [] 
        self.songTimeMinutes = [] 
        self.url = [] 
    def search(self):
        key = input('请输入想听的歌：')
        url_0 = "https://kuwo.cn/api/www/search/searchMusicBykeyWord?key={0}&pn=1&rn=30&httpsStatus=1&reqId=88432c31-fe6f-11ea-bfec-2f45c636f613".format(key)
        res_0 = requests.get(url_0,headers=self.headers)
        res_0 = res_0.json()
        music_list = res_0["data"]["list"]
        ip = 0
        for music in music_list:
                singer = music["artist"]
                song = music["name"]
                rid = music["rid"]
                songTimeMinutes = music["songTimeMinutes"]
 
                self.singer.append(singer)
                self.song.append(song)
                self.rid.append(rid)
                self.songTimeMinutes.append(songTimeMinutes)
        self.select()
 
    def select(self):
        ip = 0
        for song, singer, rid, songTimeMinutes in zip(self.song, self.singer, self.rid, self.songTimeMinutes):
            print(ip,song,singer,songTimeMinutes)
            ip += 1
        while True:
            ip = input("请输入序号：")
            ip = int(ip)
            if ip == -1:
                break
            song = self.song[ip]
            singer = self.singer[ip]
            rid = self.rid[ip]
            self.download(song,singer,rid)
    def download(self,song,singer,rid):
        url_1 = 'https://kuwo.cn/url?format=mp3&rid={0}&response=url&type=convert_url3&br=320kmp3&from=web&t=1600959341055&httpsStatus=1&reqId=03bd6000-fe76-11ea-a79c-9575039ac1cf'.format(rid)
        response = requests.get(url_1, headers=self.headers)
        dict = response.json()
        url = dict['url']
        music = requests.get(url,headers=self.headers2).content
        dir = os.getcwd()
        dir = os.path.join(dir, "酷我音乐 ")
        if not os.path.exists(dir):
            os.mkdir(dir)  # 构造文件夹
        os.chdir(dir)  # 将下载的歌曲存储在该文件夹
        print(song, singer)
        file_name =  song + '-' + singer + '.mp3'  # 文件名
        with open(file_name, 'wb') as f:
            f.write(music)
        print("下载成功！")
 
if __name__ == '__main__':
        music = KuWomusic()
        music.search()