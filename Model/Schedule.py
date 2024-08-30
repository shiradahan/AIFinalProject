import random


class Schedule:
    def __init__(self, configuration):
        self.configuration = configuration
        self.session_bookings = {workshop: {slot: [] for slot in range(3)} for workshop in self.configuration['workshops']}
        self.schedule = {}
        self.camper_slots = {}  # Track slots assigned to each camper
        self.max_slots_per_workshop = 15  # Max capacity of each session
        self.min_slots_per_workshop = 5   # Minimum number of campers required to hold a session
        self.max_sessions_per_slot = 35   # Maximum number of sessions per slot
        self.young_group = {'Nanobyte', 'Kilobyte'}
        self.older_group = {'Megabyte', 'Gigabyte'}
        self.generate_initial_schedule()

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

    def is_compatible_age_group(self, workshop, camper_age_group):
        current_age_groups = {self.configuration['campers'][c]['age_group']
                              for slot in self.session_bookings[workshop].values()
                              for c in slot}

        if not current_age_groups:
            return True  # No campers assigned yet, so it's compatible

        if camper_age_group in self.young_group:
            return current_age_groups.issubset(self.young_group)
        elif camper_age_group in self.older_group:
            return current_age_groups.issubset(self.older_group)

        return False

    def generate_initial_schedule(self):
        for camper_id, camper_data in self.configuration['campers'].items():
            assigned_workshops = self.assign_preferred_sessions(camper_id, camper_data)

            # Fill remaining slots if necessary
            if len(assigned_workshops) < 3:
                self.assign_random_sessions(camper_id, camper_data, assigned_workshops)

            self.schedule[camper_id] = assigned_workshops

        # Consolidate sessions with fewer than 4 campers
        self.consolidate_sessions()

    def assign_preferred_sessions(self, camper_id, camper_data):
        preferences = camper_data['preferences']
        age_group = camper_data['age_group']
        assigned_workshops = []
        assigned_slots = set()  # Track assigned slots

        for preference in preferences:
            if self.is_compatible_age_group(preference, age_group):
                for slot in range(3):
                    if self.can_assign(camper_id, preference, slot, assigned_workshops) and self.can_start_new_session_in_slot(
                            slot):
                        assigned_workshops.append((preference, slot))
                        self.add_booking(camper_id, preference, slot)
                        assigned_slots.add(slot)
                        break
            if len(assigned_workshops) == 3:  # Ensure exactly 3 unique sessions
                break

        return assigned_workshops

    def assign_random_sessions(self, camper_id, camper_data, assigned_workshops):
        age_group = camper_data['age_group']
        assigned_slots = {slot for _, slot in assigned_workshops}

        attempt_count = 0  # To track the number of attempts
        while len(assigned_workshops) < 3:
            remaining_workshops = [(w, slot) for w in self.configuration['workshops'] for slot in range(3)
                                   if self.can_assign(camper_id, w, slot, assigned_workshops) and w != '-']
            if remaining_workshops:
                selected_workshop = random.choice(remaining_workshops)
                if self.is_compatible_age_group(selected_workshop[0], age_group):
                    assigned_workshops.append(selected_workshop)
                    self.add_booking(camper_id, selected_workshop[0], selected_workshop[1])
                    assigned_slots.add(selected_workshop[1])

            attempt_count += 1
            if attempt_count > 3:  # Arbitrary limit to avoid infinite loops
                # print(f"Warning: Camper {camper_id} is stuck in assignment loop.")
                break

        # Assign any remaining sessions with compatible workshops
        if len(assigned_workshops) < 3:
            for workshop, slots in self.session_bookings.items():
                for slot in slots:
                    if self.can_assign(camper_id, workshop, slot, assigned_workshops) and self.is_compatible_age_group(workshop,
                                                                                                                       age_group):
                        assigned_workshops.append((workshop, slot))
                        self.add_booking(camper_id, workshop, slot)
                        assigned_slots.add(slot)
                        if len(assigned_workshops) == 3:
                            break
                if len(assigned_workshops) == 3:
                    break

        # Fill in any remaining slots with dashes if necessary
        for slot in range(3):
            if slot not in assigned_slots:
                assigned_workshops.append(("-", slot))

        self.schedule[camper_id] = assigned_workshops

    def can_assign(self, camper_id, workshop, slot, assigned_workshops):
        # Ensure the camper is not already assigned to the same workshop
        if any(workshop == w for w, _ in assigned_workshops):
            # print(f"Camper {camper_id} already assigned to workshop {workshop}.")
            return False
        if len(self.session_bookings[workshop][slot]) >= self.max_slots_per_workshop:
            # print(f"Workshop {workshop} slot {slot} is full for Camper {camper_id}.")
            return False
        if slot in self.camper_slots.get(camper_id, set()):
            # print(f"Camper {camper_id} already assigned to slot {slot}.")
            return False
        return True

    def add_booking(self, camper_id, workshop, slot):
        self.session_bookings[workshop][slot].append(camper_id)
        if camper_id not in self.camper_slots:
            self.camper_slots[camper_id] = set()
        self.camper_slots[camper_id].add(slot)

    def consolidate_sessions(self):
        for workshop, slots in self.session_bookings.items():
            for slot, campers in list(slots.items()):  # List to avoid modifying while iterating
                if len(campers) > 0 and len(campers) < self.min_slots_per_workshop:
                    merged = False
                    # Priority: Look for another slot with the same workshop to merge into
                    for target_slot in range(3):
                        if target_slot != slot and len(self.session_bookings[workshop][target_slot]) < self.max_slots_per_workshop:
                            combined_capacity = len(campers) + len(self.session_bookings[workshop][target_slot])
                            if combined_capacity <= self.max_slots_per_workshop:
                                conflict_free = all(target_slot not in self.camper_slots[camper_id] for camper_id in campers)
                                if conflict_free:
                                    # Move campers to the session of the same workshop in a different slot
                                    for camper_id in campers:
                                        self.schedule[camper_id] = [
                                            (ws, ts) if ws != workshop or ts != slot else (workshop, target_slot)
                                            for ws, ts in self.schedule[camper_id]
                                        ]
                                        self.camper_slots[camper_id].remove(slot)
                                        self.camper_slots[camper_id].add(target_slot)
                                        self.session_bookings[workshop][target_slot].append(camper_id)
                                    # Clear the old slot after moving
                                    slots[slot] = []
                                    merged = True
                                    break  # Move on after a successful merge

                    # If not merged, assign campers to a dash
                    if not merged:
                        for camper_id in campers:
                            self.schedule[camper_id] = [
                                (ws, ts) if ws != workshop or ts != slot else ("-", slot)
                                for ws, ts in self.schedule[camper_id]
                            ]
                            # Update camper_slots to reflect the dash assignment
                            self.camper_slots[camper_id].remove(slot)
                            self.camper_slots[camper_id].add(slot)
                        slots[slot] = []  # Clear the session as it was too small and not merged

    def __str__(self):
        schedule_str = "Schedule:\n"
        for camper_id, workshops in self.schedule.items():
            schedule_str += f"Camper {camper_id}: {', '.join(f'{w} (slot {s})' for w, s in workshops)}\n"
        return schedule_str



# ######## SUPER SIMPLE GA #############

# import random
#
# class Schedule:
#     def __init__(self, configuration):
#         self.configuration = configuration
#         self.session_bookings = {workshop: {slot: [] for slot in range(3)} for workshop in self.configuration['workshops']}
#         self.schedule = {}
#         self.camper_slots = {}  # Track slots assigned to each camper
#         self.max_slots_per_workshop = 15  # Max capacity of each session
#         self.max_sessions_per_slot = 35   # Maximum number of sessions per slot
#         self.generate_initial_schedule()
#
#     def generate_initial_schedule(self):
#         for camper_id, camper_data in self.configuration['campers'].items():
#             assigned_workshops = self.assign_random_sessions(camper_id, camper_data)
#             self.schedule[camper_id] = assigned_workshops
#
#     def assign_random_sessions(self, camper_id, camper_data):
#         assigned_workshops = []
#         assigned_slots = set()  # Track assigned slots
#
#         while len(assigned_workshops) < 3:
#             remaining_workshops = [(w, slot) for w in self.configuration['workshops'] for slot in range(3)
#                                    if self.can_assign(camper_id, w, slot, assigned_workshops)]
#             if remaining_workshops:
#                 selected_workshop = random.choice(remaining_workshops)
#                 assigned_workshops.append(selected_workshop)
#                 self.add_booking(camper_id, selected_workshop[0], selected_workshop[1])
#                 assigned_slots.add(selected_workshop[1])
#             else:
#                 break
#
#         # Fill in any remaining slots with dashes if necessary
#         for slot in range(3):
#             if slot not in assigned_slots:
#                 assigned_workshops.append(("-", slot))
#
#         return assigned_workshops
#
#     def can_assign(self, camper_id, workshop, slot, assigned_workshops):
#         # Simplified assignment: only check for capacity and slot usage
#         if len(self.session_bookings[workshop][slot]) >= self.max_slots_per_workshop:
#             return False
#         if slot in self.camper_slots.get(camper_id, set()):
#             return False
#         return True
#
#     def add_booking(self, camper_id, workshop, slot):
#         self.session_bookings[workshop][slot].append(camper_id)
#         if camper_id not in self.camper_slots:
#             self.camper_slots[camper_id] = set()
#         self.camper_slots[camper_id].add(slot)
#
#     def __str__(self):
#         schedule_str = "Schedule:\n"
#         for camper_id, workshops in self.schedule.items():
#             schedule_str += f"Camper {camper_id}: {', '.join(f'{w} (slot {s})' for w, s in workshops)}\n"
#         return schedule_str
