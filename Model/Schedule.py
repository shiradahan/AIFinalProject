from random import random
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

    def assign_with_preferences(self):
        for camper_id, camper_data in self.configuration['campers'].items():
            preferences = camper_data['preferences']
            age_group = camper_data['age_group']
            assigned_workshops = [("-", i) for i in range(3)]  # Initialize with dashes
            assigned_slots = set()

            for i in range(3):
                assigned = False
                for preference in preferences:
                    if self.is_compatible_age_group(preference, age_group):
                        if self.can_assign(camper_id, preference, i, assigned_workshops) and \
                                self.can_start_new_session_in_slot(i) and \
                                i not in assigned_slots:
                            assigned_workshops[i] = (preference, i)
                            self.add_booking(camper_id, preference, i)
                            assigned_slots.add(i)
                            assigned = True
                            break
                if not assigned:
                    # If no preference can be assigned, keep the dash
                    assigned_workshops[i] = ("-", i)

            # Update the schedule with the assigned workshops
            self.schedule[camper_id] = assigned_workshops

    def assign_with_even_filling(self):
        for camper_id, camper_data in self.configuration['campers'].items():
            available_workshops = list(self.configuration['workshops'])
            age_group = camper_data['age_group']
            assigned_workshops = [("-", i) for i in range(3)]  # Initialize with dashes
            assigned_slots = set()
            slots_to_fill = random.choice([1])  # Decide how many slots to fill

            for i in range(slots_to_fill):
                assigned = False
                random.shuffle(available_workshops)  # Shuffle to avoid bias
                for workshop in available_workshops:
                    if self.is_compatible_age_group(workshop, age_group):
                        if self.can_assign(camper_id, workshop, i, assigned_workshops) and \
                                self.can_start_new_session_in_slot(i) and \
                                i not in assigned_slots:
                            assigned_workshops[i] = (workshop, i)
                            self.add_booking(camper_id, workshop, i)
                            assigned_slots.add(i)
                            assigned = True
                            break
                if not assigned:
                    # If no workshop can be assigned, keep the dash
                    assigned_workshops[i] = ("-", i)

            # Fill any remaining slots with a dash
            for i in range(3):
                if i not in assigned_slots:
                    assigned_workshops[i] = ("-", i)

            # Update the schedule with the assigned workshops
            self.schedule[camper_id] = assigned_workshops

    def assign_preferences_then_random(self):
        for camper_id, camper_data in self.configuration['campers'].items():
            preferences = camper_data['preferences']
            age_group = camper_data['age_group']
            assigned_workshops = [("-", i) for i in range(3)]  # Initialize with dashes
            available_slots = list(range(3))  # Slots to attempt for assignment

            # First, try to assign based on preferences
            for i in range(3):
                assigned = False
                for preference in preferences:
                    if self.is_compatible_age_group(preference, age_group):
                        if self.can_assign(camper_id, preference, i, assigned_workshops) and \
                                self.can_start_new_session_in_slot(i):
                            assigned_workshops[i] = (preference, i)
                            self.add_booking(camper_id, preference, i)
                            assigned = True
                            break
                if not assigned:
                    # If no preferred session can be assigned, proceed to random assignment
                    if self.can_start_new_session_in_slot(i):
                        possible_workshops = [w for w in self.configuration['workshops'] if self.is_compatible_age_group(w, age_group)]
                        random.shuffle(possible_workshops)  # Shuffle workshops to randomize
                        for random_workshop in possible_workshops:
                            if self.can_assign(camper_id, random_workshop, i, assigned_workshops):
                                assigned_workshops[i] = (random_workshop, i)
                                self.add_booking(camper_id, random_workshop, i)
                                assigned = True
                                break
                if not assigned:
                    # If no random session could be assigned, keep the dash
                    assigned_workshops[i] = ("-", i)

            # Update the schedule with the assigned workshops
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

    def __str__(self):
        schedule_str = "Schedule:\n"
        for camper_id, workshops in self.schedule.items():
            schedule_str += f"Camper {camper_id}: {', '.join(f'{w} (slot {s})' for w, s in workshops)}\n"
        return schedule_str


