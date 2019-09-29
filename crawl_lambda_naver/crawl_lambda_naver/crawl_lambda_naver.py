from bs4 import BeautifulSoup
import requests
import os
import psycopg2
import datetime
        

#定数定義
NOT_END_STR = "[MORE...]"

CONTENT_MAX_LEN = 200
NEWS_LEN = 5
CURRENT_YEAR = "2019"#<!年が経つと要変更
NAVER ="naver"
#dateパラメーターが現在日・時間より遅く設定されると現在日・時間に繋がるため、2099年99月99日に設定する
NAVER_URL = "https://news.naver.com/main/ranking/popularDay.nhn?rankingType=age&subType=30"

def handler(event, context):
    response = requests.get(NAVER_URL)
    parsedHtml = response.text
    soup = BeautifulSoup(parsedHtml, 'html.parser')
    
    ###################################################NAVER#############################################
    naver_crawl_url = []         #<!記事URL
    naver_news = []

    #DB接続
    db_conn = psycopg2.connect(
        host     = os.environ['host'],
        dbname   = os.environ['database'],
        user     = os.environ['username'],
        password = os.environ['password'],
        port     = os.environ['port'])

    cursor = db_conn.cursor()

    #DELETE query作成
    sql_delete = f"delete from news where portal = '{NAVER}'"
    #新しいNEWSを挿入する前に全てのNAVER NEWSを削除する
    cursor.execute(sql_delete,())
    db_conn.commit()

    #現在IDの最大値を取得するquery作成
    sql_get_id = "select max(id) from news"
    #NEWS挿入時に使用するレコードのKEYであるID取得
    cursor.execute(sql_get_id,())
    #現在DB上の最大ID、DBにレコードが０件の場合はNoneが入る
    max_id = cursor.fetchall()[0][0]
    #レコードが0件の場合
    if max_id is None:
        max_id = 0
    new_id = max_id + 1

    #naver url取得
    naver_crawl_url = get_naver_url(NAVER_URL)

    for index in range(0, NEWS_LEN):
        #create temp naver news instance
        crawled_naver_url = naver_crawl_url[index]
        response = requests.get(crawled_naver_url)
        
        #html content取得
        soup = BeautifulSoup(response.text, 'html.parser')

        #DB挿入用レコード作成
        insert_title   = get_naver_title(soup)
        insert_content = get_naver_content(soup)
        insert_press   = get_naver_press(soup)
        insert_wrtier  = "writer"
        insert_url     = crawled_naver_url#!<urlは予め取得しておいた値を使用する
        insert_portal  = NAVER
        insert_date    = get_naver_date(soup)
        now_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        insert_create_time = now_date
        insert_updated_time = now_date

        #INSERT query作成
        #reprメソッドを使うと自動的に「''」に囲まれるので「''」省略する

        sql_insert = f"INSERT INTO news (id, title, content, press, writer, date, url, portal, created_at, updated_at)\n"
        sql_insert = sql_insert + f"VALUES ({new_id}, '{insert_title}' ,'{insert_content}', '{insert_press}', '{insert_wrtier}', '{insert_date}'::timestamptz,"
        sql_insert = sql_insert + f"{repr(insert_url)}, '{insert_portal}', '{insert_create_time}'::timestamptz, '{insert_updated_time}'::timestamptz);"
        
        print(insert_content)

        print(sql_insert)
        #create naver news
        cursor.execute(sql_insert,())
        db_conn.commit()

        #次のNEWSの挿入時のため増加させる
        new_id = new_id + 1

    #DB処理終了
    cursor.close()
    db_conn.close()

def get_naver_url(naver_url):
    naver_crwal_url = []
    naver_url_prefix = "https://news.naver.com"

    response = requests.get(naver_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    urls = soup.select(".ranking_list li .ranking_headline a")
    #newsを５件まで制限する
    for url in urls[:5]:
        print(url.get('href'))
        naver_crwal_url.append(naver_url_prefix + url.get('href'))

    return naver_crwal_url
    
def get_naver_title(soup):
    title = soup.select("#articleTitle")
    naver_crwal_title  = title[0].text

    naver_crwal_title = naver_crwal_title.replace("\'", "`", 100)
    return naver_crwal_title

def get_naver_content(soup):

    naver_crwal_content = ""
    del_str = "// flash 오류를 우회하기 위한 함수 추가\nfunction _flash_removeCallback() {}"

    contents = soup.select("#articleBodyContents")

    #フォーマットに合わせてトリミング
    temp_content = contents[0].text
    temp_content = temp_content.replace(del_str, '')
    temp_content = temp_content.split()  #全ての空白・改行文字削除
    temp_content = " ".join(temp_content)#全ての空白・改行文字削除
    temp_content = temp_content[:CONTENT_MAX_LEN] + NOT_END_STR

    temp_content = temp_content.replace("\'", "`", 100)
    naver_crwal_content = temp_content.replace("%", "Percent", 100)
    return naver_crwal_content

def get_naver_press(soup):
    naver_crawl_press = ""

    press = soup.select('.press_logo img')
    naver_crawl_press = press[0].get('title')

    return naver_crawl_press

def get_naver_date(soup):
    naver_crwal_date = ""

    date = soup.select('.t11')
    temp_date = date[0]

    #datetimeに合わせてフォーマットトリミング
    temp_date = temp_date.text[:10]
    temp_date = temp_date.replace(".", "-")
    naver_crawl_date = datetime.datetime.strptime(temp_date, "%Y-%m-%d")

    return naver_crawl_date