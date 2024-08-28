class FIFOSchedule:
    def __init__(self, configuration):
        self.configuration = configuration
        self.session_bookings = {workshop: {slot: [] for slot in range(3)} for workshop in self.configuration['workshops']}
        self.schedule = {}
        self.camper_slots = {}  # Track slots assigned to each camper
        self.max_slots_per_workshop = 15  # Max capacity of each session
        self.max_sessions_per_slot = 35   # Maximum number of sessions per slot
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
            assigned_slots = set()  # Track assigned slots to avoid duplicates

            for preference in preferences:
                for slot in range(3):
                    if len(self.session_bookings[preference][slot]) < self.max_slots_per_workshop and self.can_start_new_session_in_slot(slot) and slot not in assigned_slots:
                        assigned_workshops.append((preference, slot))
                        self.session_bookings[preference][slot].append(camper_id)
                        assigned_slots.add(slot)
                        break
                if len(assigned_workshops) == 3:
                    break

            # Fill in remaining slots with dashes
            for slot in range(3):
                if slot not in assigned_slots:
                    assigned_workshops.append(("-", slot))

            self.schedule[camper_id] = assigned_workshops

    def calculate_completion_rate(self):
        total_campers = len(self.configuration['campers'])
        fully_scheduled = sum(1 for workshops in self.schedule.values() if len([w for w, _ in workshops if w != '-']) == 3)
        completion_rate = (fully_scheduled / total_campers) * 100

        print(f"Completion Rate: {fully_scheduled} out of {total_campers} campers ({completion_rate:.2f}%) were fully scheduled.")
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
