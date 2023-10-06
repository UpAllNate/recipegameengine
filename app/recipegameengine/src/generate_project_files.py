from recipegameengine import RecipeEngine
from recipegameengine import Resource, Ingredient

from pathlib import Path
import os
import shutil

py_file_dir = Path(__file__).parent.resolve()
working_dir = Path().resolve()
project_folder_dir = Path.joinpath(working_dir, "./project_folder")
resources_dir = Path.joinpath(project_folder_dir, "./resources")

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

for resource in re.resources:

    resource_folder = Path.joinpath(resources_dir, "./", resource.name)
    os.mkdir(resource_folder)
    allocations_file_dir = Path.joinpath(resource_folder, "./" + resource.name + "_allocations.txt")

    with open(allocations_file_dir, "w") as f:
        for i in resource.allocation.keys():
            f.write(f"[{i.name}]\n")
            for j in resource.allocation[i]:
                f.write(f"\t{j.name}... {resource.allocation[i][j]}\n")
            f.write("\n")

        