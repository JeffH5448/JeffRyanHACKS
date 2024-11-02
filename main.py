import cv2
from pyzbar.pyzbar import decode
import requests

def read_barcode(crunchy_cheetos):
    # Load the image
    image = cv2.imread(crunchy_cheetos)
    
    # Decode the barcode
    decoded_objects = decode(image)
    
    if decoded_objects:
        # Return the first decoded barcode value
        print(decoded_objects[0].data.decode('utf-8'))
        return decoded_objects[0].data.decode('utf-8')
    else:
        return None

def get_nutrition_info(barcode):
    # Replace with your actual API endpoint and key
    api_url = "https://api.nutritionix.com/v1_1/search/"
    app_id = "YOUR_APP_ID"
    app_key = "YOUR_APP_KEY"
    
    # Search for the food product by barcode
    response = requests.get(f"{api_url}{barcode}?results=0:1&fields=food_name,nutritional_info&appId={app_id}&appKey={app_key}")
    
    if response.status_code == 200:
        data = response.json()
        if data['hits']:
            # Extracting the nutritional information
            food_item = data['hits'][0]['fields']
            return food_item
    return None
    
def main():

    image_path = "C:/Users/Ryan/Pictures/Screenshots/crunchy_cheetos_bc.png"

    barcode = read_barcode(image_path)
    
    if barcode:
        print(f"Decoded Barcode: {barcode}")
        nutrition_info = get_nutrition_info(barcode)
        
        if nutrition_info:
            print("Nutritional Information:")
            print(f"Product Name: {nutrition_info.get('food_name')}")
            print(f"Nutritional Info: {nutrition_info.get('nutritional_info')}")
        else:
            print("Nutritional information not found.")
    else:
        print("No barcode found in the image.")

if __name__ == "__main__":
    image_path = "path/to/your/barcode/image.jpg"
    main()