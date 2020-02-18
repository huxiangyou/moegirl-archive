# -*- coding: utf-8 -*-
"""Python 3.8.0
对列出的页面进行存档

Jan 7, 2020
Jan 15, 2020
Jan 21, 2020
Feb 18, 2020
Hu Xiangyou
"""

import requests
import time
import os
import socket

print(__doc__)

listPath="PAGELIST.txt"
fold="archive/"
fileData="!.txt"

file_encoding='UTF-8'

url="https://zh.moegirl.org/api.php"

params1={'action':'query','format':'json','prop':'info','curtimestamp':1,'indexpageids':1}
params={'action':'query','format':'json','prop':'revisions','curtimestamp':1,'indexpageids':1,'rvprop':'content|ids'}

f=open(listPath,'r',encoding=file_encoding)
pagelistfile=f.read().splitlines()
f.close()
pageidlist=[]
for pageline in pagelistfile:
	if pageline.split("\t")[0] in ('[M___]','[T___]','[C___]'):
		pageidlist.append(int(pageline.split("\t")[1]))

n_all=0
n_new=0
n_overridden=0
n_moved=0
n_error=0

f=open(fold+fileData,'r',encoding=file_encoding)
reviddict=eval(f.read())
f.close()

def devide(l:list,n:int)->list:
	for i in range(0,len(l),n):
		yield l[i:i+n]

def second2days(seconds:float=0.00)->str:
	"""将秒数转换为时间表述"""
	m,s=divmod(seconds,60)
	h,m=divmod(m,60)
	d,h=divmod(h,24)
	y,d=divmod(d,365)

	y=str(int(y))+" 年" if y else ""
	d=str(int(d))+" 天" if d else ""
	h=str(int(h))+" 小时" if h else ""
	m=str(int(m))+" 分钟" if m else ""
	s=str(round(s,2))+" 秒" if s else ""

	return " ".join(i for i in (y,d,h,m,s) if i)

def isResponceOK(json:dict)->bool:
	if 'batchcomplete' in json:
		return True
	else:
		print("响应不完整。可能因为请求的数据量过大。请调整请求的数据量。")
		return False

def saveData():
	f=open(fold+fileData,'w',encoding=file_encoding)
	f.write(str(reviddict))
	f.close()

input("按Enter开始。")
start_time=time.time()
print("开始于",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(start_time)))

for pageidlist_d in devide(pageidlist,50):
	l_param:str="|".join(str(i) for i in pageidlist_d)
	while True:
		try:
			a=requests.get(url,params={**params1,**{'pageids':l_param}},timeout=(10,30))
		except:
			print("[出错]\t网络问题，正在重试")
			n_error+=1
			continue
		else:
			if a.ok:
				json:dict=a.json()
				if isResponceOK(json):
					break
	for pageid in pageidlist_d:
		if pageid not in reviddict or \
		reviddict[pageid][0]!=json['query']['pages'][str(pageid)]['lastrevid'] or \
		reviddict[pageid][1]!=json['query']['pages'][str(pageid)]['title']:
			while True:
				try:
					b=requests.get(url,params={**params,**{'pageids':pageid}},timeout=(10,30))
				except:
					print("[出错]\t网络问题，正在重试")
					n_error+=1
					continue
				else:
					if b.ok:
						json:dict=b.json()
						if isResponceOK(json):
							break
			pageJson=json['query']['pages'][str(pageid)]
			if 'revisions' in pageJson:
				content=pageJson['revisions'][0]['*']
				title=pageJson['title']
				revid=pageJson['revisions'][0]['revid']
				title_in_file=title.replace("/","／").replace(":","：").replace("\\","＼").replace("*","＊").replace("?","？").replace("\"","＂").replace("<","＜").replace(">","＞").replace("|","｜")
				if os.path.isfile(fold+title_in_file+".txt"):
					if pageid in reviddict and reviddict[pageid][0]==revid and reviddict[pageid][1]==title:
						#print("[－]","\t[P]",pageid,"\t[R]",revid,"\t[标题]",title)
						pass
					else:
						f=open(fold+title_in_file+".txt",'w',encoding=file_encoding)
						f.write(content)
						f.close()
						print("[覆]","\t[P]",pageid,"\t[R]",revid,"\t[标题]",title)
						n_overridden+=1
				else:
					f=open(fold+title_in_file+".txt",'w',encoding=file_encoding)
					f.write(content)
					f.close()
					print("[新]","\t[P]",pageid,"\t[R]",revid,"\t[标题]",title)
					n_new+=1
				if pageid in reviddict and title!=reviddict[pageid][1]:
					print("[移]","\t",reviddict[pageid][1],"->",title,"\t[注意] 请手动删除之前的存档。")
					n_moved+=1
				reviddict[pageid]=(revid,title)
		n_all+=1
reviddict['info']="萌娘百科页面存档"
reviddict['time']=json['curtimestamp']
reviddict['by']=socket.getfqdn(socket.gethostname())

saveData()

print()
end_time=time.time()
print("结束于",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(end_time)))
print("耗时",second2days(end_time-start_time))

print(n_all,"个已检查。")
print(n_new,"个新存档。",n_overridden,"个被覆盖。",n_moved,"个被移动。")
print("期间共出错",n_error,"次。")

input("完成。")
