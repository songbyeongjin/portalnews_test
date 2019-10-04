from bs4 import BeautifulSoup
import requests
import os
import psycopg2
import datetime
        

#定数定義
NOT_END_STR = "[MORE...]"

CONTENT_MAX_LEN = 200
NEWS_LEN = 5
DAUM ="daum"
DAUM_URL = "https://media.daum.net/ranking/popular/"

def handler(event, context):
    response = requests.get(DAUM)
    parsedHtml = response.text
    soup = BeautifulSoup(parsedHtml, 'html.parser')
    
    ###################################################DAUM#############################################
    daum_news = []

    #DB接続
    db_conn = psycopg2.connect(
        host     = os.environ['host'],
        dbname   = os.environ['database'],
        user     = os.environ['username'],
        password = os.environ['password'],
        port     = os.environ['port'])

    cursor = db_conn.cursor()

    #DELETE query作成
    sql_delete = f"delete from news where portal = '{DAUM}'"
    #新しいNEWSを挿入する前に全てのDAUM NEWSを削除する
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

    #get 記事URL and 取材社名
    urlCor = get_daum_url_cor(DAUM_URL)
    daum_crwal_url = urlCor[0]
    daum_crwal_cor = urlCor[1]

    for index in range(0, NEWS_LEN):
        crawled_daum_url = daum_crwal_url[index]
        response = requests.get(crawled_daum_url)
        
        #html content取得
        soup = BeautifulSoup(response.text, 'html.parser')

        #DB挿入用レコード作成
        insert_title   = get_daum_title(soup)
        insert_content = get_daum_content(soup)
        insert_press   = daum_crwal_cor[index]
        insert_wrtier  = "writer"
        insert_url     = daum_crwal_url[index]#!<urlは予め取得しておいた値を使用する
        insert_portal  = DAUM
        insert_date    = get_daum_date(soup)
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
        #create daum news
        cursor.execute(sql_insert,())
        db_conn.commit()

        #次のNEWSの挿入時のため増加させる
        new_id = new_id + 1

    #DB処理終了
    cursor.close()
    db_conn.close()

#指定したURLから記事をcrwalし、必要な要素を抽出する
#return urlリスト,corsリスト
def get_daum_url_cor(daum_url):
    urlCor = []
    daum_crwal_url = []
    daum_crwal_cor = []

    response = requests.get(daum_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    daum_crwal_url = soup.select(".ranking_list li .ranking_headline a")
    urlCor.append(daum_crwal_url.text)
    daum_crwal_cor = soup.select(".info_news")
    urlCor.append(daum_crwal_cor.text)

def get_daum_title(soup):
    daum_crwal_title = soup.select(".tit_view")
    return daum_crwal_title.text

def get_daum_content(soup):
    temp_contents = soup.select("#harmonyContainer p")
    trimminged_content = " ".join(temp_contents.text)
    daum_crwal_content = trimminged_content[0..CONTENT_MAX_LEN] + NOT_END_STR
    return daum_crwal_content

def get_daum_date(soup):
    crawled_date = soup.select(".info_view span:nth-child(2)")
    date = crawled_date[0].text
    cor_date_boundary = date.find(DATE_BOUNDARY_STR)
    daum_crwal_date = date[cor_date_boundary:12]

    #daum記事のdateが取得できない場合はデフォルトとして、当日の日付を利用する
    if daum_crwal_date == "":
        return datetime.datetime.now
    else
        return datetime.datetime.strptime(temp_date, "%Y-%m-%d")