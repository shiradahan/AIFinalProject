import numpy as np
import pandas as pd
from Model.BaselineAlgorithm import FIFOSchedule
from Model.GeneticAlgorithm import GeneticAlgorithm
import matplotlib.pyplot as plt

from CSPAlgorithm import csp_solve

CAMPERS = 100


def load_configuration_from_excel(file_path, samples):
    # Load camper data from Excel
    sheet_data = pd.read_excel(file_path, sheet_name='Sheet1')

    sheet_data = sheet_data.sample(n=samples)

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


def check_constraints(schedule, configuration):
    # Define the adjacent age groups as tuples
    adjacent_pairs = [('Nanobyte', 'Kilobyte'), ('Megabyte', 'Gigabyte')]

    # Create a set for quick lookup of adjacent pairs
    adjacent_set = set(adjacent_pairs)

    def are_adjacent_or_same_age_groups(group1, group2):
        return group1 == group2 or (group1, group2) in adjacent_set or (group2, group1) in adjacent_set

    # Check capacity constraints
    capacity_errors = []
    for workshop, slots in schedule.session_bookings.items():
        for slot, age_groups in slots.items():
            for age_group_key, campers in age_groups.items():
                if len(campers) > 15:
                    capacity_errors.append(
                        f"Workshop '{workshop}', slot {slot}, age group '{age_group_key}' exceeds capacity with {len(campers)} campers.")

    # Check age group constraints
    age_group_errors = []
    for camper_id, workshops in schedule.schedule.items():
        camper_age_group = configuration['campers'][camper_id]['age_group']
        for workshop, slot in workshops:
            if workshop != "-":
                session_age_group = 'young' if camper_age_group in schedule.young_group else 'old'
                workshop_camper_list = schedule.session_bookings[workshop][slot][session_age_group]
                if camper_id not in workshop_camper_list:
                    age_group_errors.append(
                        f"Camper {camper_id} in '{camper_age_group}' group wrongly booked in '{session_age_group}' session of workshop '{workshop}', slot {slot}.")

    # Check preference constraints
    preference_errors = []
    for camper_id, workshops in schedule.schedule.items():
        preferences = configuration['campers'][camper_id]['preferences']
        scheduled_workshops = {w for w, _ in workshops if w != "-"}
        if not scheduled_workshops.issubset(preferences):
            preference_errors.append(
                f"Camper {camper_id} has non-preferred workshops assigned: {scheduled_workshops.difference(preferences)}.")

    # Print errors if any
    if capacity_errors:
        print("Capacity Constraints Errors:")
        for error in capacity_errors:
            print(error)
    else:
        print("All capacity constraints met.\n")

    if age_group_errors:
        print("Age Group Constraints Errors:")
        for error in age_group_errors:
            print(error)
    else:
        print("All age group constraints met.\n")

    if preference_errors:
        print("Preference Constraints Errors:")
        for error in preference_errors:
            print(error)
        print()
    else:
        print("All preference constraints met.")


def print_non_preferred_workshops(schedule, configuration):
    print("Non-Preferred Workshops per Camper:")
    for camper_id, workshops in schedule.schedule.items():
        preferences = set(configuration['campers'][camper_id]['preferences'])
        non_preferred_count = sum(1 for w, _ in workshops if w not in preferences)
        print(f"Camper {camper_id} has {non_preferred_count} non-preferred workshops.")
    print()  # Empty line between print assignments


def print_clear_schedule_overview(schedule, file_path):
    # Define the time slots
    time_slots = ['9:00 AM - 12:00 PM', '1:00 PM - 3:00 PM', '3:00 PM - 6:00 PM']

    # Initialize the structure to hold workshop information for each session
    session_data = {slot: {'Young': [], 'Old': []} for slot in time_slots}

    # Fill in the session data with workshops, capacities, and campers
    for workshop, slots in schedule.session_bookings.items():
        for slot_idx, age_groups in slots.items():
            if slot_idx >= len(time_slots):
                print(f"Warning: Slot index {slot_idx} is out of range. Skipping this slot.")
                continue  # Skip invalid slots

            # Process each age group
            for age_group_key, campers in age_groups.items():
                if len(campers) == 0:
                    continue  # Skip sessions with zero campers

                # Prepare the list of campers in this workshop and session
                camper_list = "\n        ".join(f"{i + 1}. {camper}" for i, camper in enumerate(campers))
                capacity = f"{len(campers)}/15"
                session_data[time_slots[slot_idx]][age_group_key.capitalize()].append(
                    f"{workshop} ({capacity}):\n        {camper_list}")

    # Write the schedule to a file
    with open(file_path, 'w') as file:
        for idx, slot in enumerate(time_slots):
            file.write(f"Session {idx + 1} ({slot}):\n")

            # Write Young Group Workshops
            file.write("  Young Group:\n")
            if session_data[slot]['Young']:
                for workshop in session_data[slot]['Young']:
                    file.write(f"    - {workshop}\n")
            else:
                file.write("    No Workshops\n")

            # Write Older Group Workshops
            file.write("  Older Group:\n")
            if session_data[slot]['Old']:
                for workshop in session_data[slot]['Old']:
                    file.write(f"    - {workshop}\n")
            else:
                file.write("    No Workshops\n")

            file.write("\n" + "-" * 60 + "\n")


def plot_schedule_overview(schedule, configuration, fifo):
    # Define the time slots
    time_slots = ['9:00 AM - 12:00 PM', '1:00 PM - 3:00 PM', '3:00 PM - 6:00 PM']

    # Initialize the structure to hold workshop information for each session
    session_data = {slot: {'Young': [], 'Old': []} for slot in time_slots}

    # Fill in the session data with workshops and capacities
    for workshop, slots in schedule.session_bookings.items():
        for slot_idx, age_groups in slots.items():
            if slot_idx >= len(time_slots):
                continue  # Skip invalid slots
            for age_group_key, campers in age_groups.items():
                if len(campers) > 0:
                    capacity = f"{len(campers)}/15"
                    session_data[time_slots[slot_idx]][age_group_key.capitalize()].append(f"{workshop} ({capacity})")

    # Determine the maximum number of workshops in any session for dynamic sizing
    max_workshops = max(
        max(len(session_data[slot]['Young']), len(session_data[slot]['Old']))
        for slot in time_slots
    )

    # Calculate the required figure height based on the number of workshops
    fig_height = max(6, max_workshops * 0.6)  # Adjust the multiplier as needed

    # Set up the plot
    fig, ax = plt.subplots(figsize=(15, fig_height))  # Increase the figure width and height dynamically
    ax.axis('off')  # Turn off the axis

    # Prepare the data for the table
    col_labels = ["Session", "Young Group", "Older Group"]
    cell_text = []

    for idx, slot in enumerate(time_slots):
        cell_text.append([
            f"Session {idx + 1} ({slot})",
            "\n".join(session_data[slot]['Young']) if session_data[slot]['Young'] else "No Workshops",
            "\n".join(session_data[slot]['Old']) if session_data[slot]['Old'] else "No Workshops"
        ])

    # Create the table
    table = ax.table(cellText=cell_text, colLabels=col_labels, cellLoc='center', loc='center')

    # Customize table appearance
    table.auto_set_font_size(False)
    table.set_fontsize(10)  # Keep a readable font size
    table.scale(1.5, 2.0)  # Adjust the scale of the table

    # Adjust row heights based on content
    row_height = 0.05 * max_workshops + 0.1  # Adjust height dynamically
    for pos, cell in table.get_celld().items():
        if pos[0] == 0:  # Header row
            cell.set_height(0.15)  # Set a higher height for header
        cell.set_height(row_height)

    # Save the plot based on the 'fifo' flag
    plt.savefig("FIFO camp schedule.pdf" if fifo else "Genetic camp schedule.pdf", bbox_inches='tight', dpi=300)


def generate_personalized_tables(schedule):
    for camper_id, workshops in schedule.schedule.items():
        data = {
            'Time Slot': ['Slot 1 (9:00 AM - 12:00 PM)', 'Slot 2 (1:00 PM - 3:00 PM)', 'Slot 3 (3:00 PM - 6:00 PM)'],
            'Workshop': [None, None, None]
        }
        for workshop, slot in workshops:
            data['Workshop'][slot] = workshop

        camper_schedule_df = pd.DataFrame(data)
        print(f"Schedule for Camper: {camper_id}")
        print(camper_schedule_df)
        print("\n" + "-" * 30 + "\n")


def run_fifo_schedule(configuration):
    print("Running FIFO Scheduling Algorithm...\n")
    fifo_schedule = FIFOSchedule(configuration)
    # print(fifo_schedule)  # Print the generated schedule
    # plot_schedule_overview(fifo_schedule, configuration, True)


    # fifo_schedule.print_booking()
    # print("---------------------------------------------------------------")
    # print(fifo_schedule)
    # print("---------------------------------------------------------------")
    # print(f"satisfaction rate: {calculate_satisfaction_rate(configuration, fifo_schedule)}")
    # print(f"completion rate: {calculate_completion_rate(fifo_schedule)}")
    ######
    return fifo_schedule, 'FIFOAlgorithm'


def run_genetic_schedule(configuration):
    # Create and run the genetic algorithm
    ga = GeneticAlgorithm(configuration)
    ga.run()

    # Get the best schedule from the GA result
    best_schedule = ga.best_schedule

    # Print results
    print("Best schedule found:")
    print(best_schedule)
    print()  # Empty line

    # Print non-preferred workshops
    # print_non_preferred_workshops(best_schedule, configuration)

    # Check constraints for the best schedule
    # check_constraints(best_schedule, configuration)

    plot_schedule_overview(best_schedule, configuration, False)
    print_clear_schedule_overview(best_schedule, 'Results/camp_schedule.txt')
    generate_personalized_tables(best_schedule)

    best_schedule.print_booking()
    print("---------------------------------------------------------------")
    print(best_schedule)
    print("---------------------------------------------------------------")
    print(f"satisfaction rate: {calculate_satisfaction_rate(configuration, best_schedule)}")
    print(f"completion rate: {calculate_completion_rate(best_schedule)}")

    # # Calculate and print satisfaction rate
    # satisfaction_rate = ga.calculate_satisfaction_rate(best_schedule)
    #
    # # Calculate and print completion rate
    # completion_rate = ga.calculate_completion_rate(best_schedule)

    #### s
    return best_schedule, 'GeneticAlgorithm'


def calculate_completion_rate(schedule):
    total_campers = len(schedule.schedule)
    fully_scheduled = sum(
        1 for workshops in schedule.schedule.values() if len([w for w, _ in workshops if w != '-']) == 3)
    percentages = (fully_scheduled / total_campers) * 100
    return f"{fully_scheduled} out of {total_campers} campers ({percentages:.2f}%) where fully scheduled"


def calculate_satisfaction_rate(prefrences, schedule):
    satisfaction_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    for camper_name, workshops in schedule.schedule.items():
        camper_prefs = set(prefrences['campers'][camper_name]['preferences'])
        fulfilled_count = sum(1 for workshop, _ in workshops if workshop in camper_prefs and workshop != '-')
        satisfaction_counts[fulfilled_count] += 1

    total_campers = sum(satisfaction_counts.values())

    print("Satisfaction Rates:")
    for count, num_campers in satisfaction_counts.items():
        percentage = (num_campers / total_campers) * 100
        print(f"{num_campers} campers ({percentage:.2f}%) got {count} of their preferred workshops.")

    weighted_score = sum([count * amount for count, amount in satisfaction_counts.items()])
    print(f"weighted score: {weighted_score}")

    # return satisfaction_counts
    return weighted_score


def main():
    # file_path = 'Data/400campersData.xlsx'
    # # configuration = load_configuration_from_excel(file_path)
    # configuration = load_configuration_from_excel(file_path, CAMPERS)
    # configuration['workshops']['-'] = {'age_group': None, 'name': '-'}
    #
    # # Print the configuration
    # print("Configuration Loaded:")
    # print(configuration)
    # print(f"Number of campers in configuration: {len(configuration['campers'])}")
    #
    # # Run FIFO scheduling
    # fifo_schedule = run_fifo_schedule(configuration)
    #
    # # Run Genetic scheduling
    # genetic_schedule = run_genetic_schedule(configuration)
    #
    # # Run CSP scheduling
    # csp_schedule = csp_solve(configuration)
    #
    # for schedule in [fifo_schedule, genetic_schedule, csp_schedule]:
    #     print("---------------------------------------------------------------")
    #     print(f'{schedule[1]} campers: {CAMPERS}')
    #     print(f"satisfaction rate: {calculate_satisfaction_rate(configuration, schedule[0])}")
    #     print(f"completion rate: {calculate_completion_rate(schedule[0])}")

    satisfaction_rate_lst = []
    completion_rate_lst = []

    print("---------------------------------------------------------------")
    print(f'csp campers: {CAMPERS}')

    for i in range(10):
        file_path = 'Data/400campersData.xlsx'
        configuration = load_configuration_from_excel(file_path, CAMPERS)
        configuration['workshops']['-'] = {'age_group': None, 'name': '-'}
        schedule = run_genetic_schedule(configuration)
        satisfaction_rate = calculate_satisfaction_rate(configuration, schedule[0])
        satisfaction_rate_lst.append(satisfaction_rate)
        # completion_rate = calculate_completion_rate(schedule[0])
        # completion_rate_lst.append(completion_rate)

    print("---------------------------------------------------------------")
    print('satisfaction_rate_lst: \n')
    print(satisfaction_rate_lst)
    print('mean: \n')
    print(np.mean(satisfaction_rate_lst))


    print('std: \n')
    print(np.std(satisfaction_rate_lst))



if __name__ == '__main__':
    main()
