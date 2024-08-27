import random

class Schedule:
    def __init__(self, configuration):
        self.configuration = configuration
        self.session_bookings = {workshop: {slot: [] for slot in range(3)} for workshop in self.configuration['workshops']}
        self.schedule = {}
        self.camper_slots = {}  # Track slots assigned to each camper
        self.max_slots_per_workshop = 15  # Max capacity of each session
        self.young_group = {'Nanobyte', 'Kilobyte'}
        self.older_group = {'Megabyte', 'Gigabyte'}
        self.generate_initial_schedule()
        self.consolidate_sessions()  # Consolidate sessions after generating the initial schedule


    def consolidate_sessions(self):
        """Consolidate sessions within the same age group where possible."""
        for workshop, slots in self.session_bookings.items():
            young_sessions = {slot: campers for slot, campers in slots.items() if self.is_young_group(campers)}
            old_sessions = {slot: campers for slot, campers in slots.items() if not self.is_young_group(campers)}

            # Consolidate sessions for young group
            self.consolidate_group_sessions(workshop, young_sessions)

            # Consolidate sessions for older group
            self.consolidate_group_sessions(workshop, old_sessions)

    def consolidate_group_sessions(self, workshop, sessions):
        """Consolidate sessions for a particular group if capacity allows."""
        if not sessions:  # Check if sessions is empty
            return  # If no sessions to consolidate, return early

        total_campers = sum(len(campers) for campers in sessions.values())
        if total_campers <= self.max_slots_per_workshop:
            # Move all campers to the earliest session and clear the others
            target_slot = min(sessions.keys())
            self.session_bookings[workshop][target_slot] = [camper for campers in sessions.values() for camper in campers]
            for slot in sessions:
                if slot != target_slot:
                    self.session_bookings[workshop][slot] = []

    def is_young_group(self, campers):
        """Determine if all campers in a session are in the young group."""
        return all(self.configuration['campers'][camper]['age_group'] in self.young_group for camper in campers)

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

    def same_age_group_or_category(self, group1, group2):
        if group1 == group2:
            return True
        return (group1 in self.young_group and group2 in self.young_group) or (group1 in self.older_group and group2 in self.older_group)

    def generate_initial_schedule(self):
        unscheduled_campers = []

        for camper_id, camper_data in self.configuration['campers'].items():
            assigned_workshops = self.assign_preferred_sessions(camper_id, camper_data)

            # Fill remaining slots if necessary
            if len(assigned_workshops) < 3:
                self.assign_random_sessions(camper_id, camper_data, assigned_workshops)

            if len(assigned_workshops) < 3:
                unscheduled_campers.append(camper_id)

            self.schedule[camper_id] = assigned_workshops

        # Attempt to reassign unscheduled campers
        for camper_id in unscheduled_campers:
            camper_data = self.configuration['campers'][camper_id]
            self.assign_random_sessions(camper_id, camper_data, self.schedule[camper_id])

    def assign_preferred_sessions(self, camper_id, camper_data):
        preferences = camper_data['preferences']
        age_group = camper_data['age_group']
        assigned_workshops = []

        for preference in preferences:
            if self.is_compatible_age_group(preference, age_group):
                for slot in range(3):
                    if self.can_assign(camper_id, preference, slot, assigned_workshops):
                        assigned_workshops.append((preference, slot))
                        self.add_booking(camper_id, preference, slot)
                        break
            if len(assigned_workshops) == 3:  # Ensure exactly 3 unique sessions
                break

        return assigned_workshops

    def assign_random_sessions(self, camper_id, camper_data, assigned_workshops):
        age_group = camper_data['age_group']

        while len(assigned_workshops) < 3:
            remaining_workshops = [(w, slot) for w in self.configuration['workshops'] for slot in range(3)
                                   if self.can_assign(camper_id, w, slot, assigned_workshops) and w != '-']
            if remaining_workshops:
                selected_workshop = random.choice(remaining_workshops)
                if self.is_compatible_age_group(selected_workshop[0], age_group):
                    assigned_workshops.append(selected_workshop)
                    self.add_booking(camper_id, selected_workshop[0], selected_workshop[1])
            else:
                break

        # Assign any remaining sessions with compatible workshops
        while len(assigned_workshops) < 3:
            for workshop, slots in self.session_bookings.items():
                for slot in slots:
                    if self.can_assign(camper_id, workshop, slot, assigned_workshops) and self.is_compatible_age_group(workshop, age_group):
                        assigned_workshops.append((workshop, slot))
                        self.add_booking(camper_id, workshop, slot)
                        break
                if len(assigned_workshops) == 3:
                    break

        self.schedule[camper_id] = assigned_workshops

    def can_assign(self, camper_id, workshop, slot, assigned_workshops):
        # Ensure the camper is not already assigned to the same workshop
        if any(workshop == w for w, _ in assigned_workshops):
            return False
        if len(self.session_bookings[workshop][slot]) >= self.max_slots_per_workshop:
            return False
        if slot in self.camper_slots.get(camper_id, set()):
            return False
        return True

    def add_booking(self, camper_id, workshop, slot):
        self.session_bookings[workshop][slot].append(camper_id)
        if camper_id not in self.camper_slots:
            self.camper_slots[camper_id] = set()
        self.camper_slots[camper_id].add(slot)

    def assign_to_alternative_sessions(self, camper_id, camper_data):
        age_group = camper_data['age_group']
        assigned_workshops = self.schedule.get(camper_id, [])

        while len(assigned_workshops) < 3:  # Ensure exactly 3 sessions
            remaining_workshops = [(w, slot) for w in self.configuration['workshops'] for slot in range(3) if
                                   self.can_assign(camper_id, w, slot, assigned_workshops) and
                                   self.is_compatible_age_group(w, age_group)]
            if not remaining_workshops:
                # If no valid workshops, create a new slot for the workshop
                self.add_new_session_slot()
                remaining_workshops = [(w, slot) for w in self.configuration['workshops'] for slot in range(3) if
                                       self.can_assign(camper_id, w, slot, assigned_workshops) and
                                       self.is_compatible_age_group(w, age_group)]
            if remaining_workshops:
                selected_workshop = random.choice(remaining_workshops)
                assigned_workshops.append(selected_workshop)
                self.add_booking(camper_id, selected_workshop[0], selected_workshop[1])
            else:
                break

        self.schedule[camper_id] = assigned_workshops

    def add_new_session_slot(self):
        # Add a new slot to each workshop to handle overflow
        for workshop in self.configuration['workshops']:
            next_slot = len(self.session_bookings[workshop])
            self.session_bookings[workshop][next_slot] = []
        print("Added new slots to workshops.")

    def fitness(self):
        score = 0
        unique_assignments = 0
        for workshop, slots in self.session_bookings.items():
            for slot, campers in slots.items():
                if len(campers) <= self.max_slots_per_workshop:
                    score += 1
                else:
                    score -= (len(campers) - self.max_slots_per_workshop)  # Penalize for exceeding capacity
                age_groups = {self.configuration['campers'][c]['age_group'] for c in campers}
                if len(age_groups) == 1:
                    score += 1
                else:
                    score -= 2  # Penalize for age group mismatches
        for camper_id, workshops in self.schedule.items():
            if len(set([w for w, _ in workshops])) == len(workshops):
                unique_assignments += 1
        score += unique_assignments
        return score

    def crossover(self, other, numberOfCrossoverPoints, crossoverProbability):
        if random.randint(0, 100) > crossoverProbability:
            return self

        child = Schedule(self.configuration)
        crossover_points = sorted(random.sample(range(len(self.schedule)), numberOfCrossoverPoints))

        current_point = 0
        use_self = True
        for i, camper_id in enumerate(self.schedule):
            if current_point < len(crossover_points) and i == crossover_points[current_point]:
                use_self = not use_self
                current_point += 1

            if use_self:
                child.schedule[camper_id] = self.schedule[camper_id]
            else:
                if camper_id in other.schedule:
                    child.schedule[camper_id] = other.schedule[camper_id]
                else:
                    child.schedule[camper_id] = []

        child.session_bookings = {workshop: {slot: [] for slot in range(3)} for workshop in self.configuration['workshops']}
        for camper_id, workshops in child.schedule.items():
            for workshop, slot in workshops:
                child.session_bookings[workshop][slot].append(camper_id)

        return child

    def mutation(self, mutationSize, mutationProbability):
        if random.randint(0, 100) > mutationProbability:
            return

        for _ in range(mutationSize):
            camper_id = random.choice(list(self.schedule.keys()))
            workshops = self.schedule[camper_id]
            preferences = self.configuration['campers'][camper_id]['preferences']
            camper_age_group = self.configuration['campers'][camper_id]['age_group']

            valid_workshops = [(w, slot) for w in preferences for slot in range(3) if
                               self.can_assign(camper_id, w, slot, workshops) and
                               self.is_compatible_age_group(w, camper_age_group)]
            if not valid_workshops:
                continue

            new_workshop = random.choice(valid_workshops)
            old_workshop_index = random.randint(0, len(workshops) - 1)
            old_workshop = workshops[old_workshop_index]
            old_workshop_name = old_workshop[0]
            old_workshop_slot = old_workshop[1]

            # Update session bookings
            self.session_bookings[old_workshop_name][old_workshop_slot].remove(camper_id)
            if not self.session_bookings[old_workshop_name][old_workshop_slot]:
                self.session_bookings[old_workshop_name].pop(old_workshop_slot)

            self.session_bookings[new_workshop[0]][new_workshop[1]].append(camper_id)

            # Update camper schedule and slots
            self.schedule[camper_id][old_workshop_index] = new_workshop
            self.camper_slots[camper_id].remove(old_workshop_slot)
            self.camper_slots[camper_id].add(new_workshop[1])

            # Fix slot assignments
            self.schedule[camper_id] = sorted(self.schedule[camper_id], key=lambda x: x[1])

    def makeNewFromPrototype(self):
        return Schedule(self.configuration)

    def __str__(self):
        schedule_str = "Schedule:\n"
        for camper_id, workshops in self.schedule.items():
            schedule_str += f"Camper {camper_id}: {', '.join(f'{w} (slot {s})' for w, s in workshops)}\n"
        return schedule_str

