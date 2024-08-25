import pandas as pd

# Define the maximum capacity for each workshop session
max_capacity = 15

# Initialize a dictionary to keep track of the current number of campers in each workshop
workshop_capacity = {}

# Initialize a list to store the final schedule
schedule = []


def fcfs_scheduling(df):
	global workshop_capacity, schedule

	# Iterate over each camper in the order they appear in the dataframe
	for index, row in df.iterrows():
		camper = {
			'Registration ID': row['Registration ID'],
			'Camper Name': row["Camper's name"],
			'Age Unit': row['Age Unit']
		}

		# Try to place the camper in one of their selected workshops
		for i in range(1, 5):
			workshop = row[f'Selection #{i}']

			# Initialize the workshop capacity if it hasn't been tracked yet
			if workshop not in workshop_capacity:
				workshop_capacity[workshop] = 0

			# Check if there's space in the workshop
			if workshop_capacity[workshop] < max_capacity:
				camper['Assigned Workshop'] = workshop
				workshop_capacity[workshop] += 1
				break

		# Add the camper's schedule to the final list
		schedule.append(camper)


def main():
	# Load the Excel file
	df = pd.read_excel('problem data.xlsx', sheet_name='Sheet1')

	# Run the FCFS scheduling algorithm
	fcfs_scheduling(df)

	# Convert the schedule to a DataFrame
	schedule_df = pd.DataFrame(schedule)

	# Save the final schedule to an Excel file
	output_file_path = 'FCFS_Camper_Schedule.xlsx'
	schedule_df.to_excel(output_file_path, index=False)

	print(f"Schedule saved to {output_file_path}")


if __name__ == "__main__":
	main()
