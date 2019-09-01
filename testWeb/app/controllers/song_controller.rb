class SongController < ApplicationController
    protect_from_forgery with: :null_session #Set tokens not to work.FORM
    def index
        
    end

    def main
        @firstName = params[:firstname]
        @lastName = params[:lastname]
    end
end
