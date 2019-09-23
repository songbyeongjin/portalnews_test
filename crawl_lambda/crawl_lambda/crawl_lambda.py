from bs4 import BeautifulSoup
import requests
import os
import psycopg2
import datetime

#NEWS CLASS
class News:
    def __init__(
        self,
        id,
        title,
        content,
        press,
        writer,
        date,
        url,
        portal,
        created_at,
        updated_at):

        #initilaze
        self.id = id
        self.title = title
        self.content = content
        self.press = press
        self.writer = writer
        self.date = date
        self.url = url
        self.portal = portal
        self.created_at = created_at
        self.updated_at = updated_at
        
#定数定義
NOT_END_STR = "[MORE...]"

CONTENT_MAX_LEN = 200
NEWS_LEN = 5
DATE_BOUNDARY_STR = "2019"#<!年が経つと要変更

#dateパラメーターが現在日・時間より遅く設定されると現在日・時間に繋がるため、2099年99月99日に設定する
NATE_URL = "https://news.nate.com/rank/interest?sc=all&p=day&date=20999999"
DAUM_URL = "https://media.daum.net/ranking/popular/"
#naver HTML DOM構想の問題で、全年齢のRANKING NEWSが表示されないため、30代のデータを収集
NAVER_URL = "https://news.naver.com/main/ranking/popularDay.nhn?rankingType=age&subType=30"


def handler(event, context):
    response = requests.get(NATE_URL)
    parsedHtml = response.text
    soup = BeautifulSoup(parsedHtml, 'html.parser')
    
    ###################################################NATE#############################################
    nate_crawl_url = []         #<!記事URL
    nate_url_prefix = "https:"
    nate_news = []

    #nate url取得
    nate_crawl_url = get_nate_url(NATE_URL)

    for index in range(0,NEWS_LEN):
        #create temp nate news instance

        crawled_nate_url = nate_url_prefix + nate_crawl_url[index]
        print(crawled_nate_url)

        response = requests.get(crawled_nate_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        insert_url       = crawled_nate_url
        #news.title     = get_nate_title(doc)
        #news.content   = get_nate_content(doc)
        #news.press     = get_nate_cor(doc)
        #news.date      = get_nate_date(doc)
        insert_create_time = datetime.datetime.now()
        print(insert_create_time)
        insert_updated_time = datetime.datetime.now()

        #create nate news
        #cur.execute(sql, (value1,value2))
        #get record's id
        #id = cur.fetchone()[0]
        #database commit
        #conn.commit()
        #nate_news.push(news)


def get_nate_url(nate_url):
    nate_crawl_url = []

    response = requests.get(nate_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    urls = soup.select(".mlt01 a")
    for url in urls:
        nate_crawl_url.append(url.get('href'))
    return nate_crawl_url

'''
def get_nate_title(doc)
    temp_title = ""
    doc.css('.articleSubecjt').each do |element|
        temp_title = element.text[0..-1]#<!2行にならないように文字制限
    end
    return temp_title
end

def get_nate_content(doc)
    temp_contents = []
    doc.css('#realArtcContents').each do |element|
        temp_content = element.text.squish#0..CONTENT_MAX_LEN]#<!"¥n"を削除し、文字数を制限する
        temp_contents.push(temp_content)
    end
    #リストを文字列に型変換
    trimminged_content = temp_contents.join
    trimminged_content = trimminged_content[0..CONTENT_MAX_LEN] + NOT_END_STR
    return trimminged_content
end

def get_nate_date(doc)
    temp_date = ""
    doc.css('.firstDate em').each do |element|
        temp_date = element.text
    end
    cor_date_boundary = temp_date.index(DATE_BOUNDARY_STR)
    date = DateTime.parse(temp_date[cor_date_boundary..9])
    return date
end

def get_nate_cor(doc)
    temp_cor = ""
    doc.css('.articleInfo .medium').each do |element|
        temp_cor = element.text
    end
    return temp_cor
end
'''