require 'nokogiri'
require 'open-uri'
require 'date'

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

class SecondController < ApplicationController
    def index
        ###################################################NATE#############################################
        nate_crwal_url = []         #<!記事URL
        nate_url_prefix = "https:"
        nate_news = []

        #nate url取得
        nate_crwal_url = get_nate_url(NATE_URL)

        for index in 0..NEWS_LEN-1
            #create temp nate news instance
            news = News.new
            url = nate_url_prefix + nate_crwal_url.at(index)
            puts url
            doc = Nokogiri::HTML(open(url))
            news.url       = url
            news.title     = get_nate_title(doc)
            news.content   = get_nate_content(doc)
            news.date      = get_nate_date(doc)
            news.press     = get_nate_cor(doc)
            #add nate news
            nate_news.push(news)
        end
        @nate_news = nate_news
        
        ###################################################DAUM#############################################
        daum_crwal_title = []       #<!記事タイトル
        daum_crwal_url = []         #<!記事URL
        daum_crwal_content = []     #<!記事の本文
        daum_crwal_cor = []         #<!取材社名
        daum_crwal_date = []        #<!記事の日付

        #get 記事URL and 取材社名
        urlCor = get_daum_url_cor(DAUM_URL)
        daum_crwal_url = urlCor[0]
        daum_crwal_cor = urlCor[1]

        for index in 0..NEWS_LEN
            doc = Nokogiri::HTML(open(daum_crwal_url.at(index)))
            daum_crwal_title.push(get_daum_title(doc))
            daum_crwal_date.push(get_daum_date(doc))
            daum_crwal_content.push(get_daum_content(doc))
        end
        @daum_title_crwal   =   daum_crwal_title
        @daum_cor_crwal     =   daum_crwal_cor
        @daum_date_crwal    =   daum_crwal_date
        @daum_url_crwal     =   daum_crwal_url
        @daum_content_crwal =   daum_crwal_content

        ###################################################NAVER#############################################
        naver_crwal_title = []       #<!記事タイトル
        naver_crwal_url = []         #<!記事URL
        naver_crwal_content = []     #<!記事の本文
        naver_crwal_cor = []         #<!取材社名
        naver_crwal_date = []        #<!記事の日付

        naver_url_prefix = "https://news.naver.com"
        del_str = "// flash 오류를 우회하기 위한 함수 추가\nfunction _flash_removeCallback() {}"
        cor_date_boundary = 3

        doc = Nokogiri::HTML(open(NAVER_URL))
        doc.css('.ranking_list li').each do |element|
            #URL抽出
            naver_crwal_url.push(naver_url_prefix + element.css('a').first["href"])
        end

        for index in 0..NEWS_LEN-1
            temp_content = ""
            doc = Nokogiri::HTML(open(naver_crwal_url.at(index)))
            doc.css('#articleBodyContents').each do |element|
                temp_content = element.text
            end

            temp_content = temp_content.gsub(del_str.encode("UTF-8"), "")
            trimminged_content = temp_content
            naver_crwal_content.push(trimminged_content[0..CONTENT_MAX_LEN] + NOT_END_STR)

            doc.css('#articleTitle').each do |element|
                naver_crwal_title.push(element.text)
            end

            doc.css('.t11').each do |element|
                naver_crwal_date.push("20" + element.text[cor_date_boundary-1..9])
            end 

            doc.css('.press_logo').each do |element|
                naver_crwal_cor.push(element.css('img').first["title"])
            end
        end
        @naver_title_crwal   =   naver_crwal_title
        @naver_cor_crwal     =   naver_crwal_cor
        @naver_date_crwal    =   naver_crwal_date
        @naver_url_crwal     =   naver_crwal_url
        @naver_content_crwal =   naver_crwal_content

        @len = 5
    end

    def get_nate_url(nate_url)
        nate_crwal_url = []
        doc = Nokogiri::HTML(open(nate_url))
        doc.css('.mlt01').each do |element|
            #URL抽出
            nate_crwal_url.push(element.css('a').first["href"])
        end
        return nate_crwal_url
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

    def get_nate_title(doc)
        temp_title = ""
        doc.css('.articleSubecjt').each do |element|
            temp_title = element.text[0..-1]#<!2行にならないように文字制限
        end
        return temp_title
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

    #指定したURLから記事をcrwalし、必要な要素を抽出する
    #return urlリスト,corsリスト
    def get_daum_url_cor(daum_url)
        urlCor = []
        daum_crwal_url = []
        daum_crwal_cor = []
        doc = Nokogiri::HTML(open(daum_url))
        doc.css('.list_news2 li').each do |element|
            #URL抽出
            daum_crwal_url.push(element.css('a').first["href"])
        end
        #url追加
        urlCor.push(daum_crwal_url)
        doc.css('.info_news').each do |element|
            #取材会社抽出
            daum_crwal_cor.push(element.text)
        end
        #取材会社追加
        urlCor.push(daum_crwal_cor)
    end

    def get_daum_title(doc)
        daum_crwal_title = ""
        doc.css('.tit_view').each do |element|
            daum_crwal_title = element.text
        end
        return daum_crwal_title
    end

    def get_daum_date(doc)
        daum_crwal_date = ""
        doc.css('.info_view span:nth-child(2)').each do |element|
            cor_date_boundary = element.text.index(DATE_BOUNDARY_STR)
            daum_crwal_date = element.text[cor_date_boundary..12]
        end
        return daum_crwal_date
    end
    
    def get_daum_content(doc)
        temp_contents = []
        daum_crwal_content = ""
        doc.css('#harmonyContainer p').each do |element|
            temp_contents.push(element.text)
        end
        trimminged_content = temp_contents.join
        trimminged_content += NOT_END_STR
        daum_crwal_content = trimminged_content[0..CONTENT_MAX_LEN] + NOT_END_STR
        return daum_crwal_content
    end

    def get_naver_url(naver_url)
        naver_crwal_url = []
        doc = Nokogiri::HTML(open(naver_url))
        doc.css('.ranking_list li').each do |element|
            #URL抽出
            naver_crwal_url.push(naver_url_prefix + element.css('a').first["href"])
        end
        return naver_crwal_url
    end

    def naterefresh
        @content = "successRet"
        render json: {data:@content}
    end
end
