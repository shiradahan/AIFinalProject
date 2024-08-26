from Model.Schedule import Schedule
from random import randrange, random
from time import time


class GeneticAlgorithm:
    def __init__(self, configuration, numberOfChromosomes=100, replaceByGeneration=8, trackBest=5,
                 numberOfCrossoverPoints=2, mutationSize=2, crossoverProbability=80, mutationProbability=3):
        self._prototype = Schedule(configuration)
        self._chromosomes = numberOfChromosomes * [None]
        self._bestFlags = numberOfChromosomes * [False]
        self._bestChromosomes = trackBest * [0]
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

    def addToBest(self, chromosomeIndex):
        bestChromosomes = self._bestChromosomes
        bestFlags = self._bestFlags
        chromosomes = self._chromosomes

        if self._currentBestSize == len(bestChromosomes) and chromosomes[bestChromosomes[self._currentBestSize - 1]].fitness() >= chromosomes[
            chromosomeIndex].fitness():
            return

        i = self._currentBestSize
        while i > 0:
            pos = bestChromosomes[i - 1]
            if i < len(bestChromosomes):
                if chromosomes[pos].fitness() > chromosomes[chromosomeIndex].fitness():
                    break
                bestChromosomes[i] = pos
            else:
                bestFlags[pos] = False
            i -= 1

        bestChromosomes[i] = chromosomeIndex
        bestFlags[chromosomeIndex] = True
        if self._currentBestSize < len(bestChromosomes):
            self._currentBestSize += 1

    def isInBest(self, chromosomeIndex):
        return self._bestFlags[chromosomeIndex]

    def clearBest(self):
        self._bestFlags = len(self._bestFlags) * [False]
        self._currentBestSize = 0

    def initialize(self, population):
        for i in range(len(population)):
            population[i] = self._prototype.makeNewFromPrototype()

    def selection(self, population):
        return (population[randrange(32768) % len(population)], population[randrange(32768) % len(population)])

    def replacement(self, population, replaceByGeneration):
        offspring = replaceByGeneration * [None]
        for j in range(replaceByGeneration):
            parent = self.selection(population)
            offspring[j] = parent[0].crossover(parent[1], self._numberOfCrossoverPoints, self._crossoverProbability)
            offspring[j].mutation(self._mutationSize, self._mutationProbability)
            ci = randrange(32768) % len(population)
            while self.isInBest(ci):
                ci = randrange(32768) % len(population)
            population[ci] = offspring[j]
            self.addToBest(ci)
        return offspring

    def run(self, maxRepeat=9999, minFitness=0.999):
        self.clearBest()
        self.initialize(self._chromosomes)
        random.seed(round(time() * 1000))
        currentGeneration = 0
        repeat = 0
        lastBestFit = 0.0

        while True:
            best = self.result
            print("Fitness:", "{:f}\t".format(best.fitness()), "Generation:", currentGeneration, end="\r")

            if best.fitness() > minFitness:
                break

            difference = abs(best.fitness() - lastBestFit)
            if difference <= 0.0000001:
                repeat += 1
            else:
                repeat = 0

            if repeat > (maxRepeat / 100):
                random.seed(round(time() * 1000))
                self.set_replace_by_generation(self._replaceByGeneration * 3)
                self._crossoverProbability += 1

            self.replacement(self._chromosomes, self._replaceByGeneration)
            lastBestFit = best.fitness()
            currentGeneration += 1

    def __str__(self):
        return "Genetic Algorithm"
