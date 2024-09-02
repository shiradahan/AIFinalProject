from random import random
import random

class Schedule:
    def __init__(self, configuration):
        self.configuration = configuration
        self.session_bookings = {
            workshop: {slot: {'young': [], 'old': []} for slot in range(3)}
            for workshop in self.configuration['workshops']
        }
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
            for slot, age_groups in slots.items():
                # Count the slot if there are any campers in either age group for this slot
                if age_groups['young'] or age_groups['old']:
                    session_count[slot] += 1
        return session_count

    def can_start_new_session_in_slot(self, slot):
        session_count = self.count_sessions_per_slot()
        return session_count[slot] < self.max_sessions_per_slot

    def is_compatible_age_group(self, workshop, slot, camper_age_group):
        # Example structure: {workshop: {slot: {'young': [], 'old': []}}}
        age_group_sessions = self.session_bookings[workshop][slot]
        if not any(age_group_sessions.values()):  # Check if all lists under this slot are empty
            return True  # If all sub-sessions are empty, any age group can start here

        # Specific age group handling
        if camper_age_group in self.young_group and age_group_sessions['young']:
            return True  # Young campers can join if 'young' list is not empty
        if camper_age_group in self.older_group and age_group_sessions['old']:
            return True  # Old campers can join if 'old' list is not empty

        return False  # If none of the conditions are met, it's incompatible

    def can_assign(self, camper_id, workshop, slot, camper_age_group):
        # Determine which age group list to check based on camper's age group
        age_group_key = 'young' if camper_age_group in self.young_group else 'old'

        # Check for duplicate workshop assignment in the same schedule.
        if any(workshop == w for w, _ in self.schedule.get(camper_id, [])):
            return False

        # Check if the slot already has the maximum number of campers for the specific age group.
        if len(self.session_bookings[workshop][slot][age_group_key]) >= self.max_slots_per_workshop:
            return False

        # Check if the camper has already been assigned to this time slot.
        if slot in self.camper_slots.get(camper_id, set()):
            return False

        # Check age group compatibility. This assumes the session_bookings structure now supports age group separation.
        if not self.is_compatible_age_group(workshop, slot, camper_age_group):
            return False

        # Check if a new session can be started in this slot for the specific age group (i.e., does not exceed the max sessions per slot).
        if not self.session_bookings[workshop][slot][age_group_key] and not self.can_start_new_session_in_slot(slot):
            return False

        # If all conditions are met, the assignment is possible.
        return True

    def assign_with_preferences(self):
        for camper_id, camper_data in self.configuration['campers'].items():
            preferences = camper_data['preferences']
            age_group = camper_data['age_group']
            assigned_workshops = [("-", i) for i in range(3)]  # Initialize with dashes
            assigned_slots = set()

            for i in range(3):
                assigned = False
                for preference in preferences:
                    # Check if the slot is already used and if the preference can be assigned.
                    if i not in assigned_slots and self.is_compatible_age_group(preference, i, age_group):
                        if self.can_assign(camper_id, preference, i, age_group):
                            # Assign the workshop and update bookings.
                            assigned_workshops[i] = (preference, i)
                            self.add_booking(camper_id, preference, i, age_group)  # Ensure age group is considered
                            assigned_slots.add(i)
                            assigned = True
                            self.schedule[camper_id] = assigned_workshops
                            break
                # Without this break, the algorithm assigns workshops more aggressively, making the initial population more homogeneous.
                # This can cause the Genetic Algorithm to converge quickly to a high fitness score in the first generation because there's less
                # diversity for further optimization. Omer this is great for your camp but not for testing our GA!
                # Stop trying other preferences if one is successfully assigned to a slot.
                if assigned:
                    break

                # If no preference is assigned, ensure the slot is marked with a dash.
                assigned_workshops[i] = ("-", i)

            # Update the schedule with the assigned workshops.
            self.schedule[camper_id] = assigned_workshops

    def assign_with_randomized_preferences(self):
        for camper_id, camper_data in self.configuration['campers'].items():
            preferences = camper_data['preferences']
            age_group = camper_data['age_group']
            assigned_workshops = [("-", i) for i in range(3)]  # Initialize with dashes
            assigned_slots = set()

            # Randomize the order of preferences
            random.shuffle(preferences)

            for i in range(3):
                assigned = False
                for preference in preferences:
                    if i not in assigned_slots and self.can_assign(camper_id, preference, i, age_group):
                        assigned_workshops[i] = (preference, i)
                        self.add_booking(camper_id, preference, i, age_group)
                        assigned_slots.add(i)
                        assigned = True
                        self.schedule[camper_id] = assigned_workshops
                        break
                # Without this break, the algorithm assigns workshops more aggressively, making the initial population more homogeneous.
                # This can cause the Genetic Algorithm to converge quickly to a high fitness score in the first generation because there's less
                # diversity for further optimization. Omer this is great for your camp but not for testing our GA.
                # Stop trying other preferences if one is successfully assigned to a slot.
                if assigned:
                    break

                if not assigned:
                    assigned_workshops[i] = ("-", i)

            self.schedule[camper_id] = assigned_workshops

    def assign_random_workshops(self):
        workshops = list(self.configuration['workshops'])

        for camper_id, camper_data in self.configuration['campers'].items():
            age_group = camper_data['age_group']
            assigned_workshops = [("-", i) for i in range(3)]  # Initialize with dashes
            assigned_slots = set()

            for i in range(3):
                # Randomly select a workshop
                random_workshop = random.choice(workshops)

                if i not in assigned_slots and self.can_assign(camper_id, random_workshop, i, age_group):
                    assigned_workshops[i] = (random_workshop, i)
                    self.add_booking(camper_id, random_workshop, i, age_group)
                    assigned_slots.add(i)

                if not assigned_slots:
                    assigned_workshops[i] = ("-", i)

            self.schedule[camper_id] = assigned_workshops

    def assign_with_even_distribution(self):
        for camper_id, camper_data in self.configuration['campers'].items():
            preferences = camper_data['preferences']
            age_group = camper_data['age_group']
            age_group_key = 'young' if age_group in self.young_group else 'old'
            assigned_workshops = [("-", i) for i in range(3)]
            assigned_slots = set()

            for i in range(3):
                # Determine the slot with the least number of campers assigned in the same age group
                least_filled_slot = min(
                    range(3),
                    key=lambda x: sum(len(self.session_bookings[w][x][age_group_key]) for w in preferences)
                )
                for preference in preferences:
                    if i not in assigned_slots and self.can_assign(camper_id, preference, least_filled_slot, age_group):
                        assigned_workshops[least_filled_slot] = (preference, least_filled_slot)
                        self.add_booking(camper_id, preference, least_filled_slot, age_group)
                        assigned_slots.add(least_filled_slot)
                        self.schedule[camper_id] = assigned_workshops
                        break

                if assigned_workshops[i][0] == "-":
                    assigned_workshops[i] = ("-", i)

            self.schedule[camper_id] = assigned_workshops

    def add_booking(self, camper_id, workshop, slot, camper_age_group):
        # Determine the correct list within the slot based on the camper's age group
        age_group_key = 'young' if camper_age_group in self.young_group else 'old'

        # Add the camper to the appropriate list in the session bookings
        self.session_bookings[workshop][slot][age_group_key].append(camper_id)

        # Track that the camper has been assigned to this slot, to prevent double-booking them in the same slot
        if camper_id not in self.camper_slots:
            self.camper_slots[camper_id] = set()
        self.camper_slots[camper_id].add(slot)

    def ensure_valid_sessions(self, camper_id, sessions, session_bookings):
        valid_sessions = []
        assigned_workshops = set()
        camper_age_group = self.configuration['campers'][camper_id]['age_group']
        age_group_key = 'young' if camper_age_group in self.young_group else 'old'

        for workshop, slot in sessions:
            # Check for valid entry and no duplication of workshops
            if workshop != "-" and workshop not in assigned_workshops:
                # Verify if age group is compatible and if the camper can be assigned to this slot and workshop
                if self.can_assign(camper_id, workshop, slot, camper_age_group):
                    # Check if workshop and slot are valid and ensure not exceeding capacity
                    if workshop in session_bookings and slot in session_bookings[workshop]:
                        # Access the correct list based on age group
                        if len(session_bookings[workshop][slot][age_group_key]) < self.max_slots_per_workshop:
                            valid_sessions.append((workshop, slot))
                            assigned_workshops.add(workshop)
                            # Add camper to the correct age group list in session bookings if not already there
                            if camper_id not in session_bookings[workshop][slot][age_group_key]:
                                session_bookings[workshop][slot][age_group_key].append(camper_id)
                        else:
                            # If session is over capacity, append a dash
                            valid_sessions.append(("-", slot))
                    else:
                        # If there's a misconfiguration or invalid slot, append a dash
                        valid_sessions.append(("-", slot))
                else:
                    # If the camper cannot be assigned due to constraints, append a dash
                    valid_sessions.append(("-", slot))
            else:
                # If workshop is '-' or already assigned in another slot, append a dash
                valid_sessions.append(("-", slot))

        return valid_sessions

    def __str__(self):
        schedule_str = "Schedule:\n"
        for camper_id, workshops in self.schedule.items():
            schedule_str += f"Camper {camper_id}: {', '.join(f'{w} (slot {s})' for w, s in workshops)}\n"
        return schedule_str



# TO EFFECTIVE as an initial population generator
    # def assign_preferences_then_random(self):
    #     # Track session counts across slots for diversity
    #     session_distribution = {workshop: [0, 0, 0] for workshop in self.configuration['workshops']}
    #
    #     for camper_id, camper_data in self.configuration['campers'].items():
    #         preferences = camper_data['preferences']
    #         age_group = camper_data['age_group']
    #         assigned_workshops = [("-", i) for i in range(3)]  # Initialize with dashes
    #         assigned_slots = set()
    #
    #         # Randomly shuffle preferences to introduce variability
    #         random.shuffle(preferences)
    #
    #         # Step 1: Try to assign a preferred session randomly
    #         for i in range(3):
    #             for preference in preferences:
    #                 if self.can_assign(camper_id, preference, i, age_group) and \
    #                         session_distribution[preference][i] < self.max_sessions_per_slot:
    #                     assigned_workshops[i] = (preference, i)
    #                     self.add_booking(camper_id, preference, i, age_group)
    #                     assigned_slots.add(i)
    #                     session_distribution[preference][i] += 1
    #                     self.schedule[camper_id] = assigned_workshops
    #                     break  # Break after first successful assignment to ensure diversity
    #
    #         # Step 2: Fill remaining slots with any workshop, considering age compatibility but with a twist
    #         available_slots = {i for i in range(3) if assigned_workshops[i][0] == "-"}
    #         for i in available_slots:
    #             all_workshops = list(self.configuration['workshops'])
    #             random.shuffle(all_workshops)  # Shuffle to avoid favoritism and ensure diversity
    #             assigned = False
    #             for workshop in all_workshops:
    #                 if self.can_assign(camper_id, workshop, i, age_group) and \
    #                         session_distribution[workshop][i] < self.max_sessions_per_slot:
    #                     assigned_workshops[i] = (workshop, i)
    #                     self.add_booking(camper_id, workshop, i, age_group)
    #                     session_distribution[workshop][i] += 1
    #                     self.schedule[camper_id] = assigned_workshops
    #                     assigned = True
    #                     break
    #             if not assigned:
    #                 # If no suitable workshop can be assigned, maintain the dash
    #                 assigned_workshops[i] = ("-", i)
    #
    #         # Update the schedule with the assigned workshops
    #         self.schedule[camper_id] = assigned_workshops


# TO EFFECTIVE as an initial population generator
# def assign_with_even_filling(self):
#        for camper_id, camper_data in self.configuration['campers'].items():
#            preferences = camper_data['preferences']
#            age_group = camper_data['age_group']
#            assigned_workshops = [("-", i) for i in range(3)]  # Initialize with dashes
#            filled_sessions = self.get_least_filled_sessions()
#
#            # Try to assign preferences first
#            for preference in preferences:
#                for i in sorted(range(3), key=lambda x: filled_sessions.get(preference, [])[x]):
#                    if self.is_compatible_age_group(preference, i, age_group) and \
#                            self.can_assign(camper_id, preference, i, age_group):
#                        assigned_workshops[i] = (preference, i)
#                        self.add_booking(camper_id, preference, i, age_group)  # Include age group in booking
#                        break  # Stop checking this preference if assigned
#
#            # If no preferences are assigned, fill with least filled sessions
#            for i in range(3):
#                if assigned_workshops[i][0] == "-":  # Still unassigned
#                    sorted_workshops = sorted(filled_sessions.keys(), key=lambda w: min(filled_sessions[w]))
#                    for workshop in sorted_workshops:
#                        if self.is_compatible_age_group(workshop, i, age_group) and \
#                                self.can_assign(camper_id, workshop, i, age_group):
#                            assigned_workshops[i] = (workshop, i)
#                            self.add_booking(camper_id, workshop, i, age_group)
#                            break
#
#            self.schedule[camper_id] = assigned_workshops
#
#    def get_least_filled_sessions(self):
#        filled_sessions = {workshop: [0] * 3 for workshop in self.configuration['workshops']}
#        for workshop, slots in self.session_bookings.items():
#            for slot, campers in slots.items():
#                filled_sessions[workshop][slot] = len(campers)
#        return filled_sessions