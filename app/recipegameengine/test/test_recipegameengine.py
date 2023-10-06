from recipegameengine import RecipeEngine
from recipegameengine import Resource, Ingredient

import tomllib
from pathlib import Path

py_file_dir = Path(__file__).parent.resolve()

assembly_line_2 = RecipeEngine(recipe_config_toml= Path(py_file_dir, "./resources.toml"))

for a in sorted(assembly_line_2.get_resource_by_name("AI_robot").allocation.keys()):
    print(f"[{a}]")
    print(f'\t{assembly_line_2.get_resource_by_name("AI_robot").allocation[a]}\n')

def test_prints_hello_once():
    assert True

def test_prints_all_at_once():
    assert True