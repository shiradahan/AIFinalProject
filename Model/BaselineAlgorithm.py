class FIFOSchedule:
    def __init__(self, configuration):
        self.configuration = configuration
        # Adjust session_bookings to include 'young' and 'old' sub-categories for compatibility
        self.session_bookings = {
            workshop: {slot: {'young': [], 'old': []} for slot in range(3)}
            for workshop in self.configuration['workshops']
        }
        self.schedule = {}
        self.camper_slots = {}  # Track slots assigned to each camper
        self.max_slots_per_workshop = 15  # Max capacity of each session
        self.max_sessions_per_slot = 35   # Maximum number of sessions per slot
        self.unassigned_campers = []  # List to track unassigned campers
        self.young_group = {'Nanobyte', 'Kilobyte'}
        self.older_group = {'Megabyte', 'Gigabyte'}
        self.run_fifo_schedule()

    def count_sessions_per_slot(self):
        session_count = [0, 0, 0]  # For slot 0, 1, 2
        for workshop, slots in self.session_bookings.items():
            for slot, age_groups in slots.items():
                # Count the slot if there are any campers in either age group for this slot
                if age_groups['young'] or age_groups['old']:
                    session_count[slot] += 1
        return session_count

    def can_start_new_session_in_slot(self, slot):
        session_count = self.count_sessions_per_slot()
        return session_count[slot] < self.max_sessions_per_slot

    def run_fifo_schedule(self):
        for camper_id, camper_data in self.configuration['campers'].items():
            preferences = camper_data['preferences']
            age_group = camper_data['age_group']
            assigned_workshops = []
            assigned_slots = set()  # Track assigned slots to avoid duplicates

            # Determine the correct list to use based on camper's age group
            age_group_key = 'young' if age_group in self.young_group else 'old'

            for preference in preferences:
                for slot in range(3):
                    if len(self.session_bookings[preference][slot][age_group_key]) < self.max_slots_per_workshop and self.can_start_new_session_in_slot(slot) and slot not in assigned_slots:
                        assigned_workshops.append((preference, slot))
                        self.session_bookings[preference][slot][age_group_key].append(camper_id)
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

        print("Satisfaction Rates (FIFO):")
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
