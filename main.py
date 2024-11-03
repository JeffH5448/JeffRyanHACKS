import cv2
from pyzbar.pyzbar import decode
import requests
import numpy as np
import time 

APP_ID = '6881741f'
APP_KEY = '9b89d4359cc6d75b2b0988742f353235'

def calculate_daily_intake(gender, age, height, weight, activity_level):
    age = int(age)
    height = float(height)
    weight = float(weight)

    if gender.lower() == 'male':
        bmr = 4.536 * weight + 15.88 * height - 5 * age + 5
    elif gender.lower() == 'female':
        bmr = 4.536 * weight + 15.88 * height - 5 * age - 161
    else:
        raise ValueError("Invalid gender input. Please enter 'male' or 'female'.")

    activity_multipliers = {
        "1": 1.2,
        "2": 1.375,
        "3": 1.55,
        "4": 1.725,
        "5": 1.9
    }

    if activity_level not in activity_multipliers:
        raise ValueError("Invalid activity level.")

    daily_caloric_intake = bmr * activity_multipliers[activity_level]
    return daily_caloric_intake

def get_nutrition_info(barcode):
    api_url_nut = f"https://trackapi.nutritionix.com/v2/search/item?upc={barcode}"
    api_url_al = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    
    headers = {
        "x-app-id": APP_ID,
        "x-app-key": APP_KEY,
    }

    response_nut = requests.get(api_url_nut, headers=headers)
    response_al = requests.get(api_url_al)
    
    if response_nut.status_code == 200 and response_al.status_code == 200:
        nut_data = response_nut.json()
        al_data = response_al.json()
        
        #print(al_data)
        if nut_data['foods'] and 'product' in al_data:
            food_item_nut = nut_data['foods'][0]
            food_item_al = al_data['product']
            
            is_halal = True
            is_vegan = False
            is_vegetarian = False
            halal = food_item_al.get('allergens_tags', [])
            labels = food_item_al.get('labels_tags', [])
            ingredients_analysis = food_item_al.get('ingredients_analysis_tags', [])

            if 'en:vegan' in labels or 'en:vegan' in ingredients_analysis:
                is_vegan = True
            if 'en:vegetarian' in labels or 'en:vegetarian' in ingredients_analysis:
                is_vegetarian = True

            non_halal_indicators = ['en:pork', 'en:gel', 'en:alcohol']  # Add other tags if necessary
            for tag in halal + labels + ingredients_analysis:
                if any(non_halal in tag for non_halal in non_halal_indicators):
                    is_halal = False
                    break

            return {
                'product_name': food_item_nut.get('food_name', 'Unknown'),
                'allergens': food_item_al.get('allergens_tags', 'Allergens not available'),
                'is_vegan': is_vegan,
                'is_halal': is_halal,
                'is_vegetarian': is_vegetarian, 
                'nutritional_info': {
                    'calories': food_item_nut.get('nf_calories', '0'),
                    'carbohydrates': food_item_nut.get('nf_total_carbohydrate', '0'),
                    'protein': food_item_nut.get('nf_protein', '0'),
                    'sodium': food_item_nut.get('nf_sodium', '0'),
                    'sugar': food_item_nut.get('nf_sugars', '0'),
                    'total_fat': food_item_nut.get('nf_total_fat', 'no value'),
                    'saturated_fat': food_item_nut.get('nf_saturated_fat', '0'),
                    'cholesterol': food_item_nut.get('nf_cholesterol', '0'),
                    'fiber': food_item_nut.get('nf_dietary_fiber', '0'),
                    'vitamin_d': food_item_al.get('nutriments', {}).get('vitamin-d_value', '0'),
                    'iron': food_item_al.get('nutriments', {}).get('ironvalue', '0')
                     
                }
            }
    return None

def draw_progress_bar(image, nutrient, value, max_value, bar_position):
    bar_width = 400
    bar_height = 30
    x0, y0 = bar_position
    
    try:
        value = float(value)
        max_value = float(max_value)
    except ValueError:
        print(f"Invalid value or max_value for {nutrient}: {value}, {max_value}")
        return
    
    # Draw the background of the progress bar
    cv2.rectangle(image, (x0, y0), (x0 + bar_width, y0 + bar_height), (255, 255, 255), -1)
    
    # Calculate the width of the filled part of the bar
    filled_width = int((value / max_value) * bar_width) if max_value > 0 else 0
    
    # Draw the filled part of the progress bar
    cv2.rectangle(image, (x0, y0), (x0 + filled_width, y0 + bar_height), (0, 255, 0), -1)

    # Add text to display the nutrient value
    percent_text = f"{nutrient}: {value}/{max_value}"
    cv2.putText(image, percent_text, (x0 + 10, y0 + bar_height - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)


def display_popup(image, message, duration=2):
    # Get the dimensions of the image/frame
    height, width = image.shape[:2]

    # Calculate position to center the rectangle and text
    rect_width, rect_height = 400, 100
    x = (width - rect_width) // 2
    y = (height - rect_height) // 2

    # Draw a semi-transparent background rectangle
    overlay = image.copy()
    cv2.rectangle(overlay, (x, y), (x + rect_width, y + rect_height), (0, 0, 0), -1)  # Black rectangle
    alpha = 0.6  # Transparency factor
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

    # Add the centered text in red
    text_x = x + 20
    text_y = y + 60
    cv2.putText(image, message, (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)  # Red text

    # Display the popup for the specified duration
    cv2.imshow('Barcode Scanner', image)
    cv2.waitKey(duration * 1000)


def main():
    # User inputs for dietary preferences
    allergies = input("Please enter any allergies from this list (Peanuts, Tree Nuts, Milk, Eggs, Fish, Soy, Wheat, Gluten, none): ")
    if allergies not in ['Peanuts', 'Tree Nuts', 'Milk', 'Eggs', 'Fish', 'Soy', 'Wheat', 'Gluten', 'none']:
        raise ValueError("Invalid allergies. Please enter 'Peanuts', 'Tree Nuts', 'Milk', 'Eggs', 'Fish', 'Soy', 'Wheat', 'Gluten', 'none'.")

    gender = "male"
    dailycal = calculate_daily_intake(gender, '20', '72', '200', '3')

    dietary_preference = input("Please specify your dietary preference (vegan/vegetarian/halal/none): ").strip().lower()
    if dietary_preference not in ['vegan', 'vegetarian', 'halal', 'none']:
        raise ValueError("Invalid dietary preference. Please enter 'vegan', 'vegetarian', 'halal, or 'none'.")

    # Nutrients to track
    nutrients_to_track = ['calories', 'carbohydrates', 'protein', 'total_fat', 'sodium', 'sugar', 'cholesterol', 'fiber']
    max_nutrient_values = {
        'calories': dailycal,
        'carbohydrates': int((dailycal * 0.55) / 4),
        'protein': int((dailycal * 0.15) / 4),
        'total_fat': int((dailycal * 0.30) / 9),
        'sodium': 2300,
        'sugar': min(50, dailycal * 0.10 / 4),
        'cholesterol': 300,
        'fiber': 25 if gender.lower() == 'female' else 38,
    }

    # Initialize cumulative nutrient values
    cumulative_nutrient_values = {nutrient: 0 for nutrient in nutrients_to_track}

    capture = cv2.VideoCapture(2)
    last_barcode = None

    while True:
        ret, frame = capture.read()
        if not ret:
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        decoded_objects = decode(gray_frame)

        if decoded_objects:
            barcode = decoded_objects[0].data.decode('utf-8')
            nutrition_info = get_nutrition_info(barcode)

            if barcode != last_barcode:  # Only process if it's a new barcode
                if nutrition_info:
                    print(f"\nProduct Name: {nutrition_info['product_name']}")

                    # Check dietary preference
                    if dietary_preference == "vegan" and not nutrition_info.get('is_vegan', False):
                        print("This product is not vegan, and the values will not be added to the cumulative totals.")
                        display_popup(frame, "Not Vegan!", 2)
                        continue
                    if dietary_preference == "vegetarian" and not nutrition_info.get('is_vegetarian'):
                        print("This product is not vegetarian, and the values will not be added to the cumulative totals.")
                        display_popup(frame, "Not Vegetarian!", 2)
                        continue  
                    if dietary_preference == "halal" and not nutrition_info.get('is_halal'):
                        print("This product is not halal, and the values will not be added to the cumulative totals.")
                        display_popup(frame, "Not Halal!", 2)
                        continue
                    
                    # Normalize user input allergies
                    user_allergies = [allergy.strip().lower() for allergy in allergies.split(', ')]
                    print("User Allergies: ", user_allergies)

                    # Get allergens from the nutrition info and normalize them
                    allergens = nutrition_info.get('allergens', [])
                    normalized_allergens = [allergen.split(':')[1].strip().lower() if ':' in allergen else allergen.strip().lower() for allergen in allergens]
                    print("Normalized Allergens: ", normalized_allergens)

                    # Check for any matching allergens
                    if allergies != 'none' and any(allergy in normalized_allergens for allergy in user_allergies):
                        print(f"This product contains allergens: {', '.join(normalized_allergens)}. Values will not be added.")
                        display_popup(frame, "Contains Allergens!", 2)
                        continue

                    # Get nutrient values
                    calories_val = nutrition_info['nutritional_info'].get('calories', '0')
                    carbohydrates_val = nutrition_info['nutritional_info'].get('carbohydrates', '0')
                    protein_val = nutrition_info['nutritional_info'].get('protein', '0')
                    total_fat = nutrition_info['nutritional_info'].get('total_fat', 'Not available')
                    sodium_val = nutrition_info['nutritional_info'].get('sodium', '0')
                    sugar_val = nutrition_info['nutritional_info'].get('sugar', '0')
                    cholesterol_val = nutrition_info['nutritional_info'].get('cholesterol', '0')
                    fiber_val = nutrition_info['nutritional_info'].get('fiber', '0')

                    # Add values to cumulative totals
                    cumulative_nutrient_values['calories'] += int(calories_val) if calories_val != 'Not available' else 0
                    cumulative_nutrient_values['carbohydrates'] += int(carbohydrates_val) if carbohydrates_val != 'Not available' else 0
                    cumulative_nutrient_values['protein'] += int(protein_val) if protein_val != 'Not available' else 0
                    cumulative_nutrient_values['total_fat'] += int(total_fat) if total_fat != 'Not available' else 0
                    cumulative_nutrient_values['sodium'] += int(sodium_val) if sodium_val != 'Not available' else 0
                    cumulative_nutrient_values['sugar'] += int(sugar_val) if sugar_val != 'Not available' else 0
                    cumulative_nutrient_values['cholesterol'] += int(cholesterol_val) if cholesterol_val != 'Not available' else 0
                    cumulative_nutrient_values['fiber'] += int(fiber_val) if fiber_val != 'Not available' else 0

                    # Print cumulative nutrient values
                    for nutrient in nutrients_to_track:
                        print(f"{nutrient.capitalize()}: {cumulative_nutrient_values[nutrient]}")
                else:
                    print("Nutritional information not found.")
                
                last_barcode = barcode  # Update the last barcode processed

        # Draw progress bars for each nutrient
        for i, nutrient in enumerate(nutrients_to_track):
            draw_progress_bar(frame, nutrient, cumulative_nutrient_values[nutrient], max_nutrient_values[nutrient], (50, 50 + i * 40))

        cv2.imshow('Barcode Scanner', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
