import cv2
from pyzbar.pyzbar import decode
import requests

def read_barcode(crunchy_cheetos):
    # Load the image
    image = cv2.imread(crunchy_cheetos)
    print("hello")
    # Decode the barcode
    decoded_objects = decode(image)
    
    if decoded_objects:
        # Return the first decoded barcode value
        print(decoded_objects[0].data.decode('utf-8'))
        return decoded_objects[0].data.decode('utf-8')
    else:
        return None
    
def get_nutrition_info(barcode):
    api_url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    
    # Send the GET request
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        if data['product']:
            # Extracting the nutritional information
            food_item = data['product']
            return {
                'product_name': food_item.get('product_name', 'Unknown'),
                'nutritional_info': food_item.get('nutriments', 'Nutritional information not available')
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
                #print(f"Decoded Barcode: {barcode}")
                nutrition_info = get_nutrition_info(barcode)
                
                if nutrition_info:
                    calories = int(nutrition_info['nutritional_info'].get('energy-kcal', 'Not available'))
                    carbohydrates = str(int(nutrition_info['nutritional_info'].get('carbohydrates_value', 'Not available'))) + nutrition_info['nutritional_info'].get('carbohydrates_unit', 'Not available')
                    protein = str(int(nutrition_info['nutritional_info'].get('proteins_value', 'Not available'))) + nutrition_info['nutritional_info'].get('proteins_unit', 'Not available')
                    sodium = str(int(nutrition_info['nutritional_info'].get('sodium_value', 'Not available'))) + nutrition_info['nutritional_info'].get('sodium_unit', 'Not available')
                    sugar = str(int(nutrition_info['nutritional_info'].get('sugars_value', 'Not available'))) + nutrition_info['nutritional_info'].get('sugars_unit', 'Not available')
                    #print(f"Nutritional Info: {nutrition_info['nutritional_info']}")
                    print(f"\nProduct Name: {nutrition_info['product_name']}")
                    print("Nutritional Information:")
                    print(f"Calories: {calories}kcal")
                    print(f"Carbohydrates: {carbohydrates}")
                    print(f"protein: {protein}")
                    print(f"sodium: {sodium}")
                    print(f"sugar: {sugar}")
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