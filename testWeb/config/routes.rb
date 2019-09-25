Rails.application.routes.draw do
  #root url is linked index method of song
  #root 'song#index'
  get '/song/index' => 'song#index'
  post '/song/main' => 'song#main'


  get '/second/index' => 'second#index'
  get '/second/nate' => 'second#nate'
  get '/second/kr' => 'second#kr'
  get '/second/index/naterefresh' => 'second#naterefresh'
  get '/second/:name' => 'second#name'
end
