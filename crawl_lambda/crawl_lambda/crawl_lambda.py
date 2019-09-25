from bs4 import BeautifulSoup
import requests
import os
import psycopg2
import datetime
import time
import re

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
CURRENT_YEAR = "2019"#<!年が経つと要変更
NATE ="nate"

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

        response = requests.get(crawled_nate_url)
        
        #html content取得
        soup = BeautifulSoup(response.text, 'html.parser')

        
        #DB挿入用レコード作成
        insert_title   = get_nate_title(soup)
        insert_content = get_nate_content(soup)
        insert_press   = get_nate_press(soup)
        insert_wrtier  = "writer"
        insert_url     = crawled_nate_url#!<urlは予め取得しておいた値を使用する
        insert_portal  = NATE
        insert_date    = get_nate_date(soup)
        now_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        insert_create_time = now_date
        insert_updated_time = now_date

        #INSERT query作成
        #reprメソッドを使うと自動的に「''」に囲まれるので「''」省略する
        sql = f"INSERT INTO news (id, title, content, press, writer, date, url, portal, created_at, updated_at)\n"
        sql = sql + f"VALUES(default, {repr(insert_title)} ,'{insert_content}', '{insert_press}', '{insert_wrtier}', '{insert_date}'::timestamptz,"
        sql = sql + f"{repr(insert_url)}, '{insert_portal}', '{insert_create_time}'::timestamptz, '{insert_updated_time}'::timestamptz);"

        #create nate news
        db_conn = psycopg2.connect(
            host     = os.environ['host'],
            dbname   = os.environ['database'],
            user     = os.environ['username'],
            password = os.environ['password'],
            port     = os.environ['port'])
        
        cursor = db_conn.cursor()
        cursor.execute(sql,())
        db_conn.commit()
        cursor.close()
        db_conn.close()


def get_nate_url(nate_url):
    nate_crawl_url = []

    response = requests.get(nate_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    urls = soup.select(".mlt01 a")
    for url in urls:
        nate_crawl_url.append(url.get('href'))
        
    return nate_crawl_url


def get_nate_title(soup):
    nate_crawl_title = ""
    
    title = soup.select(".articleSubecjt")
    #replaceの３番目の値はtitleの最大文字数に指定する(変換文字の数を定める)
    #「'」文字がDBに保存する際に、フィールドの識別子になるため、文字変換を行う
    nate_crawl_title = title[0].text.replace("\'", "`", 100)
    
    return nate_crawl_title


def get_nate_content(soup):
    nate_crawl_content = ""

    contents = soup.select("#realArtcContents")

    content = contents[0].text

    #文字制限及び続き文字挿入
    nate_crawl_content = content[:CONTENT_MAX_LEN] + NOT_END_STR
    #全ての空白・改行文字削除
    nate_crawl_content = nate_crawl_content.split()
    nate_crawl_content = " ".join(nate_crawl_content)
    #「'」文字がDBに保存する際に、フィールドの識別子になるため、文字変換を行う
    nate_crawl_content = nate_crawl_content.replace("\'", "`", 100)
    
    return nate_crawl_content


def get_nate_press(soup):
    nate_crawl_press = ""

    press = soup.select('.articleInfo .medium')
    nate_crawl_press = press[0].text

    return nate_crawl_press


def get_nate_date(soup):
    date = soup.select('.firstDate em')
    temp_date = date[0].text

    temp_date = temp_date[:9]
    nate_crawl_date = datetime.datetime.strptime(temp_date, "%y-%m-%d")

    return nate_crawl_date