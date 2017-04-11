# -*- coding: utf-8 -*-
# @Date    : 2017/2/20  21:55
# @Author  : 490949611@qq.com
import requests
from bs4 import BeautifulSoup

indexUrl = "http://my.seu.edu.cn/index.portal"
# response = requests.get(indexUrl)
# print response.headers

url = 'http://newids.seu.edu.cn/authserver/login?goto=http://my.seu.edu.cn/index.portal'
response = requests.get(url)
soup =BeautifulSoup(response.content,'lxml')

user = "213141714"
password = "qh129512!"

cookie = response.headers['Set-Cookie']
cookie = cookie.split(",")[0] + ";" + cookie.split(",")[1].split(";")[0]

elements = soup.find_all("input",attrs={'type':'hidden'})
lt = elements[0]['value']
dllt = elements[1]['value']
execution = elements[2]['value']
event_id = elements[3]['value']
rmShown = elements[4]['value']

data= {
	'username':user,
	'password':password,
	'lt':lt,
	'dllt':dllt,
	'execution':execution,
	'_eventId':event_id,
	'rmShown':rmShown
}

headers = {
	'Referer':'http://newids.seu.edu.cn/authserver/login?goto=http://my.seu.edu.cn/index.portal',
  	'Cookie':cookie
}

response = requests.post(url,data = data, headers = headers, allow_redirects=False)
keyCookie = response.headers['Set-Cookie'].split(";")[2].split(",")[1]


headers = {
  'Cookie': keyCookie.strip()
}

newUrl = response.headers['Location']
response = requests.get(newUrl, headers = headers, allow_redirects=False)
jsessionid_cookie = response.headers['Set-Cookie'].split(";")[0]
login_cookie = keyCookie + ";" + jsessionid_cookie


headers = {
  'Cookie': login_cookie.strip()
}

print headers
main_get_url = 'http://my.seu.edu.cn/index.portal?.pn=p1064_p1551'
soup = BeautifulSoup(requests.get(main_get_url,headers=headers).content,'lxml')
list_url = 'Znxjb20ud2lzY29tLnBvcnRhbC5zaXRlLnYyLmltcGwuRnJhZ21lbnRXaW5kb3d8ZjM0MDl8dmlld3xtYXhpbWl6ZWR8YWN0aW9uPWxpc3Q_'
param = {'.p':list_url}
# getJiangInfo(requests.get(indexUrl,headers=headers,params=param).content)
list = []
content = requests.get(indexUrl,headers=headers,params=param).content
# print jxjTitle

def getJiangInfo(content):
	jiangList = []
	jiangInfo = {
		'title': '',
		'time': '',
		'level': '',
		'year': '',
		'money': ''
	}
	soup = BeautifulSoup(content, 'lxml')
	items = soup.find_all('div', attrs={'class': 'isp-service-item-info'})
	for item in items[1:]:
		jiangInfo['title'] = item.find('div', attrs={'class': 'jxjTitle'}).text
		jiangInfo['time'] = item.find_all('div', attrs={'class': 'jxjInfo'})[0].text[3:].strip()
		jiangInfo['level'] = item.find_all('div', attrs={'class': 'jxjInfo'})[1].text[6:].strip()
		jiangInfo['year'] = item.find_all('div', attrs={'class': 'jxjInfo'})[2].text[5:].strip()
		jiangInfo['money'] = item.find_all('div', attrs={'class': 'jxjInfo'})[3].text[3:].strip()
		jiangList.append(jiangInfo)
	return jiangList

list = []
list = getJiangInfo(content)
print list