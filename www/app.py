from flask import Flask, render_template, request

app = Flask(__name__)

def load_anime():
    import json
    import xml.etree.ElementTree as ET
    import xml.dom.minidom as xmlprinter
    import requests

    # load up the schedule from our json file
    api = "http://cdn.animenewsnetwork.com/encyclopedia/api.xml?"
    all = []
    series = []
    watched = []
    schedule = dict()
    with open('static/schedule.json') as data_file:    
        data = json.load(data_file)
        schedule = data['schedule']
        series += [ts['id'] for ts in data['schedule']]
        watched += data['watched']
        all = series + watched

    query = []
    for show in all:
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
        for series in schedule:
            if series['id'] == int(timeslot.id):
                timeslot.time = series['id']
                break
        if not timeslot.time:
            context['watched'].append(timeslot)
        else:
            context['schedule'].append(timeslot)

    return context

def _base(stream):
    context = {
        "brand": "Anime Underground",
        "subtitle": "Live Fridays @ 9pm EST",
        "quality": "low",
        "stream": request.url_root + stream,
        "hostname": request.url_root,
        **load_anime()
    }
    
    return render_template("body.html", **context), 200


@app.route('/low')
def low_quality():
    return _base("hls/animeunderground_480p/index.m3u8")
    
@app.route('/')
@app.route('/high')
def high_quality():
    return _base("hls/animeunderground_720p/index.m3u8")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')