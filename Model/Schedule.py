import random

class Schedule:
    def __init__(self, configuration):
        self.configuration = configuration
        self.session_bookings = {workshop: {slot: [] for slot in range(3)} for workshop in self.configuration['workshops']}
        self.schedule = {}
        self.camper_slots = {}  # Track slots assigned to each camper
        self.max_slots_per_workshop = 15  # Max capacity of each session
        self.generate_initial_schedule()

    def generate_initial_schedule(self):
        unscheduled_campers = []

        for camper_id, camper_data in self.configuration['campers'].items():
            preferences = camper_data['preferences']
            age_group = camper_data['age_group']
            assigned_workshops = []

            # Attempt to assign preferred sessions first
            for preference in preferences:
                if self.is_compatible_age_group(preference, age_group):
                    for slot in range(3):
                        if len(self.session_bookings[preference][slot]) < 15 and slot not in self.camper_slots.get(camper_id, []):
                            if not any(preference == w for w, _ in assigned_workshops):
                                assigned_workshops.append((preference, slot))
                                self.session_bookings[preference][slot].append(camper_id)
                                if camper_id not in self.camper_slots:
                                    self.camper_slots[camper_id] = set()
                                self.camper_slots[camper_id].add(slot)
                                break
                    if len(assigned_workshops) == 3:  # Ensure exactly 3 sessions
                        break

            # Fill remaining slots if necessary
            while len(assigned_workshops) < 3:  # Ensure exactly 3 sessions
                remaining_workshops = [(w, slot) for w in self.configuration['workshops'] for slot in range(3) if
                                       (w, slot) not in assigned_workshops and
                                       len(self.session_bookings[w][slot]) < 15 and
                                       self.is_compatible_age_group(w, age_group) and
                                       slot not in self.camper_slots.get(camper_id, [])]
                if remaining_workshops:
                    selected_workshop = random.choice(remaining_workshops)
                    assigned_workshops.append(selected_workshop)
                    self.session_bookings[selected_workshop[0]][selected_workshop[1]].append(camper_id)
                    if camper_id not in self.camper_slots:
                        self.camper_slots[camper_id] = set()
                    self.camper_slots[camper_id].add(selected_workshop[1])
                else:
                    break

            if len(assigned_workshops) < 3:
                unscheduled_campers.append(camper_id)

            self.schedule[camper_id] = assigned_workshops

        # Attempt to reassign unscheduled campers
        for camper_id in unscheduled_campers:
            camper_data = self.configuration['campers'][camper_id]
            self.assign_to_available_sessions(camper_id, camper_data)

    def assign_to_available_sessions(self, camper_id, camper_data):
        age_group = camper_data['age_group']
        preferences = camper_data['preferences']
        assigned_workshops = self.schedule.get(camper_id, [])

        while len(assigned_workshops) < 3:  # Ensure exactly 3 sessions
            remaining_workshops = [(w, slot) for w in self.configuration['workshops'] for slot in range(3) if
                                   (w, slot) not in assigned_workshops and
                                   len(self.session_bookings.get(w, {}).get(slot, [])) < 15 and
                                   self.is_compatible_age_group(w, age_group) and
                                   slot not in self.camper_slots.get(camper_id, [])]
            if remaining_workshops:
                selected_workshop = random.choice(remaining_workshops)
                assigned_workshops.append(selected_workshop)
                self.session_bookings[selected_workshop[0]][selected_workshop[1]].append(camper_id)
                if camper_id not in self.camper_slots:
                    self.camper_slots[camper_id] = set()
                self.camper_slots[camper_id].add(selected_workshop[1])
            else:
                break

        self.schedule[camper_id] = assigned_workshops

    def assign_to_alternative_sessions(self, camper_id, camper_data):
        age_group = camper_data['age_group']
        preferences = camper_data['preferences']
        assigned_workshops = self.schedule.get(camper_id, [])

        while len(assigned_workshops) < 3:  # Ensure exactly 3 sessions
            remaining_workshops = [(w, slot) for w in self.configuration['workshops'] for slot in range(3) if
                                   (w, slot) not in assigned_workshops and
                                   len(self.session_bookings.get(w, {}).get(slot, [])) < self.max_slots_per_workshop and
                                   self.is_compatible_age_group(w, age_group) and
                                   slot not in self.camper_slots.get(camper_id, [])]
            if not remaining_workshops:
                # If no valid workshops, create a new slot for the workshop
                self.add_new_session_slot()
                remaining_workshops = [(w, slot) for w in self.configuration['workshops'] for slot in range(3) if
                                       (w, slot) not in assigned_workshops and
                                       len(self.session_bookings.get(w, {}).get(slot, [])) < self.max_slots_per_workshop and
                                       self.is_compatible_age_group(w, age_group) and
                                       slot not in self.camper_slots.get(camper_id, [])]
            if remaining_workshops:
                selected_workshop = random.choice(remaining_workshops)
                assigned_workshops.append(selected_workshop)
                self.session_bookings[selected_workshop[0]][selected_workshop[1]].append(camper_id)
                if camper_id not in self.camper_slots:
                    self.camper_slots[camper_id] = set()
                self.camper_slots[camper_id].add(selected_workshop[1])
            else:
                break

        # Ensure exactly 3 sessions
        if len(assigned_workshops) < 3:
            for _ in range(3 - len(assigned_workshops)):
                remaining_workshops = [(w, slot) for w in self.configuration['workshops'] for slot in range(3) if
                                       len(self.session_bookings[w][slot]) < self.max_slots_per_workshop and
                                       self.is_compatible_age_group(w, age_group) and
                                       slot not in self.camper_slots.get(camper_id, [])]
                if not remaining_workshops:
                    # If no valid workshops, create a new slot for the workshop
                    self.add_new_session_slot()
                    remaining_workshops = [(w, slot) for w in self.configuration['workshops'] for slot in range(3) if
                                           len(self.session_bookings[w][slot]) < self.max_slots_per_workshop and
                                           self.is_compatible_age_group(w, age_group) and
                                           slot not in self.camper_slots.get(camper_id, [])]
                if remaining_workshops:
                    selected_workshop = random.choice(remaining_workshops)
                    assigned_workshops.append(selected_workshop)
                    self.session_bookings[selected_workshop[0]][selected_workshop[1]].append(camper_id)
                    if camper_id not in self.camper_slots:
                        self.camper_slots[camper_id] = set()
                    self.camper_slots[camper_id].add(selected_workshop[1])
                else:
                    break

        self.schedule[camper_id] = assigned_workshops

    def is_compatible_age_group(self, workshop, camper_age_group):
        current_age_groups = {self.configuration['campers'][c]['age_group'] for slot in self.session_bookings[workshop].values() for c in slot}
        if not current_age_groups:
            return True
        for group in current_age_groups:
            if not self.are_adjacent_or_same_age_groups(group, camper_age_group):
                return False
        return True

    def are_adjacent_or_same_age_groups(self, group1, group2):
        adjacent_pairs = [('Nanobyte', 'Kilobyte'), ('Kilobyte', 'Megabyte'), ('Megabyte', 'Gigabyte')]
        return group1 == group2 or (group1, group2) in adjacent_pairs or (group2, group1) in adjacent_pairs

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
                if len(age_groups) == 1 or self.are_all_groups_adjacent(age_groups):
                    score += 1
                else:
                    score -= 2  # Penalize for age group mismatches
        for camper_id, workshops in self.schedule.items():
            if len(set([w for w, _ in workshops])) == len(workshops):
                unique_assignments += 1
        score += unique_assignments
        return score

    def are_all_groups_adjacent(self, age_groups):
        if len(age_groups) <= 1:
            return True
        age_groups = list(age_groups)
        for i in range(len(age_groups) - 1):
            if not self.are_adjacent_or_same_age_groups(age_groups[i], age_groups[i + 1]):
                return False
        return True

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
                               (w, slot) not in workshops and
                               len(self.session_bookings.get(w, {}).get(slot, [])) < self.max_slots_per_workshop and
                               self.is_compatible_age_group(w, camper_age_group) and
                               slot not in self.camper_slots.get(camper_id, [])]
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
            if camper_id not in self.camper_slots:
                self.camper_slots[camper_id] = set()
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
