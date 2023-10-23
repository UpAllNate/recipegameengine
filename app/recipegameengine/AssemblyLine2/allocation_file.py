from recipegameengine import Resource, Ingredient        
import copy

def generate_straight_split_string(res_list : list[tuple[Resource, int]], remaining_alloc : int) -> str:
    ret_str = ""
    alloc_count = len(res_list)
    skip = False

    for index, (ares, acount) in enumerate(res_list):

        if not skip:
            if remaining_alloc > 0:

                # last allocation is straight out
                if alloc_count - 1 == index:
                    remaining_alloc -= acount
                    left_text = f"[{acount}] {ares}"
                    ret_str += f"\t< {left_text:<24} v{remaining_alloc:<6} \n"

                # last two allocations are left and right
                elif alloc_count - 2 == index:
                    next_res_name = res_list[index+1][0]
                    next_res_count = res_list[index+1][1]

                    remaining_alloc -= acount
                    remaining_alloc -= next_res_count

                    left_text = f"[{acount}] {ares}"
                    right_text = f"{next_res_name} [{next_res_count}]"

                    ret_str += f"\t< {left_text:<24} v{remaining_alloc:<6} {right_text:>24} >\n"

                    skip = True

                # last two allocations are left and right
                else:
                    next_res_name = res_list[index+1][0]
                    next_res_count = res_list[index+1][1]

                    remaining_alloc -= acount
                    remaining_alloc -= next_res_count

                    left_text = f"[{acount}] {ares}"
                    right_text = f"{next_res_name} [{next_res_count}]"

                    ret_str += f"\t< {left_text:<24} v{remaining_alloc:<6} {right_text:>24} >\n"

                    skip = True
        else:
            skip = False
    return ret_str, remaining_alloc

def generate_RSD_split_string(res_list : list[tuple[Resource, int]], total_alloc : int, alloc_base : int = 10) -> str:

    ret_str = f"__ RSD splits ({alloc_base}) __\n"

    res_list_parsing = copy.deepcopy(res_list)

    # res list parsing items will be popped as their count
    # reaches 0 from being split off

    while res_list_parsing:
        stage_splits = []
        popindexes = []

        # Split off the ones
        for index, (res, count) in enumerate(res_list_parsing):
            ones = int(count % alloc_base)
            if ones > 0:
                # print(f"Modulo of {res}:{count} is {ones}")
                stage_splits.append((res, ones))
                new_count = (count - ones) / alloc_base
                if new_count == 0:
                    popindexes.append(index)
                else:
                    res_list_parsing[index] = (res, new_count)
            else:
                res_list_parsing[index] = (res, count / alloc_base)

        for index in sorted(popindexes, reverse= True):
            res_list_parsing.pop(index)

        gen_str, total_alloc = generate_straight_split_string(stage_splits, remaining_alloc= total_alloc)
        ret_str += gen_str       

        total_alloc = int(total_alloc / alloc_base)
    ret_str += "\n"
    return ret_str

def generate_allocation_file(resource : Resource) -> str:
    ret_str = ""

    # The allocation object is a dictionary with a resource as key with 
    # a dictionary of other resources with qty of each as the value
    for i in resource.allocation.keys():

        # It was easier to work in a list of tuples,
        # so it's made here
        res_list = []

        # loop through the resources that have i as an ingredient
        for j in resource.allocation[i]:
            j : Resource
            res = j.name
            count = resource.allocation[i][j]
            res_list.append((res, int(count)))

        # Compute the total of resource i needed for one crafting of resource
        total_build_requirement = sum([count for res,count in res_list])

        # The number of resources with i as an ingredient
        alloc_count = len(res_list)

        ret_str += f"[{i.name}] {total_build_requirement} total, {alloc_count} resources\n"
        for (res, count) in res_list:
            ret_str += f"\t{res:<25}... {count:>5}...{count * 100 / total_build_requirement:>6.2f}%\n"
        ret_str +=  "\n"

        # Generate the Recursive Staged Decade splits
        if alloc_count > 2:
            ret_str += generate_RSD_split_string(res_list= res_list, total_alloc= total_build_requirement, alloc_base= 10)
            ret_str += generate_RSD_split_string(res_list= res_list, total_alloc= total_build_requirement, alloc_base= 2)
            ret_str += "__ straight split __\n"
            gen_str, remaining_alloc = generate_straight_split_string(res_list, remaining_alloc= total_build_requirement)
            ret_str += gen_str
            ret_str += "\n"
    return ret_str