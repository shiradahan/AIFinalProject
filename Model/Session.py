class Session:
    def __init__(self, id, name, capacity):
        self.Id = id
        self.Name = name
        self.Capacity = capacity
        self.RegisteredCampers = []  # List of campers assigned to this workshop
