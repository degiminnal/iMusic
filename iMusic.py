import wx
import os
import time
import eyed3
import random
import win32api
import win32con
import PIL
from PIL import Image
import requests
from tkinter import *
from win32com.client import Dispatch
from tkinter.filedialog import askopenfilenames


class MusicSpider:
    def __init__(self):
        self.songInfos = {"songId": [], "songName": [], "artist": [], "album": [], "songLink": [],
                          "mapLink": [], "songTextLink": []}
        self.page = 0
        self.headers = {
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

    def get_infos(self, key):
        url_0 = "https://kuwo.cn/api/www/search/searchMusicBykeyWord?key={0}&pn=1&rn=30&httpsStatus=1&reqId=88432c31-fe6f-11ea-bfec-2f45c636f613".format("林俊杰")
        self.songInfos = {"songId": [], "songName": [], "artist": [], "album": [], "songLink": [],
                          "mapLink": [], "songTextLink": []}
        # if self.page == 0:
        if 1:
            search_response = requests.get(url_0, headers=self.headers)
        # else:
            # search_response = requests.get("http://music.taihe.com/search?key=%s&start=%d&size=%d" % (key, self.page * 20, 20))
        search_response.encoding = "utf-8"
        search_response = search_response.json()
        music_list = search_response["data"]["list"]
        for music in music_list:
            self.songInfos["artist"].append(music["artist"])
            self.songInfos["songName"].append(music["name"])
            self.songInfos["songId"].append(music["musicrid"])
            self.songInfos["album"].append(music["album"])
            self.songInfos["songLink"].append('https://kuwo.cn/url?format=mp3&rid={0}&response=url&type=convert_url3&br=320kmp3&from=web&t=1600959341055&httpsStatus=1&reqId=03bd6000-fe76-11ea-a79c-9575039ac1cf'.format(music["musicrid"]))
            self.songInfos["mapLink"].append(music['pic'])
            self.songInfos["songTextLink"].append("[00:02.54]")


class MusicFrame(wx.Frame):
    def __init__(self):
        frame_width = 1000
        frame_height = 650
        frame_x = (win32api.GetSystemMetrics(win32con.SM_CXSCREEN) - frame_width) / 2
        frame_y = (win32api.GetSystemMetrics(win32con.SM_CYSCREEN) - frame_height) / 2
        wx.Frame.__init__(self, None, -1, '艾音乐', pos=(frame_x, frame_y), size=(frame_width, frame_height))
        panel = wx.Panel(self, -1, style=wx.BORDER_NONE)
        self.SetSizeHints(wx.Size(1000, 650), wx.Size(1000, 650))
        self.songText = [[], []]  # 保存歌词文件信息，包括时间
        self.songTextToShow = ["", "begin", "软件名：iMusic", "功能：音乐爬虫 && 音乐播放器", "作者：梁德民",
                               "时间：2019/02/13", "end", ""]  # 保存要显示的歌词

        # 音乐播放控件wmp
        self.root = Tk()
        self.root.withdraw()
        self.spider = MusicSpider()
        self.wmp = Dispatch("WMPlayer.OCX")
        self.wmp.settings.Volume = 30

        # 关键数据
        self.key = ""
        self.SX = 0  # 0：列表循环 1：随机播放 2：单曲循环
        self.page = 0
        self.during = 0
        self.lrcIndex = -1
        self.lrc_able = 0  # 正在播放的歌曲是否有相匹配的歌词
        self.textSay = ""
        self.isPlaying = 0
        self.songPlayIndex = -1
        self.songInfos = {"id": [], "songName": [], "artists": [], "albums": []}  # 从网页爬取的歌曲id,名称，歌手名字，专辑名
        self.songListInfo = {"num": 0, "songNames": [], "artists": [], "albums": []}  # 保存要显示的歌曲名称，歌手，专辑
        self.urls = {"song": [], "map": [], "text": []}  # 保存歌曲链接，图片链接，歌词链接
        self.songQueue = {"filepath": [], "songName": [], "map_path": [], "songText": [], "songLength": []}
        self.tempSongName = ""  # 正在播放的歌曲名
        self.tempSongLength = 0  # 正在播放的歌曲时长
        self.tempAlbum = "default"
        self.lastTime = 0.0
        self.beginTime = 0.0
        self.presentTime = 0.0  # 歌曲已播放的时间

        # 计时器
        self.timer = wx.Timer(self, -1)
        self.timer.Start(100)

        # wx控件生成--专辑图片
        self.jpg = wx.Image("./emoji/%s.jpg" % self.tempAlbum, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.mapAlbum = wx.StaticBitmap(panel, -1, self.jpg, (25, 45), size=(self.jpg.GetWidth(), self.jpg.GetHeight()))

        # wx控件生成--声音控制，开始，暂停，上一曲，下一曲，清空队列
        self.voice = wx.Image("./emoji/voice.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.start = wx.Image("./emoji/start.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.pause = wx.Image("./emoji/pause.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.next = wx.Image("./emoji/next.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.previous = wx.Image("./emoji/previous.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.stop = wx.Image("./emoji/stop.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.sui_ji = wx.Image("./emoji/suiJi.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.xun_han = wx.Image("./emoji/xunHan.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.dan_qu = wx.Image("./emoji/danQu.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.btnStartAndPause = wx.BitmapButton(panel, wx.ID_ANY, self.start, (150, 500), (25, 25), wx.BU_AUTODRAW)
        self.btnPrevious = wx.BitmapButton(panel, wx.ID_ANY, self.previous, (110, 500), (25, 25), wx.BU_AUTODRAW)
        self.btnNext = wx.BitmapButton(panel, wx.ID_ANY, self.next, (190, 500), (25, 25), wx.BU_AUTODRAW)
        self.btnStop = wx.BitmapButton(panel, wx.ID_ANY, self.stop, (230, 500), (25, 25), wx.BU_AUTODRAW)
        self.btnSX = wx.BitmapButton(panel, wx.ID_ANY, self.xun_han, (270, 500), (25, 25), wx.BU_AUTODRAW)
        self.mapVoice = wx.StaticBitmap(panel, -1, self.voice, (70, 545),
                                        size=(self.voice.GetWidth(), self.voice.GetHeight()))
        self.sldVoice = wx.Slider(panel, wx.ID_ANY, 30, 0, 100, (110, 550), (200, 15), wx.SL_HORIZONTAL)
        self.stcTextVoice = wx.StaticText(panel, -1, "30", (320, 547), (30, -1), wx.ALIGN_LEFT)

        # 音乐播放进度
        self.gauge = wx.Gauge(panel, wx.ID_ANY, 100, (65, 460), wx.Size(260, 8), wx.GA_HORIZONTAL)
        self.gauge.SetValue(0)
        self.stcTextPresentTime = wx.StaticText(panel, -1, self.int_to_time(self.presentTime), (20, 455), (35, -1), wx.ALIGN_LEFT)
        self.stcTextTempSongLength = wx.StaticText(panel, -1, self.int_to_time(self.tempSongLength), (340, 455), (35, -1))

        # 歌词显示
        self.songShowText = []
        for i in range(0, 8):
            self.songShowText.append(wx.StaticText(panel, -1, self.songTextToShow[i], pos=(30, 220+30*i),
                                                   size=(300, 20), style=wx.ALIGN_CENTER))

        # 待播放的歌曲队列
        wx.StaticText(panel, -1, "播放列表 :", pos=(190, 45), size=(180, -1), style=wx.ALIGN_LEFT)
        self.stcTextSongQueue = []
        for i in range(0, 7):
            self.stcTextSongQueue.append(wx.StaticText(panel, -1, "", pos=(190, 65+20*i),
                                                       size=(180, 20), style=wx.ALIGN_LEFT))
        # self.stcTextSongQueue[5].SetForegroundColour("Blue")
        # self.stcTextSongQueue[6].SetLabel("")

        # 搜索歌曲
        self.txtSearch = wx.TextCtrl(panel, -1, self.key, pos=(400, 20), size=(100, 20),
                                     style=wx.TE_PROCESS_ENTER | wx.TE_WORDWRAP | wx.TE_RICH2)
        self.btnSearch = wx.Button(panel, -1, "搜索", pos=(510, 20), size=(70, 20))
        self.btnLoadNativeMusic = wx.Button(panel, -1, "本地歌曲", pos=(600, 20), size=(70, 20))

        # 进程消息通知
        self.stcTextSay = wx.StaticText(panel, -1, self.textSay, (850, 23), (130, 20), style=wx.ALIGN_LEFT)

        # 翻页，页码显示
        self.btnPrevPage = wx.Button(panel, -1, "上一页", pos=(550, 585), size=(70, 20))
        self.btnNextPage = wx.Button(panel, -1, "下一页", pos=(720, 585), size=(70, 20))
        self.pageText = wx.StaticText(panel, wx.ID_ANY, str(self.page), (645, 585), (50, -1), wx.ALIGN_CENTER)

        # 歌曲列表
        self.btnAddToPlays = []
        wx.StaticText(panel, wx.ID_ANY, "歌曲名称", (420, 50), (230, 20), wx.ALIGN_LEFT)
        wx.StaticText(panel, wx.ID_ANY, "歌手", (670, 50), (90, 20), wx.ALIGN_LEFT)
        wx.StaticText(panel, wx.ID_ANY, "专辑", (770, 50), (250, 20), wx.ALIGN_LEFT)
        self.stcTextSongNames = []
        self.stcTextAuthors = []
        self.stcTextAlbums = []
        for i in range(0, 20):
            t = 75 + 25 * i
            self.stcTextSongNames.append(wx.StaticText(panel, wx.ID_ANY, "", (420, t), (230, -1), wx.ALIGN_LEFT))
            self.stcTextAuthors.append(wx.StaticText(panel, wx.ID_ANY, "", (670, t), (90, -1), wx.ALIGN_LEFT))
            self.stcTextAlbums.append(wx.StaticText(panel, wx.ID_ANY, "", (770, t), (230, -1), wx.ALIGN_LEFT))
            self.btnAddToPlays.append(wx.Button(panel, -1, "", pos=(390, t + 3), size=(15, 15)))
            # self.btnAddToPlays[i].Disable()

        # 搭建事件和函数的联系
        self.Bind(wx.EVT_BUTTON, self.input_native_music, self.btnLoadNativeMusic)
        self.Bind(wx.EVT_BUTTON, self.start_and_pause, self.btnStartAndPause)
        self.Bind(wx.EVT_BUTTON, self.music_stop, self.btnStop)
        self.Bind(wx.EVT_BUTTON, self.next_music, self.btnNext)
        self.Bind(wx.EVT_BUTTON, self.previous_music, self.btnPrevious)
        self.Bind(wx.EVT_TIMER, self.click, self.timer)
        self.Bind(wx.EVT_BUTTON, self.play_sx, self.btnSX)
        self.sldVoice.Bind(wx.EVT_SCROLL_CHANGED, self.change_voice)
        self.Bind(wx.EVT_TEXT_ENTER, self.getinfo, self.txtSearch)
        self.Bind(wx.EVT_BUTTON, self.getinfo, self.btnSearch)
        self.Bind(wx.EVT_BUTTON, self.next_page, self.btnNextPage)
        self.Bind(wx.EVT_BUTTON, self.previous_page, self.btnPrevPage)

        self.Bind(wx.EVT_BUTTON, self.bt0_click, self.btnAddToPlays[0])
        self.Bind(wx.EVT_BUTTON, self.bt1_click, self.btnAddToPlays[1])
        self.Bind(wx.EVT_BUTTON, self.bt2_click, self.btnAddToPlays[2])
        self.Bind(wx.EVT_BUTTON, self.bt3_click, self.btnAddToPlays[3])
        self.Bind(wx.EVT_BUTTON, self.bt4_click, self.btnAddToPlays[4])
        self.Bind(wx.EVT_BUTTON, self.bt5_click, self.btnAddToPlays[5])
        self.Bind(wx.EVT_BUTTON, self.bt6_click, self.btnAddToPlays[6])
        self.Bind(wx.EVT_BUTTON, self.bt7_click, self.btnAddToPlays[7])
        self.Bind(wx.EVT_BUTTON, self.bt8_click, self.btnAddToPlays[8])
        self.Bind(wx.EVT_BUTTON, self.bt9_click, self.btnAddToPlays[9])
        self.Bind(wx.EVT_BUTTON, self.bt10_click, self.btnAddToPlays[10])
        self.Bind(wx.EVT_BUTTON, self.bt11_click, self.btnAddToPlays[11])
        self.Bind(wx.EVT_BUTTON, self.bt12_click, self.btnAddToPlays[12])
        self.Bind(wx.EVT_BUTTON, self.bt13_click, self.btnAddToPlays[13])
        self.Bind(wx.EVT_BUTTON, self.bt14_click, self.btnAddToPlays[14])
        self.Bind(wx.EVT_BUTTON, self.bt15_click, self.btnAddToPlays[15])
        self.Bind(wx.EVT_BUTTON, self.bt16_click, self.btnAddToPlays[16])
        self.Bind(wx.EVT_BUTTON, self.bt17_click, self.btnAddToPlays[17])
        self.Bind(wx.EVT_BUTTON, self.bt18_click, self.btnAddToPlays[18])
        self.Bind(wx.EVT_BUTTON, self.bt19_click, self.btnAddToPlays[19])

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_close(self, event):
        wx.Exit()

    def refresh_lrc(self):
        if self.lrc_able == 0:
            return
        n = self.presentTime
        w = round(n)
        s = str(int(w) % 60)
        m = str(int(w) // 60)
        z = str(round(n * 100) % 100)
        while len(s) < 2:
            s = "0" + s
        while len(m) < 2:
            m = "0" + m
        while len(z) < 2:
            z = "0" + z
        t = m + ":" + s + "." + z
        if self.lrcIndex < len(self.songText[0]) - 1 and self.songText[0][self.lrcIndex + 1] <= t:
            self.lrcIndex += 1
            self.lrc_move()

    # 计时器工作
    def click(self, event):
        if self.isPlaying == 0:
            return
        self.presentTime = time.time() - self.beginTime + self.lastTime  # 获取当前歌曲的播放时间
        self.refresh_progress()
        self.refresh_lrc()

    def lrc_move(self):  # 歌词移动，在timer里面调用
        for i in range(0, 7):
            self.songShowText[i].SetLabel(self.songShowText[i + 1].GetLabel())
        if self.lrcIndex + 4 >= len(self.songText[0]):
            self.songShowText[7].SetLabel("")
        else:
            self.songShowText[7].SetLabel(self.songText[1][self.lrcIndex + 4][:60])

    def lrc_put(self):  # 音乐开始时歌词显示
        self.songShowText[3].SetForegroundColour("Red")
        for i in range(0, 8):
            self.songShowText[i].SetLabel("")
        for i in range(4, 8):
            self.songShowText[i].SetLabel(self.songText[1][i-4])

    def play_sx(self, event):
        self.SX = (self.SX + 1) % 3
        if self.SX == 0:
            self.btnSX.SetBitmap(self.xun_han)
        elif self.SX == 1:
            self.btnSX.SetBitmap(self.sui_ji)
        else:
            self.btnSX.SetBitmap(self.dan_qu)

    def read_lrc(self):  # 读取歌词
        if os.path.exists(self.songQueue["songText"][self.songPlayIndex]) == 0:
            for i in self.songShowText:
                i.SetLabel("")
            self.songShowText[3].SetForegroundColour("Black")
            self.songShowText[3].SetLabel("暂无歌词")
            self.lrc_able = 0
        else:
            self.lrc_able = 1
            lrc_file = open(self.songQueue["songText"][self.songPlayIndex], 'r', encoding="utf-8")
            s = lrc_file.read().split("\n")
            for i in s:
                if i[1:3].isdigit():
                    self.songText[0].append(i[1:9])
                    self.songText[1].append(i[10:])

    def refresh_progress(self):
        self.gauge.SetValue(self.presentTime/self.tempSongLength*100)
        self.stcTextPresentTime.SetLabel(self.int_to_time(self.presentTime))
        if self.presentTime >= self.tempSongLength:
            if self.SX == 0:
                self.next_music(wx.EVT_BUTTON)
            elif self.SX == 1:
                self.random_play()
            else:
                self.play()

    def refresh_picture(self):
        if os.path.exists(self.songQueue["map_path"][self.songPlayIndex]) == 0:
            temp_map = self.jpg
        else:
            temp_map = wx.Image(self.songQueue["map_path"][self.songPlayIndex], wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.mapAlbum.SetBitmap(temp_map)

    def refresh_song_list(self):
        names = self.spider.songInfos["songName"]
        artists = self.spider.songInfos["artist"]
        albums = self.spider.songInfos["album"]
        for i in range(len(names), 20):
            self.stcTextSongNames[i].SetLabel("")
            self.stcTextAuthors[i].SetLabel("")
            self.stcTextAlbums[i].SetLabel("")
        for i in range(0, len(names)):
            self.stcTextSongNames[i].SetLabel(names[i][:35])
            self.stcTextAuthors[i].SetLabel(artists[i][:13])
            self.stcTextAlbums[i].SetLabel(albums[i][:30])

    def refresh_page_id(self):
        self.pageText.SetLabel(str(self.spider.page + 1))

    def refresh_song_in_queue(self):
        index = self.songPlayIndex
        page_first_one = index - index % 6
        page_last_one = page_first_one + 5
        if page_last_one > len(self.songQueue["songName"])-1:
            page_last_one = len(self.songQueue["songName"])-1
        for i in self.stcTextSongQueue:
            i.SetLabel("")
        for idx in range(page_first_one, page_last_one+1):
            i = idx % 6
            self.stcTextSongQueue[i].SetLabel(self.songQueue["songName"][idx][:25])
            self.stcTextSongQueue[i].SetForegroundColour("Black")
        self.stcTextSongQueue[index % 6].SetForegroundColour("Blue")
        if page_last_one < len(self.songQueue["songName"]) - 1:
            self.stcTextSongQueue[6].SetLabel(". . . . . .")

    # 获取根据关键字从网络获取歌曲信息(songId, songName, artist, album，songLink, mapLink, lrcLink)
    def getinfo(self, event):
        self.spider.page = 0
        self.key = self.txtSearch.GetValue()
        self.spider.get_infos(self.key)
        self.refresh_song_list()
        self.refresh_page_id()

    # 浏览本地音乐
    def input_native_music(self, event):
        filenames = askopenfilenames(title="艾音乐", filetypes=[("mp3文件", "*.mp3"), ("WMA文件", "*.wma"),
                                                             ("WAV文件", "*.wav")])
        if not filenames:
            return
        for i in range(0, len(filenames)):
            filename = filenames[i]
            coco = eyed3.load(filename)  # eyed3模块读取mp3信息
            self.add_to_queue(coco.tag.title, coco.tag.album, filename, int(coco.info.time_secs))
        if self.songPlayIndex == -1 and self.songQueue["songName"] != []:
            self.songPlayIndex = 0
            self.tempSongLength = self.songQueue["songLength"][self.songPlayIndex]
        self.refresh_song_in_queue()
        self.refresh_progress()
        self.refresh_picture()

    def add_to_queue(self, song_name, album, song_path, song_length):
        self.songQueue["songName"].append(song_name)
        self.songQueue["map_path"].append("./download/%s.jpg" % album)
        self.songQueue["filepath"].append(song_path)
        self.songQueue["songText"].append(song_path[:-3]+"lrc")
        self.songQueue["songLength"].append(song_length)

    # 播放控制函数，包括下载，加入列表，清空列表，播放，暂停，停止，上一首，下一首，声音调大，声音调小
    def download(self, n):
        header = {
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
        headers2 = {
            'Referer': 'https://kuwo.cn/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        }
        song_id = self.spider.songInfos["songId"][n]
        name = self.spider.songInfos["songName"][n]
        song_link = self.spider.songInfos["songLink"][n]
        album = self.spider.songInfos["album"][n]
        map_link = self.spider.songInfos["mapLink"][n]
        song_text_link = self.spider.songInfos["songTextLink"][n]
        if os.path.exists("./download/%s.mp3" % song_id) == 0:
            with open("./download/%s.mp3" % song_id, "wb") as f:
                response = requests.get(song_link, headers=header)
                dict = response.json()
                url = dict['url']
                music = requests.get(url, headers=headers2).content
                f.write(music)
            f.close()
        if os.path.exists("./download/%s.jpg" % album) == 0:
            with open("./download/%s.jpg" % album, "wb") as f:
                f.write(requests.get(map_link).content)
            f.close()

            im = PIL.Image.open("./download/%s.jpg")
            os.remove("./download/%s.jpg")
            out = im.resize((150, 150), PIL.Image.ANTIALIAS)  # resize image with high-quality
            out.save("./download/%s.jpg")
        if os.path.exists("./download/%s.lrc" % song_id) == 0 and song_text_link != "":
            with open("./download/%s.lrc" % song_id, "wb") as f:
                pass
                # f.write(requests.get(song_text_link,headers=header).content)
            f.close()
        self.add_to_queue(name, album,  "./download/%s.mp3" % song_id, int(eyed3.load("./download/%s.mp3" % song_id).info.time_secs))
        if self.songPlayIndex == -1 and self.songQueue["songName"] != []:
            self.songPlayIndex = 0
            self.tempSongLength = self.songQueue["songLength"][self.songPlayIndex]
        self.refresh_song_in_queue()
        self.refresh_progress()
        self.refresh_picture()

    def play(self):
        self.lastTime = 0.0
        self.presentTime = 0.0
        self.during = 1
        self.lrcIndex = -1
        self.songText = [[], []]
        self.refresh_song_in_queue()
        self.wmp.currentPlaylist.clear()
        self.btnStartAndPause.SetBitmap(self.pause)
        self.tempSongLength = self.songQueue["songLength"][self.songPlayIndex]
        self.stcTextTempSongLength.SetLabel(self.int_to_time(self.tempSongLength))
        media = self.wmp.newMedia(self.songQueue["filepath"][self.songPlayIndex])
        self.wmp.currentPlaylist.appendItem(media)
        self.beginTime = time.time()
        self.isPlaying = 1
        self.wmp.controls.play()
        self.refresh_picture()
        self.read_lrc()
        self.lrc_put()
        self.refresh_progress()

    def start_and_pause(self, event):
        if not self.isPlaying:
            if self.songPlayIndex == -1:
                return
            if self.during == 1:
                self.isPlaying = 1
                self.beginTime = time.time()
                self.wmp.controls.play()
                self.btnStartAndPause.SetBitmap(self.pause)
            else:
                self.play()
        else:
            self.isPlaying = 0
            self.wmp.controls.pause()
            self.lastTime = self.presentTime
            self.btnStartAndPause.SetBitmap(self.start)

    def random_play(self):
        random.seed()
        n = int(random.random() * len(self.songQueue["songName"]))
        if n <= 0:
            n = 1
        self.songPlayIndex = n
        self.play()

    def next_music(self, event):
        self.songPlayIndex = (self.songPlayIndex + 1) % len(self.songQueue["songName"])
        self.play()

    def previous_music(self, event):
        self.songPlayIndex = (self.songPlayIndex - 1) % len(self.songQueue["songName"])
        self.play()

    def change_voice(self, event):
        self.wmp.settings.Volume = self.sldVoice.GetValue()
        self.stcTextVoice.SetLabel(str(self.wmp.settings.Volume))

    def music_stop(self, event):
        self.wmp.controls.Stop()
        self.mapAlbum.SetBitmap(self.jpg)
        self.btnStartAndPause.SetBitmap(self.start)
        self.songQueue = {"filepath": [], "songName": [], "map_path": [], "songText": [], "songLength": []}
        self.songShowText[3].SetForegroundColour('Black')
        for i in range(0, 8):
            self.songShowText[i].SetLabel(self.songTextToShow[i])
        self.refresh_song_in_queue()
        self.songPlayIndex = -1
        self.during = 0
        self.presentTime = 0
        self.tempSongLength = 0
        self.isPlaying = 0
        self.refresh_progress()

    def next_page(self, event):
        self.spider.page += 1
        self.spider.get_infos(self.key)
        self.refresh_song_list()
        self.refresh_page_id()

    def previous_page(self, event):
        if self.spider.page == 0:
            return
        self.spider.page -= 1
        self.spider.get_infos(self.key)
        self.refresh_song_list()
        self.refresh_page_id()

    def int_to_time(self, n):
        n = int(n)
        m = str(n // 60)
        sec = str(n % 60)
        while len(m) < 2:
            m = "0" + m
        while len(sec) < 2:
            sec = "0" + sec
        res = m + ":" + sec
        return res

    # 添加歌曲进入队列
    def bt0_click(self, event):
        self.download(0)

    def bt1_click(self, event):
        self.download(1)

    def bt2_click(self, event):
        self.download(2)

    def bt3_click(self, event):
        self.download(3)

    def bt4_click(self, event):
        self.download(4)

    def bt5_click(self, event):
        self.download(5)

    def bt6_click(self, event):
        self.download(6)

    def bt7_click(self, event):
        self.download(7)

    def bt8_click(self, event):
        self.download(8)

    def bt9_click(self, event):
        self.download(9)

    def bt10_click(self, event):
        self.download(10)

    def bt11_click(self, event):
        self.download(11)

    def bt12_click(self, event):
        self.download(12)

    def bt13_click(self, event):
        self.download(13)

    def bt14_click(self, event):
        self.download(14)

    def bt15_click(self, event):
        self.download(15)

    def bt16_click(self, event):
        self.download(16)

    def bt17_click(self, event):
        self.download(17)

    def bt18_click(self, event):
        self.download(18)

    def bt19_click(self, event):
        self.download(19)


app = wx.App()
musicForm = MusicFrame()
musicForm.Show()
app.MainLoop()