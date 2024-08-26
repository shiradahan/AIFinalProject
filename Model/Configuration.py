import pandas as pd


class Configuration:

    def __init__(self):
        # Indicate that configuration is not parsed yet
        self._isEmpty = True
        # Parsed campers
        self._campers = {}
        # Parsed sessions
        self._sessions = {}
        # Parsed age units
        self._age_units = {}

    # Returns camper with specified name
    def getCamperByName(self, name):
        if name in self._campers:
            return self._campers[name]
        return None

    @property
    def numberOfCampers(self):
        return len(self._campers)

    # Returns session with specified name
    def getSessionByName(self, name):
        if name in self._sessions:
            return self._sessions[name]
        return None

    @property
    def numberOfSessions(self):
        return len(self._sessions)

    # Returns age unit with specified name
    def getAgeUnitByName(self, name):
        if name in self._age_units:
            return self._age_units[name]
        return None

    @property
    def numberOfAgeUnits(self):
        return len(self._age_units)

    @property
    def isEmpty(self):
        return self._isEmpty

    def parseFile(self, fileName):
        # Clear previously parsed objects
        self._campers = {}
        self._sessions = {}
        self._age_units = {}

        # Read Excel file
        data = pd.read_excel(fileName)

        # Process each row in the DataFrame
        for _, row in data.iterrows():
            camper_name = row['Camper\'s name']
            age_unit = row['Age Unit']
            preferences = [row['Selection #1'], row['Selection #2'], row['Selection #3'], row['Selection #4']]

            # Store campers
            self._campers[camper_name] = {
                'age_unit': age_unit,
                'preferences': preferences
            }

            # Update sessions from camper preferences
            for pref in preferences:
                if pref not in self._sessions:
                    self._sessions[pref] = 0

            # Update age units
            if age_unit not in self._age_units:
                self._age_units[age_unit] = []

            self._age_units[age_unit].append(camper_name)

        # Initialize session capacities based on the number of campers
        for session in self._sessions.keys():
            self._sessions[session] = 15  # Example capacity, adjust as needed

        self._isEmpty = False
