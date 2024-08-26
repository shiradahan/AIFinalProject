import pandas as pd

from .Camper import Camper
from .Session import Session
from .Schedule import Schedule


# Reads configuration from Excel file and stores parsed objects
class Configuration:

    def __init__(self):
        self._isEmpty = True
        self._campers = {}
        self._workshops = {}
        self._schedule = []

    @property
    def numberOfCampers(self) -> int:
        return len(self._campers)

    @property
    def numberOfWorkshops(self) -> int:
        return len(self._workshops)

    @property
    def schedule(self) -> []:
        return self._schedule

    @property
    def isEmpty(self) -> bool:
        return self._isEmpty

    @staticmethod
    def __parseCamper(row) -> Camper:
        try:
            id = row['ID']
            name = row['Name']
            age_group = row['Age Group']
            preferences = row['Preferences'].split(',')  # Assuming preferences are comma-separated
            return Camper(id, name, age_group, preferences)
        except KeyError:
            return None

    @staticmethod
    def __parseSession(row) -> Session:
        try:
            id = row['ID']
            name = row['Name']
            capacity = row['Capacity']
            age_group = row['Age Group']
            return Session(id, name, capacity, age_group)
        except KeyError:
            return None

    def __parseSchedule(self, row) -> Schedule:
        try:
            camper_id = row['Camper ID']
            workshop_id = row['Workshop ID']
            return Schedule(camper_id, workshop_id)
        except KeyError:
            return None

    def parseFile(self, fileName):
        self._campers = {}
        self._workshops = {}
        self._schedule = []

        # Read data from Excel file
        xls = pd.ExcelFile(fileName)

        # Load sheets into dataframes
        campers_df = pd.read_excel(xls, sheet_name='Campers')
        workshops_df = pd.read_excel(xls, sheet_name='Workshops')
        schedule_df = pd.read_excel(xls, sheet_name='Schedule')

        # Parse and store campers
        for _, row in campers_df.iterrows():
            camper = self.__parseCamper(row)
            if camper:
                self._campers[camper.id] = camper

        # Parse and store workshops
        for _, row in workshops_df.iterrows():
            workshop = self.__parseWorkshop(row)
            if workshop:
                self._workshops[workshop.id] = workshop

        # Parse and store schedule
        for _, row in schedule_df.iterrows():
            sched = self.__parseSchedule(row)
            if sched:
                self._schedule.append(sched)

        self._isEmpty = False
