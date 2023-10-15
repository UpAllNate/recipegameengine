from recipegameengine import RecipeEngine
from recipegameengine import Resource, Ingredient
from recipegameengine import get_starters_required

from pathlib import Path
import os
import shutil

from math import ceil

user_starter_count = int(input("What is your starter limit?\nAnswer: "))
user_starter_period_standard = float(input("What is your starter rate for standard resources?\nAnswer: "))
user_starter_period_nuclear = float(input("What is your starter rate for nuclear resources?\nAnswer: "))

py_file_dir = Path(__file__).parent.resolve()
working_dir = Path().resolve()
project_folder_dir = Path.joinpath(working_dir, "./project_folder")
resources_dir = Path.joinpath(project_folder_dir, "./resources")
profits_file_dir = Path.joinpath(project_folder_dir, "./profits.txt")

print(py_file_dir)
print(working_dir)
print(project_folder_dir)
print(resources_dir)

# Create new project folder
if Path.is_dir(project_folder_dir):
    shutil.rmtree(project_folder_dir)
os.mkdir(project_folder_dir)
os.mkdir(resources_dir)

# Find the toml in current working directory
toml_file_name = None
for filename in os.listdir(working_dir):
    if filename[-5:] == ".toml":
        toml_file_name = filename
        break

if toml_file_name is None:
    raise FileNotFoundError("Could not find .toml file to parse as recipe definition")

re = RecipeEngine(toml_file_name)

profit_list = []

for r in re.resources:
    starters = get_starters_required(r)

    if starters:
        starter_count = sum([st.qty for st in starters])
        starters_standard = sum([st.qty for st in starters if st.resource.name not in ["plutonium", "uranium"]])
        starters_nuclear = starter_count - starters_standard
    else:
        starter_count = 1
        starters_standard = 1 if r.name not in ["plutonium", "uranium"] else 0
        starters_nuclear = 1 if starters_standard == 0 else 0
    
    profit_list.append((r.name, r.price / starter_count, starter_count, starters_standard, starters_nuclear))

profit_list.sort(key=lambda item: (item[1], item[0]))

with open(profits_file_dir, "w") as f:
    for p in profit_list:
        f.write(f"{p[0]:>20} profit per starter: {p[1]:>6.0f} for {p[2]} starters, {p[3]} standard, {p[4]} nuclear\n")

for resource in re.resources:

    resource_folder = Path.joinpath(resources_dir, "./", resource.name)
    os.mkdir(resource_folder)
    allocations_file_dir = Path.joinpath(resource_folder, "./" + resource.name + "_allocations.txt")
    resource_tree_file_dir = Path.joinpath(resource_folder, "./" + resource.name + "_resource_tree.txt")
    starters_file_dir = Path.joinpath(resource_folder, "./" + resource.name + "_starters.txt")

    with open(allocations_file_dir, "w") as f:
        
        
        for i in resource.allocation.keys():

            res_list = []
            for j in resource.allocation[i]:
                res = j.name
                count = resource.allocation[i][j]
                res_list.append((res, count))

            total_build_requirement = sum([count for res,count in res_list])
            alloc_count = len(res_list)

            f.write(f"[{i.name}] {total_build_requirement} total, {alloc_count} resources\n")
            for (res, count) in res_list:
                f.write(f"\t{res}... {count:<6}... {count * 100 / total_build_requirement:.2f}%\n")
            f.write("\n")

            if alloc_count > 2:
                remaining_alloc = total_build_requirement
                skip = False
                for index, (ares, acount) in enumerate(res_list):
                    
                    if not skip:
                        if remaining_alloc > 0:

                            # last allocation is straight out
                            if alloc_count - 1 == index:
                                f.write(f"\tv [{acount}] {ares} \n")
                                remaining_alloc = 0

                            # last two allocations are left and right
                            elif alloc_count - 2 == index:
                                next_res_name = res_list[index+1][0]
                                next_res_count = res_list[index+1][1]
                                
                                remaining_alloc -= acount
                                remaining_alloc -= next_res_count

                                left_text = f"[{acount}] {ares}"
                                right_text = f"{next_res_name} [{next_res_count}]"

                                f.write(f"\t< {left_text:<30} v{remaining_alloc:<6} {right_text:>30} >\n")

                                skip = True
                            
                            # last two allocations are left and right
                            else:
                                next_res_name = res_list[index+1][0]
                                next_res_count = res_list[index+1][1]
                                
                                remaining_alloc -= acount
                                remaining_alloc -= next_res_count

                                left_text = f"[{acount}] {ares}"
                                right_text = f"{next_res_name} [{next_res_count}]"

                                f.write(f"\t< {left_text:<30} v{remaining_alloc:<6} {right_text:>30} >\n")

                                skip = True
                    else:
                        skip = False
            
                f.write("\n")
    
    with open(resource_tree_file_dir, "w") as f:
        f.write(resource.ingredient_tree_str)
    
    base_ingredients = [i for i in resource.ingredients_flat if not i.resource.ingredients]

    base_ingredient_starters = {}
    for i in base_ingredients:
        base_ingredient_starters[i] = {}
        if i.resource.name in ["plutonium", "uranium"]:
            base_ingredient_starters[i]["starter qty"] = i.qty * user_starter_period_nuclear
        else:
            base_ingredient_starters[i]["starter qty"] = i.qty * user_starter_period_standard

    base_starter_count = sum([i["starter qty"] for i in base_ingredient_starters.values()])

    for i in base_ingredients:
        base_ingredient_starters[i]["ratio"] = base_ingredient_starters[i]["starter qty"] / base_starter_count

    with open(starters_file_dir, "w") as f:
        f.write("Starters needed for period...\n")
        for interval in range(1,601):
            f.write(f"{interval}: {base_starter_count / interval:.2f}\n")
            for ing in base_ingredients:
                f.write(f"\t{ing.resource.name}: {base_starter_count * base_ingredient_starters[ing]['ratio'] / interval:.2f}")
            f.write("\n")

            # generated rounded up qty for each and sum
            ceil_str = ""
            rounded_sum = 0
            for ing in base_ingredients:
                rounded_qty = ceil(base_starter_count * base_ingredient_starters[ing]['ratio'] / interval)
                rounded_sum += rounded_qty
                ceil_str += f"\t{len(ing.resource.name) * ' '}     {rounded_qty}"
            ceil_str = "rounded:" + ceil_str[len("rounded:") - 3:] + f"\t{rounded_sum}\n\n"
            f.write(ceil_str)
