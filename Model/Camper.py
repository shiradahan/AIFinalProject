class Camper:
    def __init__(self, camper_id, age_group, preferred_sessions):
        self.camper_id = camper_id
        self.age_group = age_group
        self.preferred_sessions = preferred_sessions  # List of session IDs
        self.scheduled_sessions = []  # List to store the scheduled sessions

    def add_scheduled_session(self, session_id):
        if session_id not in self.scheduled_sessions:
            self.scheduled_sessions.append(session_id)
        else:
            raise ValueError(f"Session {session_id} already scheduled for this camper.")

    def is_preferred(self, session_id):
        """Check if the given session ID is in the camper's preferences."""
        return session_id in self.preferred_sessions

    def rank_preferences(self, session_id):
        """Return the rank of the given session ID in the camper's preferences.
        Rank is based on the index in the preferred_sessions list."""
        if session_id in self.preferred_sessions:
            return self.preferred_sessions.index(session_id)
        return float('inf')  # Return infinity if session ID is not in preferences

    def __repr__(self):
        return f"Camper(ID: {self.camper_id}, Age Group: {self.age_group})"