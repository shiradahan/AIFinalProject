import pandas as pd
from GeneticAlgorithm import GeneticAlgorithm
from Model.Schedule import Schedule
from Model.Camper import Camper
from Model.Session import Session


def load_configuration_from_excel(file_path):
	# Load camper data from Excel
	sheet_data = pd.read_excel(file_path, sheet_name='Sheet1')

	# Initialize the configuration dictionary
	configuration = {'campers': {}, 'workshops': {}}

	# Initialize a set to track workshop names for uniqueness
	workshop_names = set()

	# Process each row to populate the configuration dictionary
	for _, row in sheet_data.iterrows():
		camper_name = row['Camper\'s name']
		age_group = row['Age Unit']
		preferences = [row['Selection #1'], row['Selection #2'], row['Selection #3'], row['Selection #4']]

		# Add camper details to the dictionary
		configuration['campers'][camper_name] = {
			'age_group': age_group,
			'preferences': preferences
		}

		# Add workshop details to the set to ensure uniqueness
		for preference in preferences:
			if preference and preference not in workshop_names:
				workshop_names.add(preference)

	# Convert workshop names to dictionary format
	configuration['workshops'] = {name: {'name': name} for name in workshop_names}

	return configuration


def initialize_model(configuration):
	# Create camper and session instances from the configuration
	campers = {name: Camper(name, data['age_group'], data['preferences']) for name, data in configuration['campers'].items()}
	sessions = {name: Session(idx, name, 'all') for idx, name in enumerate(configuration['workshops'].keys())}

	# Create a Schedule instance
	schedule = Schedule(configuration)

	return campers, sessions, schedule


def main():
	file_path = 'campersData.xlsx'
	configuration = load_configuration_from_excel(file_path)

	# Print the configuration
	print("Configuration Loaded:")
	print(configuration)

	# Initialize the model
	campers, sessions, schedule = initialize_model(configuration)

	# Create and run the genetic algorithm
	ga = GeneticAlgorithm(configuration)
	ga.run()

	# Print results
	print("Best schedule found:")
	print(ga.result)


if __name__ == '__main__':
	main()
