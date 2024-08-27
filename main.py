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

        # Add workshop details
        for preference in preferences:
            if preference and preference not in configuration['workshops']:
                configuration['workshops'][preference] = {'name': preference, 'age_group': None}

    return configuration


def initialize_model(configuration):
    # Create camper and session instances from the configuration
    campers = {name: Camper(name, data['age_group'], data['preferences']) for name, data in configuration['campers'].items()}
    sessions = {name: Session(idx, name, 'all') for idx, name in enumerate(configuration['workshops'].keys())}

    # Create a Schedule instance
    schedule = Schedule(configuration)  # Use only the configuration

    return campers, sessions, schedule


def check_constraints(schedule, configuration):
    # Define the adjacent age groups as tuples
    adjacent_pairs = [('Nanobyte', 'Kilobyte'), ('Kilobyte', 'Megabyte'), ('Megabyte', 'Gigabyte')]

    # Create a set for quick lookup of adjacent pairs
    adjacent_set = set(adjacent_pairs)

    def are_adjacent_or_same_age_groups(group1, group2):
        return group1 == group2 or (group1, group2) in adjacent_set or (group2, group1) in adjacent_set

    # Check capacity constraints
    capacity_errors = []
    for workshop, slots in schedule.session_bookings.items():
        for slot, campers in slots.items():
            if len(campers) > 15:
                capacity_errors.append(f"Workshop '{workshop}' slot {slot} exceeds capacity with {len(campers)} campers.")

    # Check age group constraints
    age_group_errors = []
    for camper_id, workshops in schedule.schedule.items():
        camper_age_group = configuration['campers'][camper_id]['age_group']
        for workshop, slot in workshops:
            workshop_age_group = configuration['workshops'][workshop]['age_group']
            if workshop_age_group and not are_adjacent_or_same_age_groups(camper_age_group, workshop_age_group):
                age_group_errors.append(f"Camper {camper_id} assigned to workshop '{workshop}' with mismatched age group.")

    # Check preference constraints
    preference_errors = []
    for camper_id, workshops in schedule.schedule.items():
        preferences = configuration['campers'][camper_id]['preferences']
        if not set([w for w, _ in workshops]).issubset(preferences):
            preference_errors.append(f"Camper {camper_id} has non-preferred workshops.")

    # Print errors if any
    if capacity_errors:
        print("Capacity Constraints Errors:")
        for error in capacity_errors:
            print(error)
    else:
        print("All capacity constraints met.")

    if age_group_errors:
        print("Age Group Constraints Errors:")
        for error in age_group_errors:
            print(error)
    else:
        print("All age group constraints met.")

    if preference_errors:
        print("Preference Constraints Errors:")
        for error in preference_errors:
            print(error)
    else:
        print("All preference constraints met.")


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

    # Get the best schedule from the GA result
    best_schedule = ga.result

    # Print results
    print("Best schedule found:")
    print(best_schedule)  # This assumes __str__ or __repr__ methods are properly defined in the Schedule class

    # Check constraints for the best schedule
    check_constraints(best_schedule, configuration)


if __name__ == '__main__':
    main()
