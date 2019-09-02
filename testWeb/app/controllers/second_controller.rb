require 'nokogiri'
require 'open-uri'

#定数定義
NOT_END_STR = "[MORE...]"

CONTENT_MAX_LEN = 200
DATE_BOUNDARY_STR = "2019"#<!年が経つと要変更

#dateパラメーターが現在日・時間より遅く設定されると現在日・時間に繋がるため、2099年99月99日に設定する
NATE_URL = "https://news.nate.com/rank/interest?sc=all&p=day&date=20999999"

DAUM_URL = "https://media.daum.net/ranking/popular/"

#naver HTML DOM構想の問題で、全年齢のRANKING NEWSが表示されないため、30代のデータを収集
NAVER_URL = "https://news.naver.com/main/ranking/popularDay.nhn?rankingType=age&subType=30"

class SecondController < ApplicationController
    def index
        ###################################################NATE#############################################
        list_crwal_title = []       #<!記事タイトル
        list_crwal_url = []         #<!記事URL
        list_crwal_cor_date = []    #<!取材社名・記事の日付
        list_crwal_cor = []         #<!取材社名
        list_crwal_date = []        #<!記事の日付
        list_crwal_content = []     #<!記事の本文

        nate_url_prefix = "https:"
        news_len = 5;

        #指定したURLから記事をcrwalし、必要な要素を抽出する
        doc = Nokogiri::HTML(open(NATE_URL))
        doc.css('.mlt01').each do |element|
            #タイトル抽出
            list_crwal_title.push(element.css('.tit').text[0..-1])#<!2行にならないように文字制限
            #取材社名・日付抽出
            list_crwal_cor_date.push(element.css('.medium').text)
            #URL抽出
            list_crwal_url.push(element.css('a').first["href"])
        end

        #取材社名と日付を分ける
        for cor_date in list_crwal_cor_date
            #"2019-"を前後に分ける"
            cor_date_boundary = cor_date.index(DATE_BOUNDARY_STR)
            list_crwal_cor.push(cor_date[0..cor_date_boundary-1])
            list_crwal_date.push(cor_date[cor_date_boundary..-1])
        end

        #取得した記事数

        for index in 0..news_len-1
            temp_contents = []
            doc = Nokogiri::HTML(open(nate_url_prefix + list_crwal_url.at(index)))
            doc.css('#realArtcContents').each do |element|
                temp_content = element.text.squish#0..CONTENT_MAX_LEN]#<!"¥n"を削除し、文字数を制限する
                temp_contents.push(temp_content)
                end
            #リストを文字列に型変換
            trimminged_content = temp_contents.join
            trimminged_content = trimminged_content[0..CONTENT_MAX_LEN] + NOT_END_STR
            list_crwal_content.push(trimminged_content)
        end

        #パラメーターを渡す
        @title_crwal = list_crwal_title
        @cor_crwal = list_crwal_cor
        @date_crwal = list_crwal_date
        @url_crwal = list_crwal_url
        @content_crwal = list_crwal_content
        

        ###################################################DAUM#############################################
        daum_crwal_title = []       #<!記事タイトル
        daum_crwal_url = []         #<!記事URL
        daum_crwal_content = []     #<!記事の本文
        daum_crwal_cor = []         #<!取材社名
        daum_crwal_date = []        #<!記事の日付

        #指定したURLから記事をcrwalし、必要な要素を抽出する
        doc = Nokogiri::HTML(open(DAUM_URL))
        doc.css('.list_news2 li').each do |element|
            #URL抽出
            daum_crwal_url.push(element.css('a').first["href"])
        end
        doc.css('.info_news').each do |element|
            #URL抽出
            daum_crwal_cor.push(element.text)
        end


        #取得した記事数
        news_len = 5
        str = ""
        for index in 0..5
            temp_contents = []
            doc = Nokogiri::HTML(open(daum_crwal_url.at(index)))
            doc.css('.tit_view').each do |element|
                daum_crwal_title.push(element.text)
            end
            doc.css('.info_view span:nth-child(2)').each do |element|
                cor_date_boundary = element.text.index(DATE_BOUNDARY_STR)
                daum_crwal_date.push(element.text[cor_date_boundary..12])
            end
            doc.css('#harmonyContainer p').each do |element|
                temp_contents.push(element.text)
            end
            trimminged_content = temp_contents.join
            trimminged_content += NOT_END_STR
            daum_crwal_content.push(trimminged_content[0..CONTENT_MAX_LEN] + NOT_END_STR)
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

        for index in 0..news_len-1
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

    def nate

    end

    def naterefresh
        @content = "successRet"
        render json: {data:@content}
    end
end
