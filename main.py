import cv2
from pyzbar.pyzbar import decode
import requests

APP_ID = 'dbd1a571'
APP_KEY = '38f057c999dd5e27cdb536142fcb989e'

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
        
        # Check if items were found
        if nut_data['foods'] and 'product' in al_data:
            food_item_nut = nut_data['foods'][0]  
            food_item_al = al_data['product']  

            #is_halal = 'halal' in food_item_al.get('labels_tags', [])
            #is_vegan = 
            #is_vegitarian = 
            #is_gulion_free =
            
            return {
                'product_name': food_item_nut.get('food_name', 'Unknown'),
                'allergens': food_item_al.get('allergens_tags', 'Allergens not available'),
                'labels_tags': food_item_al.get('labels_tags', 'labels_tags not available'),
                'nutritional_info': {
                    'calories': food_item_nut.get('nf_calories', 'Not available'),
                    'carbohydrates': food_item_nut.get('nf_total_carbohydrate', 'Not available'),
                    'protein': food_item_nut.get('nf_protein', 'Not available'),
                    'sodium': food_item_nut.get('nf_sodium', 'Not available'),
                    'sugar': food_item_nut.get('nf_sugars', 'Not available'),
                    'total_fat': food_item_nut.get('nf_total_fat', 'Not available'),
                    'saturated_fat': food_item_nut.get('nf_saturated_fat', 'Not available'),
                    'cholesterol': food_item_nut.get('nf_cholesterol', 'Not available'),
                    'fiber': food_item_nut.get('nf_dietary_fiber', 'Not available'),
                    'vitamin_d': food_item_al.get('nutriments', {}).get('vitamin-d_100g', '0'),
                    'iron': food_item_al.get('nutriments', {}).get('iron_100g', 'Not available'),
                    'calcium': food_item_al.get('nutriments', {}).get('calcium_100g', 'Not available'),
                    'potassium': food_item_al.get('nutriments', {}).get('potassium_100g', 'Not available')
                }
            }
    return None

def main():
    capture = cv2.VideoCapture(0)  # Use 0 for the default camera

    last_barcode = None

    while True:
        # Capture frame-by-frame
        ret, frame = capture.read()
        if not ret:
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Decode barcodes from the frame
        decoded_objects = decode(gray_frame)
        
        if decoded_objects:
            # Get the first decoded barcode value
            barcode = decoded_objects[0].data.decode('utf-8')

            if barcode != last_barcode:  # Only process if it's a new barcode
                nutrition_info = get_nutrition_info(barcode)
                
                if nutrition_info:
                    print(f"\nProduct Name: {nutrition_info['product_name']}")
                    print(f"Allergens: {nutrition_info['allergens']}")
                    print(f"vegan, vegiterian status: {nutrition_info['labels_tags']}")
                    print("Nutritional Information:")
                    print(f"Calories: {nutrition_info['nutritional_info']['calories']} kcal")
                    print(f"Carbohydrates: {nutrition_info['nutritional_info']['carbohydrates']} g")
                    print(f"Protein: {nutrition_info['nutritional_info']['protein']} g")
                    print(f"Sodium: {nutrition_info['nutritional_info']['sodium']} mg")
                    print(f"Sugar: {nutrition_info['nutritional_info']['sugar']} g")
                    print(f"Total Fat: {nutrition_info['nutritional_info']['total_fat']} g")
                    print(f"Saturated Fat: {nutrition_info['nutritional_info']['saturated_fat']} g")
                    print(f"Cholesterol: {nutrition_info['nutritional_info']['cholesterol']} mg")
                    print(f"Fiber: {nutrition_info['nutritional_info']['fiber']} g")
                    print(f"Vitamin D: {nutrition_info['nutritional_info']['vitamin_d']} µg")
                    print(f"Iron: {nutrition_info['nutritional_info']['iron']} mg")
                    print(f"Calcium: {nutrition_info['nutritional_info']['calcium']} mg")
                    print(f"Potassium: {nutrition_info['nutritional_info']['potassium']} mg")
                else:
                    print("Nutritional information not found.")
                
                last_barcode = barcode  # Update the last barcode processed
        
        # Show the frame (optional)
        cv2.imshow('Barcode Scanner', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture when done
    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
