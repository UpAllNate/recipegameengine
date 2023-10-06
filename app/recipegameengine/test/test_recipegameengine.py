from recipegameengine import RecipeEngine, Resource, Ingredient
from pathlib import Path

py_file_dir = Path(__file__).parent.resolve()
assembly_line_2 = RecipeEngine(recipe_config_toml= Path.joinpath(py_file_dir, "./Assembly_Line_2.toml"))

def test_all_allocations_populated():
    robot_allocation = assembly_line_2.get_resource_by_name("AI_robot").allocation
    assert robot_allocation != {}
    for a in sorted(robot_allocation.keys(), key= lambda r: r.name):
        assert a.__class__ == Resource
        assert robot_allocation[a].__class__ == dict
        for r in robot_allocation[a].keys():
            assert r.__class__ == Resource
            assert robot_allocation[a][r].__class__ == int