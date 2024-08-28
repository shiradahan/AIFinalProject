import random


class FIFOSchedule:
    def __init__(self, configuration):
        self.configuration = configuration
        self.session_bookings = {workshop: {slot: [] for slot in range(3)} for workshop in self.configuration['workshops']}
        self.schedule = {}
        self.camper_slots = {}  # Track slots assigned to each camper
        self.max_slots_per_workshop = 15  # Max capacity of each session
        self.run_fifo_schedule()

    def run_fifo_schedule(self):
        for camper_id, camper_data in self.configuration['campers'].items():
            preferences = camper_data['preferences']
            assigned_workshops = []

            for preference in preferences:
                for slot in range(3):
                    if len(self.session_bookings[preference][slot]) < self.max_slots_per_workshop:
                        assigned_workshops.append((preference, slot))
                        self.session_bookings[preference][slot].append(camper_id)
                        break
                if len(assigned_workshops) == 3:
                    break

            # Randomly assign remaining slots without checking constraints
            while len(assigned_workshops) < 3:
                for workshop, slots in self.session_bookings.items():
                    for slot in range(3):
                        if len(slots[slot]) < self.max_slots_per_workshop:
                            assigned_workshops.append((workshop, slot))
                            self.session_bookings[workshop][slot].append(camper_id)
                            break
                    if len(assigned_workshops) == 3:
                        break

            self.schedule[camper_id] = assigned_workshops

    def calculate_satisfaction_rate(self):
        satisfaction_counts = {0: 0, 1: 0, 2: 0, 3: 0}

        for camper_id, workshops in self.schedule.items():
            preferences = set(self.configuration['campers'][camper_id]['preferences'])
            fulfilled_count = sum(1 for workshop, _ in workshops if workshop in preferences)
            satisfaction_counts[fulfilled_count] += 1

        total_campers = sum(satisfaction_counts.values())

        print("Satisfaction Rates (Simple FIFO):")
        for count, num_campers in satisfaction_counts.items():
            percentage = (num_campers / total_campers) * 100
            print(f"{num_campers} campers ({percentage:.2f}%) got {count} of their preferred workshops.")

        return satisfaction_counts

    def __str__(self):
        schedule_str = "Simple FIFO Schedule:\n"
        for camper_id, workshops in self.schedule.items():
            schedule_str += f"Camper {camper_id}: {', '.join(f'{w} (slot {s})' for w, s in workshops)}\n"
        return schedule_str