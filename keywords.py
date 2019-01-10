#!/usr/bin/env python
# coding: utf-8

# In[7]:


import requests
import json
import pymongo
from bs4 import BeautifulSoup
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# - base를 글로벌 영역으로 빼줘야

# In[8]:


base = declarative_base()
class NaverKeyword(base):
    __tablename__ = "naver"

    id = Column(Integer, primary_key=True)
    rank = Column(Integer, nullable=False)
    keyword = Column(String(50), nullable=False)
    rdate = Column(TIMESTAMP, nullable=False)

    def __init__(self, rank, keyword):
        self.rank = rank
        self.keyword = keyword

    def __repr__(self):
        return "<NaverKeyword {}, {}>".format(self.rank, self.keyword)  


# - ip
# - base 필요
# - datas: 크롤링 후 obj 변수에 저장
# - self. 주의

# In[9]:


class NaverKeywords:
    
    def __init__(self, ip, base):
        self.mysql_client = create_engine("mysql://root:wnstmwkd00@{}/world?charset=utf8".format(ip))
        self.mongo_client = pymongo.MongoClient('mongodb://{}:27017'.format(ip))
        self.datas = None
        self.base = base
        
    def crawling(self):
        response = requests.get("https://www.naver.com/")
        dom = BeautifulSoup(response.content, "html.parser")
        keywords = dom.select(".ah_roll_area > .ah_l > .ah_item")
        datas = []
        for keyword in keywords:
            rank = keyword.select_one(".ah_r").text
            keyword = keyword.select_one(".ah_k").text
            datas.append((rank, keyword))
        self.datas = datas
    
    
    def mysql_save(self):
        
        # make table
        self.base.metadata.create_all(self.mysql_client)
        
        # parsing keywords
        keywords = [NaverKeyword(rank, keyword) for rank, keyword in self.datas]

        # make session
        maker = sessionmaker(bind=self.mysql_client)
        session = maker()

        # save datas
        session.add_all(keywords)
        session.commit()

        # close session
        session.close()
        
    def mongo_save(self):
        
        # parsing querys
        keyowrds = [{"rank":rank, "keyword":keyword} for rank, keyword in self.datas]
        
        # insert keyowrds
        self.mongo_client.crawling.naver_keywords.insert(keyowrds)
        
    def send_slack(self, msg, channel="#james_new", username="provision_bot" ):
        webhook_URL = "https://hooks.slack.com/services/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"
        payload = {
            "channel": channel,
            "username": username,
            "icon_emoji": ":provision:",
            "text": msg,
        }
        response = requests.post(
            webhook_URL,
            data = json.dumps(payload),
        )
    
    def run(self):
        self.crawling()
        self.mysql_save()
        self.mongo_save()
        self.send_slack("naver crawling done!")
        print("ok")


# In[10]:


nk = NaverKeywords("54.180.104.62", base)
nk.run()
