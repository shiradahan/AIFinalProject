class Camper:
    def __init__(self, camper_id, age_group, preferred_sessions):
        self.camper_id = camper_id
        self.age_group = age_group
        self.preferred_sessions = preferred_sessions  # List of session IDs
        self.scheduled_sessions = []  # List to store the scheduled sessions

    def add_scheduled_session(self, session_id):
        self.scheduled_sessions.append(session_id)

    def __repr__(self):
        return f"Camper(ID: {self.camper_id}, Age Group: {self.age_group})"
