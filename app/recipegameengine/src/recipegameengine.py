from typing import Union
from pathlib import Path
import tomllib

class Resource:

    def __init__(self, name : str) -> None:
        self.name = name
        self.ingredients : list[Ingredient] = []
        self.ingredient_depth = 0
        self.ingredient_tree_str : str = ""
        self.ingredients_flat : list[Ingredient] = []
        self.allocation : dict = {}
        self.price = 0

    def __str__(self) -> str:
        name = f"[{self.name}]"
        ret_str = f"{name:<20}, flat ingredient count: {len(self.ingredients_flat):>3} ... depth: {self.ingredient_depth}"

        return ret_str

    def str_plus_ingredients(self) -> str:
        ret_str = self.__str__()
        ret_str += "Ingredients\n"
        if self.ingredients:
            for i in self.ingredients:
                ret_str += f"\t{i.resource.name:<15} {i.qty:<4}... depth: {i.resource.ingredient_depth}\n"

            return ret_str[:-1]
        else:
            return ret_str

    def str_plus_ingredients_plus_flats(self) -> str:
        ret_str = self.str_plus_ingredients()

        ret_str += "\nFlat Ingredients\n"
        for i in self.ingredients_flat:
            ret_str += f"\t{i.resource.name:<15} {i.qty:<4}... depth: {i.resource.ingredient_depth}\n"

        return ret_str[:-1]

    def __eq__(self, other) -> bool:
        try:
            return True if isinstance(other,Resource) and self.name == other.name else False
        except:
            return False

    def __hash__(self) -> int:
        return hash((self.name, tuple(self.ingredients)))

class Ingredient:

    def __init__(self, resource : Resource, qty : int) -> None:
        self.resource = resource
        self.qty = qty

    def __str__(self) -> str:
        ret_str = f"{self.resource.name} ... {self.qty:.2f}"
        return ret_str

    def __eq__(self, other) -> bool:
        try:
            return True if isinstance(other,Ingredient) and self.resource == other.resource else False
        except:
            return False

    def __hash__(self) -> int:
        return hash((self.resource, 80085))

class RecipeEngine:

    def __init__(self, recipe_config_toml : Union[str, Path]) -> None:
        self.resources : list[Resource] = []

        with open(recipe_config_toml, "rb") as f:
            self.resources = self.parse_recipes(tomllib.load(f))

    def get_resource_by_name(self, name : str) -> Resource:
        try:
            index = [r.name for r in self.resources].index(name)
            return self.resources[index]
        except:
            return None

    def generate_ingredient_tree(self, ingredient : Ingredient, tab_level : int = 0) -> str:

        ret_str = "\t" * tab_level + str(ingredient) + "\n"
        if ingredient.resource.ingredients:

            for i in ingredient.resource.ingredients:
                ret_str += self.generate_ingredient_tree(i, tab_level= tab_level + 1)

        return ret_str

    def generate_resource_tree(self, resource : Resource) -> str:

        ret_str = str(resource) + "\n"

        if resource:
            for i in resource.ingredients:
                ret_str += self.generate_ingredient_tree(ingredient= i, tab_level=1)
        return ret_str

    def generate_resource_tree_by_name(self, name : str) -> str:

        resource = self.get_resource_by_name(name)

        if not resource:
            return None

        return self.generate_resource_tree(self, resource= resource)

    def _get_flat_ingredient_list_by_name(self, name : str) -> list[Ingredient]:

        resource = self.get_resource_by_name(name)
        if not resource:
            return None

        return self._get_flat_ingredient_list(resource=resource)

    def _get_flat_ingredient_list(self, resource : Resource) -> list[Ingredient]:

        ingredients : list[Ingredient] = []

        for ingredient in resource.ingredients:
            ingredients.append(ingredient)
            if ingredient.resource.ingredients:
                for ing in self._get_flat_ingredient_list(ingredient.resource):
                    ingredients.append(Ingredient(resource= ing.resource, qty= ing.qty * ingredient.qty))

        return ingredients

    def get_flat_ingredients(self, resource : Resource) -> list[Ingredient]:

        unsummed_flat_ingredients = self._get_flat_ingredient_list(resource)

        # Count the instance of each
        ret_ingredients : list[Ingredient] = []
        unsummed_resource_set = set(i.resource for i in unsummed_flat_ingredients)
        for r in unsummed_resource_set:
            count = sum([i.qty for i in unsummed_flat_ingredients if i.resource == r])
            ret_ingredients.append(Ingredient(resource= r, qty = count))

        return sorted(ret_ingredients,key= lambda ing: (-ing.resource.ingredient_depth, ing.resource.name))

    def get_flat_ingredients_by_name(self, name : str) -> list[Ingredient]:

        resource = self.get_resource_by_name(name)

        if not resource:
            return None

        return self.get_flat_ingredients(resource= resource)

    def get_ingredient_depth(self, resource : Resource, i_count = 0) -> int:
        if resource.ingredients:
            counts = []
            for i in resource.ingredients:
                counts.append(self.get_ingredient_depth(i.resource, i_count= i_count + 1))
        else:
            counts = [i_count]
        return max(counts)

    def get_allocations(self, resource : Resource) -> dict:

        allocation = {}

        for i in resource.ingredients_flat:
            for j in resource.ingredients_flat:

                # if this ingredient is in the ingredients list of another,
                # then add this ingredient's allocation to this qty
                if i in j.resource.ingredients:
                    index = j.resource.ingredients.index(i)

                    try:
                        _ = allocation[i.resource]
                    except:
                        allocation[i.resource] = {}

                    allocation[i.resource][j.resource] = j.resource.ingredients[index].qty * j.qty

                if i in resource.ingredients:
                    index = resource.ingredients.index(i)

                    try:
                        _ = allocation[i.resource]
                    except:
                        allocation[i.resource] = {}

                    allocation[i.resource][resource] = resource.ingredients[index].qty

        return allocation

    def parse_recipes(self, toml_dict : dict) -> list[Resource]:
        resources : list[Resource] = []

        resource_parsed = True

        while resource_parsed:

            resource_parsed = False # This is cleared on each loop of the while, set if a new resource is parsed

            # loop through all resources
            for resource_name in toml_dict.keys():

                if resource_name in [r.name for r in resources]:
                    continue

                # resource is not valid if it contains an ingredient that hasn't been parsed yet
                resource_valid = True

                # loop through all ingredients
                for ingredient_name in toml_dict[resource_name]["ingredients"].keys():

                    # check if it's an ingredient that hasn't been parsed yet
                    if ingredient_name not in [r.name for r in resources]:
                        resource_valid = False

                # if all ingredients are valid, it's a good resource to parse
                if resource_valid:
                    resource_parsed = True

                    new_resource = Resource(name= resource_name)
                    new_resource.price = toml_dict[resource_name]["price"]

                    for ingredient_name in toml_dict[resource_name]["ingredients"].keys():
                        ingredient_resource_index = [r.name for r in resources].index(ingredient_name)
                        new_resource.ingredients.append(
                            Ingredient(
                                resource=resources[ingredient_resource_index],
                                qty= toml_dict[resource_name]["ingredients"][ingredient_name]
                            )
                        )

                    resources.append(new_resource)

        for r in resources:
            r.ingredient_depth = self.get_ingredient_depth(r)
            r.ingredient_tree_str = self.generate_resource_tree(r)
            r.ingredients_flat = self.get_flat_ingredients(r)
            r.allocation = self.get_allocations(r)

        return resources

def get_starters_required(resource : Resource) -> list[Ingredient]:
    return [Ingredient(resource=i.resource,qty=i.qty) for i in resource.ingredients_flat if not i.resource.ingredients]