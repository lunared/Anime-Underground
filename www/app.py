from flask import Flask, render_template, request

app = Flask(__name__)

# App Configuration

BRAND = "Anime Underground"
SUBTITLE = "Live Fridays @ 9pm EST"
SCHEDULE = [
    {"id": 17991, "time": "09:00PM"},
    {"id": 1053, "time": "09:50PM"},
    {"id": 15895, "time": "10:15PM"},
    {"id": 394, "time": "11:00PM"}
]
WATCHED = [
    11017, 16900, 15742, 16247, 8550, 13, 17825, 1029, 166
]
CHAT_URI = "http://discordapp.com"
STREAM_NAME = "animeunderground"

# End App Configuration

SERIES = [ts['id'] for ts in SCHEDULE]
ALL_SERIES = WATCHED + SERIES

def load_anime():
    import xml.etree.ElementTree as ET
    import xml.dom.minidom as xmlprinter
    import requests

    # load up the schedule from our json file
    api = "http://cdn.animenewsnetwork.com/encyclopedia/api.xml?"

    query = []
    for show in ALL_SERIES:
        query.append("anime=" + str(show))

    api += "&".join(query)

    # query the api
    response = requests.get(api)
    xml = ET.fromstring(response.content)

    context = {
        'schedule': [],
        'watched': [],
    }

    class Timeslot:
        time = None
        _id = 0
        link = ""
        title = ""
        thumbnail = ""
        plot = ""
        genres = ""

        @property
        def id(self):
            return self._id

        @id.setter
        def id(self, value):
            self._id = value
            self.link = "http://www.animenewsnetwork.com/encyclopedia/anime.php?id=" + value


    # traverse the api xml response for show metadata
    for anime in [node for node in xml if node.tag == 'anime']:
        timeslot = Timeslot()
        timeslot.id = anime.attrib['id']
        genres = []

        # parse info
        for info in [node for node in anime if node.tag == 'info']:
            _type = info.attrib['type']
            if _type == 'Genres':
                genres.append(info.text)
            elif _type == 'Picture':
                images = [node for node in info if node.tag == 'img']
                if len(images) > 0:
                    timeslot.thumbnail = images[0].attrib['src']
            elif _type == 'Main title':
                timeslot.title = info.text
            elif _type == "Plot Summary":
                timeslot.plot = info.text
        timeslot.genres = ", ".join(genres)
        for SERIES in SCHEDULE:
            if SERIES['id'] == int(timeslot.id):
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
        "stream_root": f"{request.url_root}hls/{STREAM_NAME}.m3u8",
        "stream": f"{request.url_root}hls/{STREAM_NAME}_{resolution}/index.m3u8",
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
