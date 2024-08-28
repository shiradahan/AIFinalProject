class FIFOSchedule:
    def __init__(self, configuration):
        self.configuration = configuration
        self.session_bookings = {workshop: {slot: [] for slot in range(3)} for workshop in self.configuration['workshops']}
        self.schedule = {}
        self.camper_slots = {}  # Track slots assigned to each camper
        self.max_slots_per_workshop = 15  # Max capacity of each session
        self.max_sessions_per_slot = 30   # Maximum number of sessions per slot
        self.unassigned_campers = []  # List to track unassigned campers
        self.run_fifo_schedule()

    def count_sessions_per_slot(self):
        session_count = [0, 0, 0]  # For slot 0, 1, 2
        for workshop, slots in self.session_bookings.items():
            for slot, campers in slots.items():
                if campers:  # Count non-empty sessions
                    session_count[slot] += 1
        return session_count

    def can_start_new_session_in_slot(self, slot):
        session_count = self.count_sessions_per_slot()
        return session_count[slot] < self.max_sessions_per_slot

    def run_fifo_schedule(self):
        for camper_id, camper_data in self.configuration['campers'].items():
            preferences = camper_data['preferences']
            assigned_workshops = []
            assigned = False

            for preference in preferences:
                for slot in range(3):
                    if len(self.session_bookings[preference][slot]) < self.max_slots_per_workshop and self.can_start_new_session_in_slot(slot):
                        assigned_workshops.append((preference, slot))
                        self.session_bookings[preference][slot].append(camper_id)
                        assigned = True
                        break
                if assigned and len(assigned_workshops) == 3:
                    break

            if len(assigned_workshops) < 3:
                self.unassigned_campers.append(camper_id)

            self.schedule[camper_id] = assigned_workshops

    def calculate_completion_rate(self):
        total_campers = len(self.configuration['campers'])
        unassigned_count = len(self.unassigned_campers)
        completion_rate = (total_campers - unassigned_count) / total_campers * 100

        print(f"Completion Rate: {completion_rate:.2f}%")
        print(f"Unassigned Campers: {unassigned_count}/{total_campers}")
        return completion_rate

    def calculate_satisfaction_rate(self):
        satisfaction_counts = {0: 0, 1: 0, 2: 0, 3: 0}

        for camper_id, workshops in self.schedule.items():
            preferences = set(self.configuration['campers'][camper_id]['preferences'])
            fulfilled_count = sum(1 for workshop, _ in workshops if workshop in preferences)
            satisfaction_counts[fulfilled_count] += 1

        total_campers = sum(satisfaction_counts.values())

        print("Satisfaction Rates (Adjusted FIFO):")
        for count, num_campers in satisfaction_counts.items():
            percentage = (num_campers / total_campers) * 100
            print(f"{num_campers} campers ({percentage:.2f}%) got {count} of their preferred workshops.")

        return satisfaction_counts

    def __str__(self):
        schedule_str = "FIFO Schedule:\n"
        for camper_id, workshops in self.schedule.items():
            if workshops:
                schedule_str += f"Camper {camper_id}: {', '.join(f'{w} (slot {s})' for w, s in workshops)}\n"
            else:
                schedule_str += f"Camper {camper_id}: Not Assigned\n"
        return schedule_str
