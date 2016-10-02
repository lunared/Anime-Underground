from flask import Flask, render_template, request

app = Flask(__name__)

# App Configuration

BRAND = "Anime Underground"
SUBTITLE = "Live Fridays @ 9pm EST"
SCHEDULE = [
    {"id": 'mawaru-penguindrum', "time": "09:00PM"},
    {"id": 'nourin', "time": "09:50PM"},
    {"id": 'mushishi-zoku-shou', "time": "10:15PM"},
    {"id": 'thunderbolt-fantasy', "time": "11:00PM"}
]
WATCHED = [
    'working-1',
    'wakako-zake',
    'pupipo',
    'danna-ga-nani-wo-itteiru-ka-wakaranai-ken',
    'gyakkyou-burai-kaiji-ultimate-survivor',
    'cowboy-bebop',
    'mobile-suit-gundam-thunderbolt',
    'ys',
    'serial-experiments-lain',
    'sakamoto-desu-ga',
    'android-ana-maico-2010',
    'lodoss-tou-senki'
]
CHAT_URI = "http://discordapp.com"
STREAM_NAME = "animeunderground"
HUMMINGBIRD_API_KEY = "d4cba8366841f91d8a70"

# End App Configuration

SERIES = [ts['id'] for ts in SCHEDULE]
ALL_SERIES = WATCHED + SERIES

def load_anime():
    import requests

    class Timeslot:
        time = None
        _id = 0
        link = ""
        title = ""
        thumbnail = ""
        plot = ""
        genres = ""
        episodes = 0

        @property
        def id(self):
            return self._id

        @id.setter
        def id(self, value):
            self._id = value
            self.link = "https://hummingbird.me/anime/{0}".format(value)

    # load up the schedule from our json file
    api = "http://hummingbird.me/api/v2/anime/{0}"
    context = {
        'schedule': [],
        'watched': [],
    }

    for show in ALL_SERIES:
        # query the api
        response = requests.get(api.format(show), headers={
	    'X-Client-Id': HUMMINGBIRD_API_KEY
        })
        anime = response.json().get('anime')
        if anime:
            timeslot = Timeslot()
            timeslot.id = anime['id']
            timeslot.title = anime['titles']['canonical']
            timeslot.thumbnail = anime['poster_image']
            timeslot.genres = ", ".join(anime['genres'])
            timeslot.episodes = anime['episode_count']
            timeslot.plot = anime['synopsis']
            for SERIES in SCHEDULE:
                if SERIES['id'] == show:
                    timeslot.time = SERIES['time']
                    break
            if not timeslot.time:
                context['watched'].append(timeslot)
            else:
                context['schedule'].append(timeslot)

    return context

def _base(quality):
    resolution = "480p" if quality == 'low' else "720p"
    context = {
        "brand": BRAND,
        "subtitle": SUBTITLE,
        "quality": quality,
        "stream_root": "{:s}hls/{:s}.m3u8".format(request.url_root, STREAM_NAME),
        "stream": "{:s}hls/{:s}_{:s}/index.m3u8".format(request.url_root, STREAM_NAME, resolution),
        "chat": CHAT_URI,
        **load_anime()
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
    app.run(debug=True, host='0.0.0.0')
