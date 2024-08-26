class Session:
    def __init__(self, id, name, capacity, age_group):
        """
        Initializes a Session object.

        :param id: Unique identifier for the session
        :param name: Name of the session
        :param capacity: Maximum number of campers that can attend the session
        :param age_group: Age group(s) that the session is suitable for
        """
        self.id = id
        self.name = name
        self.capacity = capacity
        self.age_group = age_group  # Expecting a single age group or a list of age groups

    def __str__(self):
        return f"Session(ID: {self.id}, Name: {self.name}, Capacity: {self.capacity}, Age Group: {self.age_group})"

    def __repr__(self):
        return self.__str__()

    def fits_age_group(self, camper_age_group):
        """
        Checks if the session is suitable for the camper based on their age group.

        :param camper_age_group: Age group of the camper
        :return: True if the session fits the camper's age group, False otherwise
        """
        if isinstance(self.age_group, list):
            return camper_age_group in self.age_group
        return self.age_group == camper_age_group
