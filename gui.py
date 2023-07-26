import pickle
import threading
import tkinter as tk
from concurrent.futures import thread

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from myEntry import MyEntry
from tools import *

def allowed_gai_family():
    return socket.AF_INET
urllib3.util.connection.allowed_gai_family = allowed_gai_family


videoList=[]


def selectAll(searchBox):
    searchBox.select_set(0,tk.END)

def clearAll(searchBox):
    searchBox.select_clear(0, tk.END)

def search(searchInfo):
    global videoList
    if "http" not in searchInfo:
        videoList=getUpVideos(searchInfo)
        for item in videoList:
            searchBox.select_clear(0, tk.END)
            searchBox.insert(tk.END, item['title']+'-'+item['bvid'])
    else:
        bvid=re.search(r'(BV.*?).{10}', searchInfo).group(0)
        info=getVideoInfoByUrl(searchInfo)
        videoList=[{'title':info[2],'bvid':bvid}]
        searchBox.insert(tk.END, info[2]+'-'+bvid)

def dl():
    selecteds=searchBox.curselection()
    for index in selecteds:
        print(index)
        print(videoList)
        audioUrl, videoUrl, title = getVideoInfo(videoList[index])
        label.config(text="正在下载：" + title)
        print("正在下载：" + title)
        download(audioUrl,videoUrl,"./download",title)
        print(title+"下载完成")
        label.config(text=title+"下载完成")

# 创建线程执行程序
def thread_it(func, *args):		# 传入函数名和参数
    # 创建线程
    t = threading.Thread(target=func, args=args)
    # 守护线程
    t.setDaemon(True)
    # 启动
    t.start()


root = ttk.Window(title="Bilibili视频下载器",themename="minty",size=(800,600),alpha=0.9,iconphoto="./static/download.png")
root.place_window_center()
searchInput=MyEntry(root, "输入视频链接或uid")

searchInput.place(x=170,y=50, width=400, height=30)
searchBtn=ttk.Button(text="搜索",command=lambda:thread_it(search,searchInput.get()))
searchBtn.place(x=570,y=50, width=60, height=30)


searchBox=tk.Listbox(root, selectmode=tk.MULTIPLE)
searchBox.place(x=20,y=100,width=760,height=450)



selectAllBtn=ttk.Button(root,text="全选",bootstyle="link",command=lambda:selectAll(searchBox))
selectAllBtn.place(x=20,y=560)
clearAllBtn=ttk.Button(root,text="清除",bootstyle="danger-link",command=lambda:clearAll(searchBox))
clearAllBtn.place(x=80,y=560)
downloadBtn=ttk.Button(root,text="下载",bootstyle="success",command=lambda:thread_it(dl))
downloadBtn.place(x=700,y=560)
label=ttk.Label()
label.place(x=150,y=565)
root.mainloop()