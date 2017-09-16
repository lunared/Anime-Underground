from .meta import AnimeBackend, Timeslot
import requests

class KitsuTimeslot(Timeslot):
    def __init__(self, link):
        super().__init__(link)

class KitsuBackend(AnimeBackend):
    api = "http://kitsu.io/api/edge/anime?filter[slug]={0}&fields[anime]=slug,posterImage,canonicalTitle,synopsis,genres,episodeCount&include=genres&page[limit]=20"
    name = "Kitsu"
    url = "https://kitsu.io"

    def test_backend(self):
        req = self._perform_request('dragonball')
        return req.status_code == 200

    def headers(self):
        return {
            'Accept': 'application/vnd.api+json',
            'Content-Type': 'application/vnd.api+json'
        }

    def _perform_request(self, series):
        return requests.get(self.api.format(series), headers=self.headers()) 

    def load_anime(self, SCHEDULE, WATCHED):
        ALL_SERIES = [] + WATCHED + [s['id'] for s in SCHEDULE]

        # load up the schedule from our json file
        context = {
            'schedule': [],
            'watched': [],
        }

        # query the api
        genres = {
            genre['id']: genre['attributes']['name']
            for genre in requests.get(
                "https://kitsu.io/api/edge/genres?page[limit]=100&fields[genres]=name", 
                headers=self.headers()
            ).json().get('data')
        }
        series = []
        for chunk in range(0, len(ALL_SERIES), 20):
            request = self._perform_request(",".join(ALL_SERIES[chunk:chunk+20])).json()
            series.extend(request.get('data'))

        for show in series:
            attr = show['attributes']
            timeslot = KitsuTimeslot("https://kitsu.io/anime/"+attr['slug'])
            timeslot.id = attr['slug']
            timeslot.title = attr['canonicalTitle']
            timeslot.thumbnail = attr['posterImage']['tiny'] if attr['posterImage'] else None
            timeslot.genres = ", ".join(list(map(lambda genre: genres[genre['id']], show['relationships']['genres']['data'])))
            timeslot.episodes = attr['episodeCount']
            timeslot.plot = attr['synopsis']
            for SERIES in SCHEDULE:
                if SERIES['id'] == attr['slug']:
                    timeslot.time = SERIES['time']
                    break
            if not timeslot.time:
                context['watched'].append(timeslot)
            else:
                context['schedule'].append(timeslot)

        context['watched'].sort(key=lambda show: WATCHED.index(show.id))

        return context
