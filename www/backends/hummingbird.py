from .meta import AnimeBackend, Timeslot
from settings import HUMMINGBIRD_API_KEY
import requests

class HummingbirdTimeslot(Timeslot):
    def __init__(self):
        super().__init__("https://hummingbird.me/anime/{0}")

class HummingbirdBackend(AnimeBackend):
    api = "http://hummingbird.me/api/v2/anime/{0}"

    def test_backend(self):
        req = self._perform_request('dragonball')
        return req.status_code == 200

    def _perform_request(self, series):
        return requests.get(self.api.format(series), headers={
            'X-Client-Id': HUMMINGBIRD_API_KEY
        }) 

    def load_anime(self, SCHEDULE, WATCHED):
        ALL_SERIES = [] + WATCHED + [s['id'] for s in SCHEDULE]

        # load up the schedule from our json file
        context = {
            'schedule': [],
            'watched': [],
        }

        for show in ALL_SERIES:
            # query the api
            response = self._perform_request(show)
            anime = response.json().get('anime')
            if anime:
                timeslot = HummingbirdTimeslot()
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
