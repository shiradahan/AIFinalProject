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


#  The comparison may not be entirely fair if the GA has more flexibility in handling constraints and optimizing the schedule.
#  If FIFO doesn't account for the same level of constraint handling or optimization, it's expected that GA will perform better in most scenarios.
#  This adjusted FIFO algorithm now handles constraints more similarly to your GA.
#  This should provide a more fair comparison between the two approaches when you analyze satisfaction rates,
#  completion rates, and overall performance. Check with them if this is whats needed or can compare to the stupid fifo above.
#  Constraint Handling:  GA seems to handle constraints more robustly by trying to assign campers even when their preferences cannot be met directly.
#  This includes reassigning campers to different slots or workshops if necessary and ensuring that constraints like capacity and age group
#  compatibility are respected.FIFO: The FIFO algorithm might not handle all constraints as well, particularly because it doesn't appear to be as
#  flexible in reassigning campers when preferences can't be met.
#
# import random
#
# class FIFOSchedule:
#     def __init__(self, configuration):
#         self.configuration = configuration
#         self.session_bookings = {workshop: {slot: [] for slot in range(3)} for workshop in self.configuration['workshops']}
#         self.schedule = {}
#         self.camper_slots = {}  # Track slots assigned to each camper
#         self.max_slots_per_workshop = 15  # Max capacity of each session
#         self.max_sessions_per_slot = 35   # Maximum number of sessions per slot
#         self.young_group = {'Nanobyte', 'Kilobyte'}
#         self.older_group = {'Megabyte', 'Gigabyte'}
#         self.run_fifo_schedule()
#
#     def count_sessions_per_slot(self):
#         session_count = [0, 0, 0]  # For slot 0, 1, 2
#         for workshop, slots in self.session_bookings.items():
#             for slot, campers in slots.items():
#                 if campers:  # Count non-empty sessions
#                     session_count[slot] += 1
#         return session_count
#
#     def can_start_new_session_in_slot(self, slot):
#         session_count = self.count_sessions_per_slot()
#         return session_count[slot] < self.max_sessions_per_slot
#
#     def is_compatible_age_group(self, workshop, camper_age_group):
#         current_age_groups = {self.configuration['campers'][c]['age_group']
#                               for slot in self.session_bookings[workshop].values()
#                               for c in slot}
#
#         if not current_age_groups:
#             return True  # No campers assigned yet, so it's compatible
#
#         if camper_age_group in self.young_group:
#             return current_age_groups.issubset(self.young_group)
#         elif camper_age_group in self.older_group:
#             return current_age_groups.issubset(self.older_group)
#
#         return False
#
#     def run_fifo_schedule(self):
#         for camper_id, camper_data in self.configuration['campers'].items():
#             preferences = camper_data['preferences']
#             age_group = camper_data['age_group']
#             assigned_workshops = []
#             assigned_slots = set()  # Track assigned slots to avoid duplicates
#
#             for preference in preferences:
#                 if self.is_compatible_age_group(preference, age_group):
#                     for slot in range(3):
#                         if len(self.session_bookings[preference][slot]) < self.max_slots_per_workshop and self.can_start_new_session_in_slot(slot) and slot not in assigned_slots:
#                             assigned_workshops.append((preference, slot))
#                             self.session_bookings[preference][slot].append(camper_id)
#                             assigned_slots.add(slot)
#                             break
#                 if len(assigned_workshops) == 3:
#                     break
#
#             # If not fully scheduled, assign random available sessions
#             if len(assigned_workshops) < 3:
#                 self.assign_random_sessions(camper_id, age_group, assigned_workshops, assigned_slots)
#
#             # Fill in remaining slots with dashes
#             for slot in range(3):
#                 if slot not in assigned_slots:
#                     assigned_workshops.append(("-", slot))
#
#             self.schedule[camper_id] = assigned_workshops
#
#     def assign_random_sessions(self, camper_id, age_group, assigned_workshops, assigned_slots):
#         attempt_count = 0  # To track the number of attempts
#         while len(assigned_workshops) < 3:
#             remaining_workshops = [(w, slot) for w in self.configuration['workshops'] for slot in range(3)
#                                    if w != '-' and slot not in assigned_slots and len(self.session_bookings[w][slot]) < self.max_slots_per_workshop]
#             if remaining_workshops:
#                 selected_workshop, slot = random.choice(remaining_workshops)
#                 if self.is_compatible_age_group(selected_workshop, age_group):
#                     assigned_workshops.append((selected_workshop, slot))
#                     self.session_bookings[selected_workshop][slot].append(camper_id)
#                     assigned_slots.add(slot)
#             else:
#                 break
#
#             attempt_count += 1
#             if attempt_count > 3:  # Arbitrary limit to avoid infinite loops
#                 break
#
#     def calculate_completion_rate(self):
#         total_campers = len(self.configuration['campers'])
#         fully_scheduled = sum(1 for workshops in self.schedule.values() if len([w for w, _ in workshops if w != '-']) == 3)
#         completion_rate = (fully_scheduled / total_campers) * 100
#
#         print(f"Completion Rate: {fully_scheduled} out of {total_campers} campers ({completion_rate:.2f}%) were fully scheduled.")
#         return completion_rate
#
#     def calculate_satisfaction_rate(self):
#         satisfaction_counts = {0: 0, 1: 0, 2: 0, 3: 0}
#
#         for camper_id, workshops in self.schedule.items():
#             preferences = set(self.configuration['campers'][camper_id]['preferences'])
#             fulfilled_count = sum(1 for workshop, _ in workshops if workshop in preferences)
#             satisfaction_counts[fulfilled_count] += 1
#
#         total_campers = sum(satisfaction_counts.values())
#
#         print("Satisfaction Rates (Adjusted FIFO):")
#         for count, num_campers in satisfaction_counts.items():
#             percentage = (num_campers / total_campers) * 100
#             print(f"{num_campers} campers ({percentage:.2f}%) got {count} of their preferred workshops.")
#
#         return satisfaction_counts
#
#     def __str__(self):
#         schedule_str = "FIFO Schedule:\n"
#         for camper_id, workshops in self.schedule.items():
#             if workshops:
#                 schedule_str += f"Camper {camper_id}: {', '.join(f'{w} (slot {s})' for w, s in workshops)}\n"
#             else:
#                 schedule_str += f"Camper {camper_id}: Not Assigned\n"
#         return schedule_str
