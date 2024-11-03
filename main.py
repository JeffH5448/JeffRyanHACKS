import cv2
from pyzbar.pyzbar import decode
import requests

# Replace with your actual Nutritionix app ID and app key
APP_ID = 'dbd1a571'
APP_KEY = '38f057c999dd5e27cdb536142fcb989e'

def get_nutrition_info(barcode):
    api_url = f"https://trackapi.nutritionix.com/v2/search/item?upc={barcode}"
    
    # Set up headers for Nutritionix API authentication
    headers = {
        "x-app-id": APP_ID,
        "x-app-key": APP_KEY,
    }
    
    # Send the GET request
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # Check if items were found
        if data['foods']:
            food_item = data['foods'][0]
            return {
                'product_name': food_item.get('food_name', 'Unknown'),
                'allergens': food_item.get('allergens', 'Allergens not available'),
                'nutritional_info': {
                    'calories': food_item.get('nf_calories', 'Not available'),
                    'carbohydrates': food_item.get('nf_total_carbohydrate', 'Not available'),
                    'protein': food_item.get('nf_protein', 'Not available'),
                    'sodium': food_item.get('nf_sodium', 'Not available'),
                    'sugar': food_item.get('nf_sugars', 'Not available'),
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
                    print(f"\nAllergens: {nutrition_info['allergens']}")
                    print("Nutritional Information:")
                    print(f"Calories: {nutrition_info['nutritional_info']['calories']} kcal")
                    print(f"Carbohydrates: {nutrition_info['nutritional_info']['carbohydrates']} g")
                    print(f"Protein: {nutrition_info['nutritional_info']['protein']} g")
                    print(f"Sodium: {nutrition_info['nutritional_info']['sodium']} mg")
                    print(f"Sugar: {nutrition_info['nutritional_info']['sugar']} g")
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
