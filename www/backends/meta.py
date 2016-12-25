import abc
from abc import abstractmethod

class AnimeBackend:
    @abstractmethod
    def load_anime(self, SCHEDULE, WATCHED):
        pass

class Timeslot:
    time = None
    _id = 0
    link = ""
    title = ""
    thumbnail = ""
    plot = ""
    genres = ""
    episodes = 0

    def __init__(self, link_fmt):
        self.link_fmt = link_fmt

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value
        self.link = self.link_fmt.format(value)
