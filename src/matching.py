def normalize_allergen_list(allergen_list, normalize_text):
    return {normalize_text(allergen) for allergen in allergen_list}


def flag_matching_ingredients(ingredient_records, normalized_allergens):

    result = []

    for ingredient in ingredient_records:
        # Does any user defined allergen match this ingredient
        matched_allergens = []
        parent_allergens = []
        url = []

        for allergen in normalized_allergens:
            parent_name = allergen["item_name"]
            related_names = allergen["allergens"]
            parent_url = allergen["url"]

            for individual_allergen in related_names:
                if individual_allergen in ingredient["ingredient_text"]:
                    matched_allergens.append(individual_allergen.title())
                    parent_allergens.append(parent_name)
                    url.append(parent_url)

        new_ingredient = ingredient.copy()
        new_ingredient["matched_allergens"] = matched_allergens
        new_ingredient["parent_allergen"] = parent_allergens
        new_ingredient["url"] = url
        new_ingredient["is_match"] = len(matched_allergens) > 0

        result.append(new_ingredient)

    return result
