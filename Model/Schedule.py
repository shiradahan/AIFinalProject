class Schedule:
    def __init__(self):
        self.Sessions = {}
        self.Campers = {}

    def addWorkshop(self, session):
        self.Sessions[session.Id] = session

    def addCamper(self, camper):
        self.Campers[camper.Id] = camper

    def assignCampers(self):
        # Ensure that we can track assignments
        for workshop in self.Sessions.values():
            workshop.RegisteredCampers = []

        # Attempt to assign campers to workshops
        for camper in self.Campers.values():
            assigned = False
            for option in camper.Options:
                session = self.Sessions.get(option)
                if session and session.addCamper(camper):
                    assigned = True
                    break

            if not assigned:
                print(f"Camper {camper.Name} could not be assigned to any preferred workshop.")

    def printAssignments(self):
        for session in self.Sessions.values():
            print(f"Workshop {session.Name}:")
            for camper in session.RegisteredCampers:
                print(f"  Camper: {camper.Name} (Age Group: {camper.AgeGroup})")
