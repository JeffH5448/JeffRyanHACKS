import cv2
from pyzbar.pyzbar import decode
import requests

def get_nutrition_info(barcode):
    api_url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        if data['product']:
            food_item = data['product']
            return {
                'product_name': food_item.get('product_name', 'Unknown'),
                'nutritional_info': food_item.get('nutriments', 'Nutritional information not available')
            }
    return None

def main():
    capture = cv2.VideoCapture(0)  # Use 0 for the default camera
    last_barcode = None
    nutrition_info = {}

    while True:
        ret, frame = capture.read()
        if not ret:
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Decode barcodes from the frame
        decoded_objects = decode(gray_frame)
        
        if decoded_objects:
            barcode = decoded_objects[0].data.decode('utf-8')
            if barcode != last_barcode:
                nutrition_info = get_nutrition_info(barcode)
                last_barcode = barcode  # Update the last barcode processed

        # Draw the smaller rectangle for displaying nutritional information
        height, width = frame.shape[:2]
        box_width = 250  # Reduced width
        box_height = height // 4  # Quarter of the screen height
        top_left_x = width - box_width
        top_left_y = 10  # Position slightly down from the top

        cv2.rectangle(frame, (top_left_x, top_left_y), (width, top_left_y + box_height), (255, 255, 255), -1)

        # Display nutritional info in the smaller rectangle if available
        if nutrition_info:
            product_name = nutrition_info.get('product_name', 'Unknown')
            nutriments = nutrition_info.get('nutritional_info', {})
            calories = f"Calories: {nutriments.get('energy-kcal', 'N/A')} kcal"
            carbs = f"Carbs: {nutriments.get('carbohydrates_value', 'N/A')} {nutriments.get('carbohydrates_unit', '')}"
            protein = f"Protein: {nutriments.get('proteins_value', 'N/A')} {nutriments.get('proteins_unit', '')}"
            sodium = f"Sodium: {nutriments.get('sodium_value', 'N/A')} {nutriments.get('sodium_unit', '')}"
            sugar = f"Sugar: {nutriments.get('sugars_value', 'N/A')} {nutriments.get('sugars_unit', '')}"

            y_offset = top_left_y + 20  # Start text a bit down from the top of the box
            line_spacing = 20  # Space between lines

            cv2.putText(frame, f"Product: {product_name}", (top_left_x + 10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            cv2.putText(frame, calories, (top_left_x + 10, y_offset + line_spacing), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            cv2.putText(frame, carbs, (top_left_x + 10, y_offset + 2 * line_spacing), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            cv2.putText(frame, protein, (top_left_x + 10, y_offset + 3 * line_spacing), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            cv2.putText(frame, sodium, (top_left_x + 10, y_offset + 4 * line_spacing), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            cv2.putText(frame, sugar, (top_left_x + 10, y_offset + 5 * line_spacing), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        # Show the frame with the nutrition info box
        cv2.imshow('Barcode Scanner', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__": 
    main()
