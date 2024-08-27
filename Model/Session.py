class Session:
    def __init__(self, session_id, start_time, end_time):
        self.session_id = session_id
        self.start_time = start_time
        self.end_time = end_time
        self.campers = []  # List of campers assigned to this session
        self.age_groups = set()  # Set of age groups in this session

    def add_camper(self, camper):
        if self.is_compatible(camper) and len(self.campers) < 15:
            self.campers.append(camper)
            self.age_groups.add(camper.age_group)
            return True
        return False

    def is_compatible(self, camper):
        if not self.age_groups:
            return True  # If no age group is set, any camper can be added
        if camper.age_group in self.age_groups:
            return True  # If camper's age group matches the existing ones
        # Check if camper's age group is adjacent to the existing ones
        return abs(max(self.age_groups) - camper.age_group) <= 1

    def has_overlapping(self, other_session):
        return not (self.end_time <= other_session.start_time or self.start_time >= other_session.end_time)
