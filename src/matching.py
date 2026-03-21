def normalize_allergen_list(allergen_list, normalize_text):
    return {normalize_text(allergen) for allergen in allergen_list}


def flag_matching_ingredients(ingredient_records, normalized_allergens):
    for ingredient in ingredient_records:
        # Does any user defined allergen match this ingredient
        matched_allergens = []

        for allergen in normalized_allergens:
            if allergen in ingredient["ingredient_text"]:
                matched_allergens.append(allergen.title())

        ingredient["matched_allergens"] = matched_allergens
        ingredient["is_match"] = len(matched_allergens) > 0

    return ingredient_records
