# -*- coding: utf-8 -*-
import urllib    
import urllib2  
import math
import time 
import json
from bs4 import BeautifulSoup

BASE_URL = "http://www.p2pblack.com"
HOME_PAGE_URL = BASE_URL+"/merc/search.html"
#default records per page is 20
RECORD_PER_PAGE = 20
SLEEP_TIME = 1


name_map = {
    u'手机号':'phone',
    u'职业':'occupation',
    u'户籍':'huji',
    u'学校或单位':'school_company',
    u'QQ号码': 'QQ',
    u'邮箱':'email',
    u'现居地':'current_address',
    u'职位':'position',
    u'手机':'phone',
    u'学校/公司':'school_company'
    
}

def crawler_exe(_username,main_output,detail_output):
	detailLinks = []
	retMainPageInfo = []
	retDetailPageInfo = []
	mainPageOutput = main_output
	detailPageOutput = detail_output
	username = _username
	print "username: ",username
	#crawl the first page, get total record 
	total_num_records = getRecordNum(username, HOME_PAGE_URL)
	print "total number of record: ",total_num_records
 
	total_num_pages = int(math.ceil(float(total_num_records)/float(RECORD_PER_PAGE)))
	print "total number of pages: ",total_num_pages
	
	#crawl the main page page by page 
	ret = []
	for i in range(1,total_num_pages+1):
	    page_label = i
	    #mainPageOutput.write("crawling page "+str(page_label))
	    url = 'http://www.p2pblack.com/merc/search.html?currentPage='+str(page_label)+'&showCount=20'
	    print "crawling main page "+url
	    ret = mainPageProcess(username, url)
	    retMainPageInfo.extend(ret[0])
	    detailLinks.extend(ret[1])
    
	json.dump(retMainPageInfo,mainPageOutput,indent=2)

	#crawl the detail links
	#history per name 
	history = []
	for l in detailLinks:
	    d_url = "http://www.p2pblack.com"+l
	    if d_url not in history:
	        print "crawling detail page: ",d_url
	        history.append(d_url)
	        retDetailPageInfo.extend(detailPageProcess(d_url,l))
	    else:
	        print "ignore repeated url: ", d_url
	    
	json.dump(retDetailPageInfo,detailPageOutput,indent=2)    

 

def getRecordNum(name,url):
    values = {"kw":name}
    data = urllib.urlencode(values) 
    request = urllib2.Request(url,data)
    response = urllib2.urlopen(request)
    soup = BeautifulSoup(response,"lxml")
    total_num_records = soup.find(class_='pagination').li.font.get_text()
    return total_num_records 


# "http://www.p2pblack.com/merc/search.html?currentPage=5&showCount=20"
def mainPageProcess(name,url):
    detail_links = []
    ret_list = []
    values = {"kw":name}
    data = urllib.urlencode(values) 
    request = urllib2.Request(url,data)
    response = urllib2.urlopen(request)
    soup = BeautifulSoup(response,"lxml")
    #print (soup.prettify())
    blacklist = soup.find_all(class_='sousuo_jg_list')

    for black_item in blacklist:
        ret = {}
        m = black_item.find_all('p')
        if len(m) == 8:
            link = (black_item.a['href'].split(";"))[0]
            detail_links.append(link)

            ret['name'] = m[0].get_text()
            ret['idcard'] = m[1].strong.get_text()
            ret['loan_amount'] = m[2].strong.get_text()
            ret['platform'] = m[3].strong.get_text()
            ret['overdue_amount'] = m[4].strong.get_text()
            ret['status'] = m[5].strong.get_text()
            ret['remark'] = m[6].strong.get_text()
            ret['detail_link'] = link

            info = (m[7].get_text().replace(" ","").split("\r\n"))
            info = (x for x in info if len(x)>0)
            for item in info:
                kv = item.split(u'：')
                ret[name_map[kv[0]]] = kv[1]
            #print "ret is ",ret
            ret_list.append(ret)

    return (ret_list,detail_links)

def detailPageProcess(url,link):
    #history per name 
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    soup = BeautifulSoup(response,"lxml")
    ret_list = []
    #print (soup.prettify())
    platforms = soup.find_all(class_='ss_jgxq_pingtai')
    for pf in platforms:
        ret = {}
        ret['link'] = link
        basic = pf.find(class_="pingtai_jiben_xinxi").get_text().replace(" ","").split("\r\n")
        for item in basic:
            if len(item)>0:
                kv = item.split(u'：')
                ret[name_map[kv[0].replace("\n","")]] = kv[1].replace("\n","")
        records = pf.find_all(class_="ss_xinxi_listtitle")
        #remove the label row
        records = records[1:]
        for r in records:
            fields = r.find_all('p')
            ret['label'] = fields[0].get_text()
            ret['platform'] = fields[1].get_text()
            ret['name'] = fields[2].get_text()
            ret['loan_amount'] = fields[3].get_text()
            ret['total_loan_num'] = fields[4].get_text()
            ret['loan_start_time'] = fields[5].get_text()
            ret['overdue_amount'] = fields[6].get_text()
            ret['status'] = fields[7].get_text()
            ret['upload_time'] = fields[8].get_text()
            ret['remark'] = fields[9].get_text()
            ret_list.append(ret)
            
    return ret_list