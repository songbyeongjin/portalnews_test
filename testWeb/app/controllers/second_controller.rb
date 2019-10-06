require 'nokogiri'
require 'open-uri'
require 'date'

NEWS_LEN = 5
class SecondController < ApplicationController
    def kr
        #NATE
        nate_news = News.where(portal:'nate').take(NEWS_LEN)
        print(nate_news)
        @nate_news = nate_news

        #DAUM
        daum_news = News.where(portal:'daum').take(NEWS_LEN)
        @daum_news = daum_news
      
        #NAVER
        naver_news = News.where(portal:'naver').take(NEWS_LEN)
        @naver_news = naver_news

        @len = NEWS_LEN
    end
end
