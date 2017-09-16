from flask import Flask, render_template, request
import importlib

app = Flask(__name__)

# App Configuration
from settings import *

anime = {}
backend = None

def _base(quality):
    resolution = "480p" if quality == 'low' else "720p"
    context = {
        "brand": BRAND,
        "subtitle": SUBTITLE,
        "quality": quality,
        "stream_root": "{:s}hls/{:s}.m3u8".format(request.url_root, STREAM_NAME),
        "stream": "{:s}hls/{:s}_{:s}/index.m3u8".format(request.url_root, STREAM_NAME, resolution),
        "chat": CHAT_URI,
        "backend": {
            "name": backend.name,
            "url": backend.url
        },
        **anime
    }

    return render_template("body.html", **context), 200


@app.route('/low')
def low_quality():
    return _base("low")


@app.route('/')
@app.route('/high')
def high_quality():
    return _base("high")


if __name__ == '__main__':
    import importlib
    
    anime = None
    # test backends
    for config in SCHEDULE:
        b = getattr(importlib.import_module('backends'), config['backend'])()
        if b.test_backend():
            anime = b.load_anime(config['schedule'], config['watched'])
            backend = b
            break

    if not anime:
        raise Exception("Could not fetch anime schedule") 

    app.run(debug=True, host='0.0.0.0')
