"""
Python 3.8.0
对列出的页面进行存档

Jan 7, 2020
Jan 15, 2020
Jan 21, 2020
Hu Xiangyou
"""

import requests
import time
import os
import socket

filepath="PAGELIST.txt"
fold="archive/"
fileData="!.txt"

url="https://zh.moegirl.org/api.php"

params1={'action':'query','format':'json','prop':'info','curtimestamp':1,'indexpageids':1}
params={'action':'query','format':'json','prop':'revisions','curtimestamp':1,'indexpageids':1,'rvprop':'content|ids'}

f=open(filepath,'r',encoding='UTF-8')
pagelistfile=f.read().splitlines()
f.close()
pageidlist=[]
for pageline in pagelistfile:
	if pageline.split("\t")[0] in ('[M___]','[T___]','[C___]'):
		pageidlist.append(int(pageline.split("\t")[1]))

n_all=0
n_new=0
n_overridden=0

f=open(fold+fileData,'r',encoding='UTF-8')
reviddict=eval(f.read())
f.close()

def devide(l:list,n:int)->list:
	for i in range(0,len(l),n):
		yield l[i:i+n]

def isResponceOK(json:dict)->bool:
	if 'batchcomplete' in json:
		return True
	else:
		print("响应不完整。可能因为请求的数据量过大。请调整请求的数据量。")
		return False

def pageEdited(json:dict,pageid:int)->bool:
	lastrevid=json['query']['pages'][str(pageid)]['lastrevid']
	title=json['query']['pages'][str(pageid)]['title']
	if reviddict[pageid][0]!=lastrevid or reviddict[pageid][1]!=title:
		return True
	else:
		return False

def saveData():
	f=open(fold+fileData,'w',encoding='UTF-8')
	f.write(str(reviddict))
	f.close()

def saveContent(pageid:int):
	global n_new,n_overridden
	while True:
		try:
			a=requests.get(url,params={**params,**{'pageids':pageid}},timeout=(10,30))
		except:
			print(".",end="")
			continue
		else:
			break
	json:dict=a.json()
	if not isResponceOK(json):
		raise
	if 'revisions' in json['query']['pages'][str(pageid)]:
		content=json['query']['pages'][str(pageid)]['revisions'][0]['*']
		title=json['query']['pages'][str(pageid)]['title']
		revid=json['query']['pages'][str(pageid)]['revisions'][0]['revid']
		title_in_file=title.replace("/","／").replace(":","：").replace("\\","＼").replace("*","＊").replace("?","？").replace("\"","＂").replace("<","＜").replace(">","＞").replace("|","｜")
		if pageid in reviddict and title!=reviddict[pageid][1]:
			print("[提示][移]","\t[Moved]",reviddict[pageid][1],"->",title,"\t[Note] 请手动删除之前的存档。")
		if os.path.isfile(fold+title_in_file+".txt"):
			if pageid in reviddict and reviddict[pageid][0]==revid and reviddict[pageid][1]==title:
				#print("-\t","\t[PID]",pageid,"\t[RID]",revid,"\t[Title]",title)
				pass
			else:
				f=open(fold+title_in_file+".txt",'w',encoding='UTF-8')
				f.write(content)
				f.close()
				reviddict[pageid]=[revid,title]
				print("[存][覆盖]","\t[PID]",pageid,"\t[RID]",revid,"\t[Title]",title)
				n_overridden+=1
		else:
			f=open(fold+title_in_file+".txt",'w',encoding='UTF-8')
			f.write(content)
			f.close()
			reviddict[pageid]=[revid,title]
			print("[存][新]","\t[PID]",pageid,"\t[RID]",revid,"\t[Title]",title)
			n_new+=1

input("按Enter开始。")
start_time=time.time()
print("开始于",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(start_time)))

for pageidlist_d in devide(pageidlist,50):
	l_param:str="|".join(str(i) for i in pageidlist_d)
	while True:
		try:
			a=requests.get(url,params={**params1,**{'pageids':l_param}},timeout=(10,30))
		except:
			print(".",end="")
			continue
		else:
			break
	json:dict=a.json()
	for pageid in pageidlist_d:
		if pageid in reviddict:
			if pageEdited(json,pageid):
				saveContent(pageid)
		else:
			saveContent(pageid)
		n_all+=1
reviddict['info']="萌娘百科LoveLive!系列页面存档"
reviddict['time']=json['curtimestamp']
reviddict['by']=socket.getfqdn(socket.gethostname())

saveData()

print()
end_time=time.time()
print("结束于",time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(end_time)))
print("耗时",end_time-start_time,"秒")

print("已检查",n_all,"个已检查。")
print(n_new,"个新存档。",n_overridden,"个被覆盖。")

input("完成。")