from Model.Schedule import Schedule


class FIFOSchedule(Schedule):
    def __init__(self, configuration):
        self.name = 'FIFOAlgorithm'
        self.configuration = configuration
        # Adjust session_bookings to include 'young' and 'old' sub-categories for compatibility
        self.session_bookings = {
            workshop: {slot: {'young': [], 'old': []} for slot in range(3)}
            for workshop in self.configuration['workshops']
        }
        self.schedule = {}
        self.camper_slots = {}  # Track slots assigned to each camper
        self.max_slots_per_workshop = 15  # Max capacity of each session
        self.max_sessions_per_slot = 35   # Maximum number of sessions per time slot
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
        # Iterate over campers and assign based on preferences
        for camper_id, camper_data in self.configuration['campers'].items():
            preferences = camper_data['preferences']
            age_group = camper_data['age_group']
            assigned_workshops = []
            assigned_slots = set()  # Track assigned time slots to avoid duplicates
            assigned_preferences = set()  # Track assigned preferences to avoid duplicates

            # Determine the correct list to use based on camper's age group
            age_group_key = 'young' if age_group in self.young_group else 'old'

            for slot in range(3):
                # Check if the max session limit for this time slot has been reached
                if not self.can_start_new_session_in_slot(slot):
                    continue

                for preference in preferences:
                    # Ensure the preference hasn't already been assigned
                    if preference not in assigned_preferences and slot not in assigned_slots:
                        if self.can_assign(camper_id, preference, slot, age_group):
                            # Assign first available session
                            assigned_workshops.append((preference, slot))
                            self.session_bookings[preference][slot][age_group_key].append(camper_id)
                            assigned_slots.add(slot)
                            assigned_preferences.add(preference)
                            self.schedule[camper_id] = assigned_workshops
                            break  # Move to the next slot once assigned

                if len(assigned_workshops) == 3:
                    break

            # Fill in remaining slots with dashes if no valid sessions can be found
            for slot in range(3):
                if slot not in assigned_slots:
                    assigned_workshops.append(("-", slot))

            # Store the final schedule for the camper
            self.schedule[camper_id] = assigned_workshops

    # def calculate_completion_rate(self):
    #     total_campers = len(self.configuration['campers'])
    #     fully_scheduled = sum(1 for workshops in self.schedule.values() if len([w for w, _ in workshops if w != '-']) == 3)
    #     completion_rate = (fully_scheduled / total_campers) * 100
    #
    #     print(f"Completion Rate: {fully_scheduled} out of {total_campers} campers ({completion_rate:.2f}%) were fully scheduled.")
    #     return completion_rate
    #
    # def calculate_satisfaction_rate(self):
    #     satisfaction_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    #
    #     for camper_id, workshops in self.schedule.items():
    #         preferences = set(self.configuration['campers'][camper_id]['preferences'])
    #         fulfilled_count = sum(1 for workshop, _ in workshops if workshop in preferences)
    #         satisfaction_counts[fulfilled_count] += 1
    #
    #     total_campers = sum(satisfaction_counts.values())
    #
    #     print("Satisfaction Rates (FIFO):")
    #     for count, num_campers in satisfaction_counts.items():
    #         percentage = (num_campers / total_campers) * 100
    #         print(f"{num_campers} campers ({percentage:.2f}%) got {count} of their preferred workshops.")
    #
    #     return satisfaction_counts

    def __str__(self):
        schedule_str = "FIFO Schedule:\n"
        for camper_id, workshops in self.schedule.items():
            if workshops:
                schedule_str += f"Camper {camper_id}: {', '.join(f'{w} (slot {s})' for w, s in workshops)}\n"
            else:
                schedule_str += f"Camper {camper_id}: Not Assigned\n"
        return schedule_str

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

    def add_booking(self, camper_id, workshop, slot, camper_age_group):
        # Determine the correct list within the slot based on the camper's age group
        age_group_key = 'young' if camper_age_group in self.young_group else 'old'

        # Add the camper to the appropriate list in the session bookings
        self.session_bookings[workshop][slot][age_group_key].append(camper_id)

        # Track that the camper has been assigned to this slot, to prevent double-booking them in the same slot
        if camper_id not in self.camper_slots:
            self.camper_slots[camper_id] = set()
        self.camper_slots[camper_id].add(slot)