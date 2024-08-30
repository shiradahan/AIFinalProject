import random

from Model.Schedule import Schedule


class GeneticAlgorithm:
    def __init__(self, configuration, population_size=100, generations=1000, crossover_rate=0.8, mutation_rate=0.2):
        self.configuration = configuration
        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.population = self.initialize_population()
        self.best_schedule = None

    def initialize_population(self):
        print("Initializing population with diverse strategies...")
        population = []
        strategies = ["preferences", "even_filling", "preferences+random"]

        for i in range(self.population_size):
            schedule = Schedule(self.configuration)
            strategy = strategies[i % len(strategies)]

            # Call the strategy method directly
            if strategy == "preferences":
                schedule.assign_with_preferences()
            elif strategy == "even_filling":
                schedule.assign_with_even_filling()
            elif strategy == "preferences+random":
                schedule.assign_preferences_then_random()

            population.append(schedule)

        print(f"Initialized diverse population with {self.population_size} schedules.")
        return population

    def fitness(self, schedule):
        fitness_score = 0
        total_campers = 300
        fully_scheduled = 0
        satisfaction_score = 0

        for camper_id, workshops in schedule.schedule.items():
            satisfied = sum(1 for workshop, _ in workshops if workshop != "-")
            if satisfied == 3:
                fully_scheduled += 1
            satisfaction_score += satisfied

            for workshop, slot in workshops:
                if workshop != "-":
                    # Penalize for exceeding max capacity
                    if len(schedule.session_bookings[workshop][slot]) > schedule.max_slots_per_workshop:
                        fitness_score -= 5
                    # Penalize for mixed age groups
                    if not schedule.is_compatible_age_group(workshop, self.configuration['campers'][camper_id]['age_group']):
                        fitness_score -= 10
                    # Penalize if more than 35 sessions per slot
                    if schedule.count_sessions_per_slot()[slot] > schedule.max_sessions_per_slot:
                        fitness_score -= 5

        # High reward for completion rate
        completion_rate = fully_scheduled / total_campers
        fitness_score += completion_rate * 100  # Adjust this weight to prioritize completion

        # High reward for satisfaction rate
        satisfaction_rate = satisfaction_score / (total_campers * 3)  # Max satisfaction score is 3 per camper
        fitness_score += satisfaction_rate * 100  # Adjust this weight to prioritize satisfaction

        return fitness_score

    def selection(self, population, fitness_scores):
        selected = []
        for _ in range(len(population)):
            participants = random.sample(list(zip(population, fitness_scores)), k=3)
            winner = max(participants, key=lambda x: x[1])
            selected.append(winner[0])
        return selected

    def crossover(self, parent1, parent2):
        child1, child2 = Schedule(self.configuration), Schedule(self.configuration)
        crossover_points = sorted(random.sample(range(1, 3), 2))  # Two crossover points within the three slots

        for camper_id in parent1.schedule:
            # Copy segments from parent1 to child1, parent2 to child2
            child1_sessions = parent1.schedule[camper_id][:crossover_points[0]] + \
                              parent2.schedule[camper_id][crossover_points[0]:crossover_points[1]] + \
                              parent1.schedule[camper_id][crossover_points[1]:]

            child2_sessions = parent2.schedule[camper_id][:crossover_points[0]] + \
                              parent1.schedule[camper_id][crossover_points[0]:crossover_points[1]] + \
                              parent2.schedule[camper_id][crossover_points[1]:]

            # Ensure no overlap and maintain constraints
            child1.schedule[camper_id] = self.ensure_valid_sessions(child1_sessions)
            child2.schedule[camper_id] = self.ensure_valid_sessions(child2_sessions)

        return child1, child2

    def ensure_valid_sessions(self, sessions):
        # Ensure no duplicate workshops and replace any conflicts with a dash
        valid_sessions = []
        assigned_workshops = set()
        for workshop, slot in sessions:
            if workshop != "-" and workshop not in assigned_workshops:
                valid_sessions.append((workshop, slot))
                assigned_workshops.add(workshop)
            else:
                valid_sessions.append(("-", slot))  # Replace conflicts with a dash
        return valid_sessions

    def mutation(self, individual):
        if random.random() < self.mutation_rate:
            camper_id = random.choice(list(individual.schedule.keys()))
            preferences = self.configuration['campers'][camper_id]['preferences']
            slot_to_mutate = random.choice(range(3))

            current_workshop = individual.schedule[camper_id][slot_to_mutate][0]
            available_preferences = [workshop for workshop in preferences if workshop != current_workshop]

            if available_preferences:
                new_workshop = random.choice(available_preferences)

                # Ensure no overlap of sessions within this camper's schedule
                existing_workshops = [workshop for workshop, _ in individual.schedule[camper_id]]

                if new_workshop not in existing_workshops:
                    if individual.can_assign(camper_id, new_workshop, slot_to_mutate, individual.schedule[camper_id]):
                        # Remove old booking if it exists
                        old_workshop = individual.schedule[camper_id][slot_to_mutate][0]
                        if old_workshop != "-" and camper_id in individual.session_bookings.get(old_workshop, {}).get(slot_to_mutate, []):
                            individual.session_bookings[old_workshop][slot_to_mutate].remove(camper_id)

                        # Assign new workshop and update bookings
                        individual.schedule[camper_id][slot_to_mutate] = (new_workshop, slot_to_mutate)
                        individual.add_booking(camper_id, new_workshop, slot_to_mutate)

    def run(self):
        for generation in range(self.generations):
            # Calculate fitness for each schedule in the population
            fitness_scores = [self.fitness(schedule) for schedule in self.population]

            # Find the best schedule of the current generation
            best_current = max(self.population, key=self.fitness)
            best_fitness_current = self.fitness(best_current)

            # Debug statement: Print generation number and best fitness score
            print(f"Generation {generation + 1}/{self.generations} - Best Fitness: {best_fitness_current}")

            # Selection process
            selected_individuals = self.selection(self.population, fitness_scores)

            next_population = []
            for i in range(0, len(selected_individuals), 2):
                if random.random() < self.crossover_rate:
                    parent1, parent2 = selected_individuals[i], selected_individuals[i + 1]
                    child1, child2 = self.crossover(parent1, parent2)
                    next_population.extend([child1, child2])
                else:
                    next_population.extend([selected_individuals[i], selected_individuals[i + 1]])

            # Apply mutation to the next population
            for individual in next_population:
                self.mutation(individual)

            self.population = next_population

            # Elitism: Preserve the best individual from the current generation
            if not self.best_schedule or best_fitness_current > self.fitness(self.best_schedule):
                self.best_schedule = best_current

        # Final best schedule after all generations
        final_best_fitness = self.fitness(self.best_schedule)
        print(f"Final Best Fitness: {final_best_fitness}")

        return self.best_schedule

    def calculate_completion_rate(self, schedule):
        total_campers = len(schedule.configuration['campers'])
        fully_scheduled = sum(1 for workshops in schedule.schedule.values() if len([w for w, _ in workshops if w != '-']) == 3)
        completion_rate = (fully_scheduled / total_campers) * 100

        print(f"Completion Rate: {fully_scheduled} out of {total_campers} campers ({completion_rate:.2f}%) were fully scheduled.")
        return completion_rate

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

        return satisfaction_counts