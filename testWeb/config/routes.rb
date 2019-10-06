Rails.application.routes.draw do
  #root url is linked index method of song
  #root 'song#index'
  get '/second/index' => 'second#index'
  get '/second/kr' => 'second#kr'
end
