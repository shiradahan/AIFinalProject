import random
from random import randrange


class Schedule:
	def __init__(self, configuration):
		self.configuration = configuration
		self.schedule = self.generate_initial_schedule()

	def generate_initial_schedule(self):
		schedule = {}
		for camper_id, camper_data in self.configuration['campers'].items():
			age_group = camper_data['age_group']
			preferences = camper_data['preferences']
			assigned_workshops = random.sample(preferences, 3)  # Randomly assign 3 out of 4 preferences
			schedule[camper_id] = assigned_workshops
		return schedule

	def fitness(self):
		score = 0
		workshop_capacities = {workshop: 0 for workshop in self.configuration['workshops']}

		for camper_id, workshops in self.schedule.items():
			age_group = self.configuration['campers'][camper_id]['age_group']

			if len(set(workshops)) == len(workshops):
				score += 1

			for workshop in workshops:
				if self.configuration['workshops'][workshop]['age_group'] == age_group:
					score += 1
				workshop_capacities[workshop] += 1

		for workshop, count in workshop_capacities.items():
			if count <= 15:
				score += 1
			else:
				score -= (count - 15)  # Penalize for exceeding capacity

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

		return child

	def mutation(self, mutationSize, mutationProbability):
		if random.randint(0, 100) > mutationProbability:
			return

		for _ in range(mutationSize):
			camper_id = random.choice(list(self.schedule.keys()))
			workshops = self.schedule[camper_id]
			preference = self.configuration['campers'][camper_id]['preferences']
			mutated_workshop = random.choice([w for w in preference if w not in workshops])
			workshops[random.randint(0, 2)] = mutated_workshop

	def makeNewFromPrototype(self):
		return Schedule(self.configuration)
