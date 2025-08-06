from .db import Database
from .singleton import Singleton

class Excel(metaclass=Singleton):
    def __init__(self):
        if not hasattr(self, '_db'):
            self._db = Database()
