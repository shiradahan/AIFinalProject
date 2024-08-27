from random import randrange, random, seed
from time import time

from Model.Schedule import Schedule

class GeneticAlgorithm:
    def __init__(self, configuration, numberOfChromosomes=100, replaceByGeneration=8, trackBest=5,
                 numberOfCrossoverPoints=2, mutationSize=2, crossoverProbability=80, mutationProbability=3):
        self._prototype = Schedule(configuration)
        self._chromosomes = [self._prototype.makeNewFromPrototype() for _ in range(numberOfChromosomes)]
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
        fitness = self._chromosomes[chromosome_index].fitness()
        if (self._currentBestSize == len(self._bestChromosomes) and
                self._chromosomes[self._bestChromosomes[-1]].fitness() >= fitness):
            return

        # Insert chromosome in sorted order
        i = self._currentBestSize
        while i > 0 and self._chromosomes[self._bestChromosomes[i - 1]].fitness() > fitness:
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
        self._chromosomes = [self._prototype.makeNewFromPrototype() for _ in range(len(self._chromosomes))]

    def select_parents(self):
        return (self._chromosomes[randrange(len(self._chromosomes))],
                self._chromosomes[randrange(len(self._chromosomes))])

    def replace_generation(self):
        for _ in range(self._replaceByGeneration):
            parent1, parent2 = self.select_parents()
            child = parent1.crossover(parent2, self._numberOfCrossoverPoints, self._crossoverProbability)
            child.mutation(self._mutationSize, self._mutationProbability)
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
            current_fitness = best_chromosome.fitness()

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

            print(f"Best fitness: {self.result.fitness():.6f} after {current_generation} generations.")
        return self.result
