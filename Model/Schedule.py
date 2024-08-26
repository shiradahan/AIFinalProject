import random

class Schedule:
    def __init__(self, configuration):
        self.configuration = configuration
        self.schedule = self.generate_initial_schedule()
        self.session_bookings = {workshop: [] for workshop in self.configuration['workshops']}  # Track which campers are booked in which sessions

    def generate_initial_schedule(self):
        schedule = {}
        for camper_id, camper_data in self.configuration['campers'].items():
            age_group = camper_data['age_group']
            preferences = camper_data['preferences']
            assigned_workshops = random.sample(preferences, 3)  # Randomly assign 3 out of 4 preferences
            schedule[camper_id] = assigned_workshops
            for workshop in assigned_workshops:
                self.session_bookings[workshop].append(camper_id)  # Track booking
        return schedule

    def fitness(self):
        score = 0
        workshop_capacities = {workshop: 0 for workshop in self.configuration['workshops']}
        age_group_matches = 0
        unique_assignments = 0

        # Check for overlaps and update fitness
        for workshop, campers in self.session_bookings.items():
            if len(campers) <= 15:  # Respect capacity constraint
                score += 1
            else:
                score -= (len(campers) - 15)  # Penalize for exceeding capacity

        # Evaluate each camper's schedule
        for camper_id, workshops in self.schedule.items():
            age_group = self.configuration['campers'][camper_id]['age_group']

            if len(set(workshops)) == len(workshops):
                unique_assignments += 1

            for workshop in workshops:
                if self.configuration['workshops'][workshop]['age_group'] == age_group:
                    age_group_matches += 1

        score += unique_assignments  # Reward unique workshop assignments
        score += age_group_matches  # Reward matching age groups

        return score

    def crossover(self, other, numberOfCrossoverPoints, crossoverProbability):
        if random.randint(0, 100) > crossoverProbability:
            return self

        child = Schedule(self.configuration)
        crossover_point = random.randint(1, len(self.schedule) - 1)
        for i, camper_id in enumerate(self.schedule):
            if i < crossover_point:
                child.schedule[camper_id] = self.schedule[camper_id]
            else:
                child.schedule[camper_id] = other.schedule[camper_id]

        # Update session bookings for the child schedule
        child.session_bookings = {workshop: [] for workshop in self.configuration['workshops']}
        for camper_id, workshops in child.schedule.items():
            for workshop in workshops:
                child.session_bookings[workshop].append(camper_id)

        return child

    def mutation(self, mutationSize, mutationProbability):
        if random.randint(0, 100) > mutationProbability:
            return

        for _ in range(mutationSize):
            camper_id = random.choice(list(self.schedule.keys()))
            workshops = self.schedule[camper_id]
            preferences = self.configuration['campers'][camper_id]['preferences']
            new_workshop = random.choice([w for w in preferences if w not in workshops])
            old_workshop_index = random.randint(0, 2)
            old_workshop = workshops[old_workshop_index]

            # Remove old workshop from bookings
            self.session_bookings[old_workshop].remove(camper_id)
            # Assign new workshop
            workshops[old_workshop_index] = new_workshop
            self.session_bookings[new_workshop].append(camper_id)

    def makeNewFromPrototype(self):
        return Schedule(self.configuration)
