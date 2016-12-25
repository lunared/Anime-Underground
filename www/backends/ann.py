from .meta import AnimeBackend, Timeslot
import xml.etree.ElementTree as ET
import xml.dom.minidom as xmlprinter
import requests


class ANNTimeslot(Timeslot):
    def __init__(self):
        super().__init__("http://www.animenewsnetwork.com/encyclopedia/anime.php?id={}")


class ANNBackend(AnimeBackend):
    api = "http://cdn.animenewsnetwork.com/encyclopedia/api.xml"
        
    def test_backend(self):
        req = requests.get(ANNBackend.api)
        return req.status_code == 200

    def _make_request(self, series):
        return requests.get(ANNBackend.api, params={
            'anime': series
        })

    def load_anime(self, SCHEDULE, WATCHED):
        # do not query titles with provided names, as it's assuemd they are not already in the db
        ALL_SERIES = [] + [id for id in WATCHED if type(id) is int] + [s['id'] for s in SCHEDULE if type(s['id']) is int]
        NOQ_SERIES = [] + [id for id in WATCHED if type(id) is str] + [s['id'] for s in SCHEDULE if type(s['id']) is str]

        # load up the schedule from our json file
        # query the api
        response = self._make_request(ALL_SERIES)
        xml = ET.fromstring(response.content)

        context = {
            'schedule': [],
            'watched': [],
        }

        # traverse the api xml response for show metadata
        for anime in [node for node in xml if node.tag == 'anime']:
            timeslot = ANNTimeslot()
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

        for anime in NOQ_SERIES:
            timeslot = ANNTimeslot()
            timeslot.genres = ''
            timeslot.title = anime

            context['watched'].append(timeslot)

        return context
