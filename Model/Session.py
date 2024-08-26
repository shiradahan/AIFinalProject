class Session:
    def __init__(self, session_id, name, age_group, capacity=15):
        self.session_id = session_id
        self.name = name
        self.age_group = age_group
        self.capacity = capacity
        self.enrolled_camper_ids = []

    def add_camper(self, camper_id, camper_age_group):
        if len(self.enrolled_camper_ids) < self.capacity and self.age_group == camper_age_group:
            self.enrolled_camper_ids.append(camper_id)
            return True
        return False

    # useful if we ever need to remove a camper from a session (e.g., during a mutation or crossover operation)
    def remove_camper(self, camper_id):
        if camper_id in self.enrolled_camper_ids:
            self.enrolled_camper_ids.remove(camper_id)
            return True
        return False

    def is_full(self):
        return len(self.enrolled_camper_ids) >= self.capacity

    def __repr__(self):
        return f"Session({self.name}, Age Group: {self.age_group}, Capacity: {self.capacity})"
