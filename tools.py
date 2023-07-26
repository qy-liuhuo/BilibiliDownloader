import hashlib
import json
import pickle
import re
import shutil
import time
import urllib
from functools import reduce
import requests
from bs4 import BeautifulSoup
from moviepy.editor import *
import socket
import urllib3


def allowed_gai_family():
    return socket.AF_INET


urllib3.util.connection.allowed_gai_family = allowed_gai_family
SESSDATA = 'xxx'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',
    'Cookie': 'SESSDATA=' + SESSDATA,
}


def getjson(url, headers=None):
    response = requests.get(url, headers=headers,timeout=3)
    if response.status_code == 200:
        json_data = response.json()
        print(json_data)
        return json_data
    else:
        return None


def getMixinKey(ae):
    oe = [46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12,
          38, 41,
          13, 37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36,
          20, 34, 44, 52]
    le = reduce(lambda s, i: s + ae[i], oe, "")
    return le[:32]


def encWbi(params_in: dict):
    params = params_in.copy()  # 加上防止改变传入字典的原值?
    resp = getjson("https://api.bilibili.com/x/web-interface/nav")
    wbi_img: dict = resp["data"]["wbi_img"]
    me = getMixinKey(wbi_img['img_url'].split("/")[-1].split(".")[0] + wbi_img['sub_url'].split("/")[-1].split(".")[0])
    wts = int(time.time())
    # wts = 1684940606
    params["wts"] = wts
    params = dict(sorted(params.items()))
    Ae = "&".join([f'{key}={value}' for key, value in params.items()])
    w_rid = hashlib.md5((Ae + me).encode(encoding='utf-8')).hexdigest()
    return w_rid, wts


# 输入uid 返回投稿视频的字典列表
def getUpVideos(up_uid, startpage=1, endpage=100, tid=0, keyword=''):
    up_videos = []
    for space_video_page in range(startpage, endpage + 1):
        time.sleep(3)  # 频率不宜过快
        space_video_search_params_dict = {'mid': up_uid,  # UP主UID
                                          'ps': 30,  # 每页的视频个数
                                          'tid': tid,  # 分区筛选号 0为不筛选
                                          'special_type': '',
                                          'pn': space_video_page,  # 页码
                                          'keyword': keyword,  # 搜索关键词
                                          'order': 'pubdate',  # 降序排序 click(播放)/stow(收藏)
                                          'platform': 'web',
                                          'web_location': 1550101,
                                          'order_avoided': 'true'
                                          }
        w_rid, wts = encWbi(space_video_search_params_dict)

        space_video_search_params_urlcoded = urllib.parse.urlencode(space_video_search_params_dict)
        up_videos_api = 'https://api.bilibili.com/x/space/wbi/arc/search?%s&w_rid=%s&wts=%s' % (
        space_video_search_params_urlcoded, w_rid, wts)
        space_video_search_json = getjson(up_videos_api, headers=headers)
        if space_video_page == startpage:
            # 获取分类表 如果该页无视频则返回None
            # tlist = space_video_search_json['data']['list']['tlist']
            # for each in tlist :
            #     print('tid:',tlist[each]['tid'],'类名:',tlist[each]['name'],'数目:',tlist[each]['count'])

            # 获取视频总数 如果该页无视频则返回0
            space_video_num = space_video_search_json['data']['page']['count']

        if space_video_search_json['data']['list']['vlist']:  # 如果不存在视频则为空列表[]
            thisPageVideos = space_video_search_json['data']['list']['vlist']
            thisPageVideos.reverse()
            thisPageVideos_num = len(thisPageVideos)
            for each_video_id in range(thisPageVideos_num):
                each_video_info = thisPageVideos[thisPageVideos_num - each_video_id - 1]
                # up_videos格式
                up_videos.append({'title': each_video_info['title'],
                                  'bvid': each_video_info['bvid'],
                                  'author': each_video_info['author'],
                                  'mid': each_video_info['mid'],
                                  'created': each_video_info['created'],
                                  })

            if space_video_page == endpage:
                print('[√] 已获取 [%d/%d] 个视频' % (len(up_videos), space_video_num))
                return up_videos
        else:  # 这页不存在视频
            print('[√] 已获取 [%d/%d] 个视频' % (len(up_videos), space_video_num))
            return up_videos




def getVideoInfo(videoInfo):
    context = requests.get('https://www.bilibili.com/video/'+videoInfo['bvid'], timeout=1).text
    playInfo = json.loads(re.findall(r'<script>window.__playinfo__=(.*?)</script>', context)[0])

    audioUrl = playInfo['data']['dash']['audio'][0]['baseUrl']
    videoUrl = playInfo['data']['dash']['video'][0]['baseUrl']
    print(videoUrl)
    title = videoInfo['title']
    return audioUrl,videoUrl,title

def getVideoInfoByUrl(url):
    context = requests.get(url, timeout=1).text
    playInfo = json.loads(re.findall(r'<script>window.__playinfo__=(.*?)</script>', context)[0])
    soup = BeautifulSoup(context)
    title=soup.find(attrs={'class':'video-title'}).text
    audioUrl = playInfo['data']['dash']['audio'][0]['baseUrl']
    videoUrl = playInfo['data']['dash']['video'][0]['baseUrl']
    return audioUrl,videoUrl,title

def download(audioUrl,videoUrl,path,title):
    headers2 = {
        'Origin': 'https://www.bilibili.com/',
        'Referer': 'https://www.bilibili.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82'
    }
    path=path+"/"+title
    try:
        data1=requests.get(audioUrl,headers=headers2).content
        data2=requests.get(videoUrl,headers=headers2).content
        if not os.path.exists(path):
            os.mkdir(path)
        with open(path+"/"+title+".mp3", mode='wb') as f:  # 保存数据
            f.write(data1)
        with open(path+"/"+title+".mp4", mode='wb') as f:  # 保存数据
            f.write(data2)
        video = VideoFileClip(path+"/"+title+".mp4")
        audio = AudioFileClip(path+"/"+title+".mp3")
        newVideo = video.set_audio(audio)
        newVideo.write_videofile(title+".mp4")
        shutil.move(title+".mp4", path+"/"+title+".mp4")
    except Exception as e:
        print(e)
        print(title+"下载失败")
        return
    print("视频"+title+"下载完成")





if __name__ == '__main__':
    # audioUrl, videoUrl, title=getVideoInfo("https://www.bilibili.com/video/BV1vV411K7VE")
    # download(audioUrl,videoUrl,"./download",title)
    uid="1836322665"
    # data=getUpVideos(uid)
    # file = open(uid+'.pickle', 'wb')
    # pickle.dump(data, file)
    # file.close()
    with open(uid+'.pickle', 'rb') as file:
        videoList = pickle.load(file)
    print(videoList)
    # for item in videoList:
    #     print(item)
    #     audioUrl, videoUrl, title = getVideoInfo(item)
    #     download(audioUrl,videoUrl,"./download",title)
    print(getVideoInfoByUrl("https://www.bilibili.com/video/BV1vV411K7VE"))
