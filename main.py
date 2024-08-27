import pandas as pd
from GeneticAlgorithm import GeneticAlgorithm
from Model.Schedule import Schedule
from Model.Camper import Camper
from Model.Session import Session
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


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
    adjacent_pairs = [('Nanobyte', 'Kilobyte'), ('Megabyte', 'Gigabyte')]

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
        print("All age group constraints met.\n")

    # if preference_errors:
    #     print("Preference Constraints Errors:")
    #     for error in preference_errors:
    #         print(error)
    # else:
    #     print("All preference constraints met.")


def print_non_preferred_workshops(schedule, configuration):
    print("Non-Preferred Workshops per Camper:")
    for camper_id, workshops in schedule.schedule.items():
        preferences = set(configuration['campers'][camper_id]['preferences'])
        non_preferred_count = sum(1 for w, _ in workshops if w not in preferences)
        print(f"Camper {camper_id} has {non_preferred_count} non-preferred workshops.")
    print()  # Empty line between print assignments


def print_clear_schedule_overview(schedule, configuration):
    # Define the time slots
    time_slots = ['9:00 AM - 12:00 PM', '1:00 PM - 3:00 PM', '3:00 PM - 6:00 PM']

    # Initialize the structure to hold workshop information for each session
    session_data = {slot: {'Young': [], 'Old': []} for slot in time_slots}

    # Fill in the session data with workshops and capacities
    for workshop, slots in schedule.session_bookings.items():
        for slot, campers in slots.items():
            if slot >= len(time_slots):
                print(f"Warning: Slot index {slot} is out of range. Skipping this slot.")
                continue  # Skip invalid slots

            if len(campers) == 0:
                continue  # Skip sessions with zero campers

            age_group_set = {configuration['campers'][camper]['age_group'] for camper in campers}
            if age_group_set.issubset({'Nanobyte', 'Kilobyte'}):
                age_group = 'Young'
            elif age_group_set.issubset({'Megabyte', 'Gigabyte'}):
                age_group = 'Old'
            else:
                continue  # If mixed age groups are found, skip (should not happen)

            capacity = f"{len(campers)}/15"
            session_data[time_slots[slot]][age_group].append(f"{workshop} ({capacity})")

    # Print the schedule for each session
    for idx, slot in enumerate(time_slots):
        print(f"Session {idx + 1} ({slot}):")

        # Print Young Group Workshops
        print("  Young Group:")
        if session_data[slot]['Young']:
            for workshop in session_data[slot]['Young']:
                print(f"    - {workshop}")
        else:
            print("    No Workshops")

        # Print Older Group Workshops
        print("  Older Group:")
        if session_data[slot]['Old']:
            for workshop in session_data[slot]['Old']:
                print(f"    - {workshop}")
        else:
            print("    No Workshops")

        print("\n" + "-" * 60 + "\n")


def plot_clear_schedule_overview(schedule, configuration):
    # Define the time slots
    time_slots = ['9:00 AM - 12:00 PM', '1:00 PM - 3:00 PM', '3:00 PM - 6:00 PM']

    # Initialize the structure to hold workshop information for each session
    session_data = {slot: {'Young': [], 'Old': []} for slot in time_slots}

    # Fill in the session data with workshops and capacities
    for workshop, slots in schedule.session_bookings.items():
        for slot, campers in slots.items():
            age_group_set = {configuration['campers'][camper]['age_group'] for camper in campers}
            if age_group_set.issubset({'Nanobyte', 'Kilobyte'}):
                age_group = 'Young'
            elif age_group_set.issubset({'Megabyte', 'Gigabyte'}):
                age_group = 'Old'
            else:
                continue  # If mixed age groups are found, skip (should not happen)

            capacity = f"{len(campers)}/15"
            session_data[time_slots[slot]][age_group].append(f"{workshop} ({capacity})")

    # Determine the maximum number of workshops in any session for dynamic sizing
    max_workshops = max(
        max(len(session_data[slot]['Young']), len(session_data[slot]['Old']))
        for slot in time_slots
    )

    # Calculate the required figure height based on the number of workshops
    fig_height = max(6, max_workshops * 0.5)  # Adjust the multiplier as needed

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

    # Adjust row heights to ensure everything fits well
    row_height = (max_workshops * 0.02) + 0.1 # Adjust height dynamically based on content
    for i in range(len(cell_text) + 1):  # +1 for header
        table[i, 0].set_height(row_height)  # Session column
        table[i, 1].set_height(row_height)  # Young Group column
        table[i, 2].set_height(row_height)  # Older Group column

    # Adjust column widths dynamically
    for i, key in enumerate(table._cells):
        cell = table._cells[key]
        if key[0] == 0:  # Header row
            cell.set_fontsize(12)
            cell.set_text_props(weight='bold')
        if key[1] == 0:  # Session column
            cell.set_width(0.3)  # Increase the width of the Session column
        else:
            cell.set_width(0.6)  # Increase width for workshop columns

    # Improve layout
    # plt.tight_layout()

    # Save the plot as an image file
    plt.savefig("camp_schedule.pdf", bbox_inches='tight', dpi=300)  # Save with high resolution


def plot_clear_schedule_overview(schedule, configuration):
    # Define the time slots
    time_slots = ['9:00 AM - 12:00 PM', '1:00 PM - 3:00 PM', '3:00 PM - 6:00 PM']

    # Initialize the structure to hold workshop information for each session
    session_data = {slot: {'Young': [], 'Old': []} for slot in time_slots}

    # Fill in the session data with workshops and capacities
    for workshop, slots in schedule.session_bookings.items():
        for slot, campers in slots.items():
            if slot >= len(time_slots):
                continue  # Skip invalid slots

            age_group_set = {configuration['campers'][camper]['age_group'] for camper in campers}
            if age_group_set.issubset({'Nanobyte', 'Kilobyte'}):
                age_group = 'Young'
            elif age_group_set.issubset({'Megabyte', 'Gigabyte'}):
                age_group = 'Old'
            else:
                continue  # If mixed age groups are found, skip (should not happen)

            capacity = f"{len(campers)}/15"
            session_data[time_slots[slot]][age_group].append(f"{workshop} ({capacity})")

    # Determine the maximum number of workshops in any session for dynamic sizing
    max_workshops = max(
        max(len(session_data[slot]['Young']), len(session_data[slot]['Old']))
        for slot in time_slots
    )

    # Calculate the required figure height based on the number of workshops
    fig_height = max(6, max_workshops * 0.5)  # Adjust the multiplier as needed

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

    # Adjust row heights to ensure everything fits well
    row_height = (max_workshops * 0.02) + 0.1 # Adjust height dynamically based on content
    for i in range(len(cell_text) + 1):  # +1 for header
        table[i, 0].set_height(row_height)  # Session column
        table[i, 1].set_height(row_height)  # Young Group column
        table[i, 2].set_height(row_height)  # Older Group column

    # Adjust column widths dynamically
    for i, key in enumerate(table._cells):
        cell = table._cells[key]
        if key[0] == 0:  # Header row
            cell.set_fontsize(12)
            cell.set_text_props(weight='bold')
        if key[1] == 0:  # Session column
            cell.set_width(0.3)  # Increase the width of the Session column
        else:
            cell.set_width(0.6)  # Increase width for workshop columns

    # Improve layout
    # plt.tight_layout()

    # Save the plot as an image file
    plt.savefig("camp_schedule.pdf", bbox_inches='tight', dpi=300)  # Save with high resolution


def generate_personalized_tables(schedule, configuration):
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


def calculate_satisfaction_rate(schedule, configuration):
    satisfaction_counts = {0: 0, 1: 0, 2: 0, 3: 0}

    for camper_id, workshops in schedule.schedule.items():
        preferences = set(configuration['campers'][camper_id]['preferences'])
        fulfilled_count = sum(1 for workshop, _ in workshops if workshop in preferences)
        satisfaction_counts[fulfilled_count] += 1

    total_campers = sum(satisfaction_counts.values())

    print("Satisfaction Rates:")
    for count, num_campers in satisfaction_counts.items():
        percentage = (num_campers / total_campers) * 100
        print(f"{num_campers} campers ({percentage:.2f}%) got {count} of their preferred workshops.")

    return satisfaction_counts


def main():
    file_path = 'campersData.xlsx'
    configuration = load_configuration_from_excel(file_path)

    # Print the configuration
    print("Configuration Loaded:")
    print(configuration)
    print()  # Empty line
    print(f"Number of campers in configuration: {len(configuration['campers'])}")

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
    print()  # Empty line

    # Print non-preferred workshops
    print_non_preferred_workshops(best_schedule, configuration)

    # Check constraints for the best schedule
    check_constraints(best_schedule, configuration)

    # Call the function to plot the Gantt chart
    # Example usage:
    plot_clear_schedule_overview(best_schedule, configuration)

    print_clear_schedule_overview(best_schedule, configuration)

    generate_personalized_tables(best_schedule, configuration)

    # Assuming `best_schedule` and `configuration` are already defined in your environment
    satisfaction_counts = calculate_satisfaction_rate(best_schedule, configuration)

if __name__ == '__main__':
    main()