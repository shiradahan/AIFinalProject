class Configuration:
    def __init__(self, max_generations, population_size, crossover_rate, mutation_rate):
        self.max_generations = max_generations
        self.population_size = population_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate

    def __str__(self):
        return f"Max Generations: {self.max_generations}, Population Size: {self.population_size}, " \
               f"Crossover Rate: {self.crossover_rate}, Mutation Rate: {self.mutation_rate}"
