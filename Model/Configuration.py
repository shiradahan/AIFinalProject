import pandas as pd


class Configuration:

    def __init__(self):
        # Indicate that configuration is not parsed yet
        self.is_empty = True
        # Parsed campers
        self.campers = {}
        # Parsed sessions
        self.sessions = {}
        # Parsed age units
        self.age_units = {}

    # Returns camper with specified name
    def getCamperByName(self, name):
        if name in self.campers:
            return self.campers[name]
        return None

    @property
    def numberOfCampers(self):
        return len(self.campers)

    # Returns session with specified name
    def getSessionByName(self, name):
        if name in self.sessions:
            return self.sessions[name]
        return None

    @property
    def numberOfSessions(self):
        return len(self.sessions)

    # Returns age unit with specified name
    def getAgeUnitByName(self, name):
        if name in self.age_units:
            return self.age_units[name]
        return None

    @property
    def numberOfAgeUnits(self):
        return len(self.age_units)

    @property
    def isEmpty(self):
        return self.is_empty

    def parseFile(self, fileName):
        # Clear previously parsed objects
        self.campers = {}
        self.sessions = {}
        self.age_units = {}

        # Read Excel file
        data = pd.read_excel(fileName)

        # Process each row in the DataFrame
        for _, row in data.iterrows():
            camper_name = row['Camper\'s name']
            age_unit = row['Age Unit']
            preferences = [row['Selection #1'], row['Selection #2'], row['Selection #3'], row['Selection #4']]

            # Store campers
            self.campers[camper_name] = {
                'age_unit': age_unit,
                'preferences': preferences
            }

            # Update sessions from camper preferences
            for pref in preferences:
                if pref not in self.sessions:
                    self.sessions[pref] = 0

            # Update age units
            if age_unit not in self.age_units:
                self.age_units[age_unit] = []

            self.age_units[age_unit].append(camper_name)

        # Initialize session capacities based on the number of campers
        for session in self.sessions.keys():
            self.sessions[session] = 15  # Example capacity, adjust as needed

        self.is_empty = False
