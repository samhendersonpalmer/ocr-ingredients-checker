import cv2


def draw_matched_ingredients(img, ingredient_records):
    output_img = img.copy()

    for ingredient in ingredient_records:
        if ingredient["is_match"]:
            for word in ingredient["words"]:
                output_img = cv2.rectangle(
                    output_img, word["top_left"], word["bottom_right"], (255, 0, 0), 2
                )
    return output_img
