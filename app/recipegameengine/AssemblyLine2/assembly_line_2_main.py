from recipegameengine import RecipeEngine
from recipegameengine import Resource, Ingredient
from recipegameengine import get_starters_required
from allocation_file import generate_allocation_file, generate_straight_split_string, generate_RSD_split_string

from pathlib import Path
import os
import shutil

from math import ceil


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
for filename in os.listdir(py_file_dir):
    if filename[-5:] == ".toml":
        toml_file_name = filename
        break

if toml_file_name is None:
    raise FileNotFoundError("Could not find .toml file to parse as recipe definition")

re = RecipeEngine(Path.joinpath(py_file_dir, toml_file_name))

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
        f.write(generate_allocation_file(resource=resource))

    with open(resource_tree_file_dir, "w") as f:
        f.write(resource.ingredient_tree_str)

    base_ingredients = [i for i in resource.ingredients_flat if not i.resource.ingredients]

    base_ingredient_starters = {}
    for i in base_ingredients:
        base_ingredient_starters[i] = {}
        if i.resource.name in ["plutonium", "uranium"]:
            base_ingredient_starters[i]["starter qty"] = i.qty * 0.5
        else:
            base_ingredient_starters[i]["starter qty"] = i.qty * 0.25

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
