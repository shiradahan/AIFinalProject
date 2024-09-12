import copy

import Model.GeneticAlgorithm
# import util
from Model.Schedule import Schedule
from itertools import permutations


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

    return satisfaction_counts


def calc_remaining_value(camper_id, age_group, workshops_permutations, schedule):
    score = 0
    for perm in workshops_permutations:
        score += sum([schedule.can_assign(camper_id, perm[i], i, age_group) for i in range(3)])  # TODO: make generic
    return score


def create_permutations(camper):
    return list(permutations(camper['preferences'], 3))


def select_unassigned_student(campers_prefs, schedule):
    next_camper = None
    min_MRV = float('inf')
    for camper in campers_prefs.items():
        workshops_permutations = create_permutations(camper[1])
        MRV_score = calc_remaining_value(camper[0], camper[1]['age_group'], workshops_permutations, schedule)
        if MRV_score < min_MRV:
            next_camper = camper
            min_MRV = MRV_score
    return next_camper


def assign_by_LCV(camper, schedule):
    best_perm = None
    lcv_score = 0
    workshops_permutations = create_permutations(camper[1])
    for perm in workshops_permutations:
        score = 0
        for i in range(len(perm)):
            score += schedule.get_remain_sit(perm[i], i, camper[1]['age_group'])
            #score += 20 if schedule.get_remain_sit(perm[i], i, camper[1]['age_group']) == 4 else 0
        # score = sum([schedule.get_remain_sit(perm[i], i, camper[1]['age_group']) for i in range(len(perm))])

        if score > lcv_score:
            lcv_score = score
            best_perm = perm
    for slot in range(len(best_perm)):
        if schedule.can_assign(camper[0], best_perm[slot], slot, camper[1]['age_group']):
            schedule.add_booking(camper[0], best_perm[slot], slot, camper[1]['age_group'])
            schedule.add_to_schedule(camper[0], best_perm)
            continue
        if schedule.can_start_new_session_in_slot(slot):
            # TODO: create new workshop in this slot and assign camper
            schedule.add_booking(camper[0], best_perm[slot], slot, camper[1]['age_group'])
            schedule.add_to_schedule(camper[0], best_perm)
            continue
        # TODO: assign '-' to this slot
        schedule.add_booking(camper[0], '-', slot, camper[1]['age_group'])
        lst = list(best_perm)
        lst[slot] = '-'
        best_perm = tuple(lst)
        schedule.add_to_schedule(camper[0], best_perm)


# def find_available_workshop(schedule, camper_id, slot, age_group):
#     for workshop in schedule.session_bookings.items():
#         curr_workshop = workshop[1][slot][age_group]
#         if 5 < len(curr_workshop) < 15:
#             schedule.add_booking(camper_id, workshop[0], slot, age_group)
#             return True
#     return False

def csp_solve(campers_data):
    schedule = Schedule(campers_data)
    lst_campers_pref = copy.deepcopy(campers_data['campers'])
    while lst_campers_pref:
        camper = select_unassigned_student(lst_campers_pref, schedule)  # MRV
        assign_by_LCV(camper, schedule)
        # remove camper from data
        lst_campers_pref.pop(camper[0])

    # eliminate too small workshops
    # for workshop in schedule.session_bookings.items():
    #     for slot in range(len(workshop[1].keys())):
    #         curr_workshop = workshop[1][slot]['old']
    #         if len(curr_workshop) < 5:
    #             for camper_name in curr_workshop:
    #                 schedule.schedule[camper_name].pop(slot)
    #                 schedule.schedule[camper_name].insert(slot, ("-", slot))
    #                 continue
    #             workshop[1][slot]['old'] = []
    #
    # for workshop in schedule.session_bookings.items():
    #     for slot in range(len(workshop[1].keys())):
    #         curr_workshop = workshop[1][slot]['young']
    #         if len(curr_workshop) < 5:
    #             for camper_name in curr_workshop:
    #                 lst = list(schedule.schedule[camper_name])
    #                 lst[slot] = ("-", slot)
    #                 continue
    #             workshop[1][slot]['young'] = []

    # schedule.print_booking()
    # print("---------------------------------------------------------------")
    # print(schedule)
    # print("---------------------------------------------------------------")
    # print(f"satisfaction rate: {calculate_satisfaction_rate(campers_data, schedule)}")
    # print(f"completion rate: {calculate_completion_rate(schedule)}")

    return schedule, 'CSPAlgorithm'
