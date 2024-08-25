class Session:
    def __init__(self, id, time, location, capacity):
        self.id = id
        self.time = time
        self.location = location
        self.capacity = capacity
        self.assignments = []

    def is_full(self):
        return len(self.assignments) >= self.capacity

    def add_camper(self, camper):
        if not self.is_full():
            self.assignments.append(camper)
            return True
        return False