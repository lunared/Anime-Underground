Anime-Underground Dockerfile/Docker Compose
=====================

This Docker Compose builds off of the [nginx-rtmp-dockerfile](https://github.com/brocaar/nginx-rtmp-dockerfile) 
by providing a light weight, easy to configure web interface built on Flask for your stream.
The website contains an HLS HTML5 web  player, a link to your HLS (for people who'd rather 
use something like VLC to watch your stream), a schedule and history of anime for your stream with
metadata fetched from ANN, a quality toggle, and a button to your stream's choice of web accessible chatroom.


How to use
----------

1. Build and run the container (`docker-compose build && docker-compose up -d`)

2. Stream your live content to `rtmp://localhost:1935/encoder/stream_name` where
   `stream_name` is the name of your stream.

3. In any HTML5 HLS capable browser, navigate to `http://localhost/` and enjoy your 
   anime stream.  Stream comes with 2 qualities (720 and 480p).  Note that the first time,
   it might take a few (10-15) seconds before the stream works. This is because
   when you start streaming to the server, it needs to generate the first
   segments and the related playlists.


Links
-----

* http://nginx.org/
* https://github.com/arut/nginx-rtmp-module
* https://www.ffmpeg.org/
* https://obsproject.com/
* https://github.com/dailymotion/hls.js
* https://www.animenewsnetwork.com/
* http://flask.pocoo.org/
* http://getskeleton.com/
