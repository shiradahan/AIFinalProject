from random import randrange, random, seed, sample
from time import time
from Model.Schedule import Schedule
import random


class GeneticAlgorithm:
    def __init__(self, configuration, numberOfChromosomes=100, replaceByGeneration=8, trackBest=5,
                 numberOfCrossoverPoints=2, mutationSize=2, crossoverProbability=80, mutationProbability=3):
        self.configuration = configuration
        self._chromosomes = [Schedule(configuration) for _ in range(numberOfChromosomes)]
        self._bestFlags = [False] * numberOfChromosomes
        self._bestChromosomes = [0] * trackBest
        self._currentBestSize = 0
        self._mutationSize = mutationSize
        self._numberOfCrossoverPoints = numberOfCrossoverPoints
        self._crossoverProbability = crossoverProbability
        self._mutationProbability = mutationProbability
        self.set_replace_by_generation(replaceByGeneration)

    @property
    def result(self):
        return self._chromosomes[self._bestChromosomes[0]]

    def set_replace_by_generation(self, value):
        numberOfChromosomes = len(self._chromosomes)
        trackBest = len(self._bestChromosomes)
        if value > numberOfChromosomes - trackBest:
            value = numberOfChromosomes - trackBest
        self._replaceByGeneration = value

    def add_to_best(self, chromosome_index):
        fitness = self.fitness(self._chromosomes[chromosome_index])
        if (self._currentBestSize == len(self._bestChromosomes) and
                self.fitness(self._chromosomes[self._bestChromosomes[-1]]) >= fitness):
            return

        # Insert chromosome in sorted order
        i = self._currentBestSize
        while i > 0 and self.fitness(self._chromosomes[self._bestChromosomes[i - 1]]) > fitness:
            if i < len(self._bestChromosomes):
                self._bestChromosomes[i] = self._bestChromosomes[i - 1]
            i -= 1

        if i < len(self._bestChromosomes):
            self._bestChromosomes[i] = chromosome_index
            self._bestFlags[chromosome_index] = True

        if self._currentBestSize < len(self._bestChromosomes):
            self._currentBestSize += 1

    def is_in_best(self, chromosome_index):
        return self._bestFlags[chromosome_index]

    def clear_best(self):
        self._bestFlags = [False] * len(self._bestFlags)
        self._currentBestSize = 0

    def initialize_population(self):
        self._chromosomes = [Schedule(self.configuration) for _ in range(len(self._chromosomes))]

    def select_parents(self):
        # Implementing tournament selection for parent selection
        return (self.tournament_selection(), self.tournament_selection())

    def tournament_selection(self, tournament_size=3):
        selected = sample(self._chromosomes, tournament_size)
        best = max(selected, key=self.fitness)
        return best

    def replace_generation(self):
        for _ in range(self._replaceByGeneration):
            parent1, parent2 = self.select_parents()
            child = self.crossover(parent1, parent2)
            self.mutation(child)
            replace_idx = randrange(len(self._chromosomes))
            while self.is_in_best(replace_idx):
                replace_idx = randrange(len(self._chromosomes))
            self._chromosomes[replace_idx] = child
            self.add_to_best(replace_idx)

    def run(self, max_generations=1000, min_fitness=0.999):
        self.clear_best()
        self.initialize_population()
        seed(round(time() * 1000))
        current_generation = 0
        repeat_count = 0
        last_best_fitness = 0.0

        while current_generation < max_generations:
            best_chromosome = self.result
            current_fitness = self.fitness(best_chromosome)

            print(f"Fitness: {current_fitness:.6f}\tGeneration: {current_generation}", end="\r")

            if current_fitness >= min_fitness:
                break

            if abs(current_fitness - last_best_fitness) <= 1e-7:
                repeat_count += 1
            else:
                repeat_count = 0

            if repeat_count > max_generations // 100:
                seed(round(time() * 1000))
                self.set_replace_by_generation(self._replaceByGeneration * 3)
                self._crossoverProbability = min(100, self._crossoverProbability + 1)
                self._mutationProbability = min(10, self._mutationProbability + 1)
                last_best_fitness = current_fitness

            self.replace_generation()
            current_generation += 1

            print(f"Best fitness: {self.fitness(self.result):.6f} after {current_generation} generations.")
        return self.result

    def fitness(self, schedule):
        score = 0
        unique_assignments = 0
        for workshop, slots in schedule.session_bookings.items():
            for slot, campers in slots.items():
                if len(campers) <= schedule.max_slots_per_workshop and len(campers) >= schedule.min_slots_per_workshop:
                    score += 1
                else:
                    score -= (len(campers) - schedule.max_slots_per_workshop)  # Penalize for exceeding capacity
                age_groups = {schedule.configuration['campers'][c]['age_group'] for c in campers}
                if len(age_groups) == 1:
                    score += 1
                else:
                    score -= 2  # Penalize for age group mismatches
        for camper_id, workshops in schedule.schedule.items():
            if len(set([w for w, _ in workshops])) == len(workshops):
                unique_assignments += 1
        score += unique_assignments
        return score

    def crossover(self, parent1, parent2):
        if random() * 100 > self._crossoverProbability:
            return parent1

        child = Schedule(self.configuration)
        crossover_points = sorted(random.sample(range(len(parent1.schedule)), self._numberOfCrossoverPoints))

        current_point = 0
        use_parent1 = True
        assigned_slots = set()  # Track slots already assigned to ensure no duplicates

        for i, camper_id in enumerate(parent1.schedule):
            if current_point < len(crossover_points) and i == crossover_points[current_point]:
                use_parent1 = not use_parent1
                current_point += 1

            if use_parent1:
                schedule_to_use = parent1.schedule[camper_id]
            else:
                schedule_to_use = parent2.schedule[camper_id] if camper_id in parent2.schedule else []

            for workshop, s in schedule_to_use:
                if s not in assigned_slots:
                    child.schedule[camper_id].append((workshop, s))
                    child.session_bookings[workshop][s].append(camper_id)
                    assigned_slots.add(s)

            # If less than 3 unique slots are assigned, fill with dashes
            while len(child.schedule[camper_id]) < 3:
                next_slot = len(child.schedule[camper_id])
                child.schedule[camper_id].append(("-", next_slot))
                assigned_slots.add(next_slot)

        return child

    def mutation(self, schedule):
        if random() * 100 > self._mutationProbability:
            return

        for _ in range(self._mutationSize):
            camper_id = random.choice(list(schedule.schedule.keys()))
            workshops = schedule.schedule[camper_id]
            preferences = schedule.configuration['campers'][camper_id]['preferences']
            camper_age_group = schedule.configuration['campers'][camper_id]['age_group']

            # Track slots already assigned to ensure no duplicates
            assigned_slots = {slot for _, slot in workshops}

            valid_workshops = [(w, s) for w in preferences for s in range(3)
                               if schedule.can_assign(camper_id, w, s, workshops) and
                               schedule.is_compatible_age_group(w, camper_age_group) and
                               s not in assigned_slots]

            if not valid_workshops:
                continue

            new_workshop = random.choice(valid_workshops)
            old_workshop_index = random.randint(0, len(workshops) - 1)
            old_workshop = workshops[old_workshop_index]
            old_workshop_name = old_workshop[0]
            old_workshop_slot = old_workshop[1]

            # Update session bookings
            schedule.session_bookings[old_workshop_name][old_workshop_slot].remove(camper_id)
            if not schedule.session_bookings[old_workshop_name][old_workshop_slot]:
                schedule.session_bookings[old_workshop_name].pop(old_workshop_slot)

            schedule.session_bookings[new_workshop[0]][new_workshop[1]].append(camper_id)

            # Update camper schedule and slots
            schedule.schedule[camper_id][old_workshop_index] = new_workshop
            schedule.camper_slots[camper_id].remove(old_workshop_slot)
            schedule.camper_slots[camper_id].add(new_workshop[1])

            # Ensure the camper has 3 unique slots
            unique_slots = len(set(slot for _, slot in schedule.schedule[camper_id]))
            if unique_slots < 3:
                # Fill remaining slots with dashes if necessary
                for i in range(3):
                    if i not in {slot for _, slot in schedule.schedule[camper_id]}:
                        schedule.schedule[camper_id].append(("-", i))

    def calculate_satisfaction_rate(self, schedule):
        satisfaction_counts = {0: 0, 1: 0, 2: 0, 3: 0}

        for camper_id, workshops in schedule.schedule.items():
            preferences = set(schedule.configuration['campers'][camper_id]['preferences'])
            fulfilled_count = sum(1 for workshop, _ in workshops if workshop in preferences)
            satisfaction_counts[fulfilled_count] += 1

        total_campers = sum(satisfaction_counts.values())

        print("Satisfaction Rates:")
        for count, num_campers in satisfaction_counts.items():
            percentage = (num_campers / total_campers) * 100
            print(f"{num_campers} campers ({percentage:.2f}%) got {count} of their preferred workshops.")
        print()
        return satisfaction_counts

    def calculate_completion_rate(self, schedule):
        total_campers = len(schedule.schedule)
        fully_scheduled = 0

        for workshops in schedule.schedule.values():
            if all(workshop != '-' for workshop, _ in workshops):
                fully_scheduled += 1

        completion_rate = (fully_scheduled / total_campers) * 100

        print(f"Completion Rate:\n{fully_scheduled} out of {total_campers} campers ({completion_rate:.2f}%) were fully scheduled.")
        return completion_rate
