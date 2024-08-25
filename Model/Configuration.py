from Model.Camper import Camper
from Model.Session import Session


class Configuration:
    def __init__(self):
        self._isEmpty = True
        self._campers = {}
        self._workshops = {}

    def getCamperById(self, id) -> Camper:
        return self._campers.get(id, None)

    def getWorkshopById(self, id) -> Session:
        return self._workshops.get(id, None)

    @property
    def numberOfCampers(self) -> int:
        return len(self._campers)

    @property
    def numberOfWorkshops(self) -> int:
        return len(self._workshops)

    @property
    def isEmpty(self) -> bool:
        return self._isEmpty

    @staticmethod
    def __parseCamper(dictConfig):
        id = dictConfig.get('id', 0)
        name = dictConfig.get('name', '')
        age_group = dictConfig.get('age_group', '')
        options = dictConfig.get('options', [])
        if id == 0 or name == '' or age_group == '' or not options:
            return None
        return Camper(id, name, age_group, options)

    @staticmethod
    def __parseWorkshop(dictConfig):
        id = dictConfig.get('id', 0)
        name = dictConfig.get('name', '')
        capacity = dictConfig.get('capacity', 0)
        if id == 0 or name == '' or capacity == 0:
            return None
        return Workshop(id, name, capacity)

    def parseFile(self, fileName):
        self._campers = {}
        self._workshops = {}
        self._isEmpty = True

        with codecs.open(fileName, "r", "utf-8") as f:
            data = json.load(f)

        for dictConfig in data:
            for key in dictConfig:
                if key == 'camper':
                    camper = self.__parseCamper(dictConfig[key])
                    if camper:
                        self._campers[camper.Id] = camper
                elif key == 'workshop':
                    workshop = self.__parseWorkshop(dictConfig[key])
                    if workshop:
                        self._workshops[workshop.Id] = workshop

        self._isEmpty = False
