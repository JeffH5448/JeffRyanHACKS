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
    #image_path = "C:/Users/Ryan/Pictures/Screenshots/crunchy_cheetos_bc.png"

    barcode = read_barcode(image_path)
    
    if barcode:
        print(f"Decoded Barcode: {barcode}")
        nutrition_info = get_nutrition_info(barcode)
        
        if nutrition_info:
            print("Nutritional Information:")
            print(f"Product Name: {nutrition_info['product_name']}")
            print(f"Nutritional Info: {nutrition_info['nutritional_info']}")
        else:
            print("Nutritional information not found.")
    else:
        print("No barcode found in the image.")

if __name__ == "__main__":
    main()

