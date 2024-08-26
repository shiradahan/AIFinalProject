class Session:
    def __init__(self, session_id, name, age_group, capacity=15):
        self.session_id = session_id
        self.name = name
        self.age_group = age_group
        self.capacity = capacity
        self.enrolled_camper_ids = []

    def add_camper(self, camper_id):
        if len(self.enrolled_camper_ids) < self.capacity:
            self.enrolled_camper_ids.append(camper_id)
            return True
        return False

    def is_full(self):
        return len(self.enrolled_camper_ids) >= self.capacity

    def __repr__(self):
        return f"Session({self.name}, Age Group: {self.age_group}, Capacity: {self.capacity})"
