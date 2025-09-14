# app.py
from flask import Flask, request, send_file
from rembg import remove
from PIL import Image
import io

# Create a Flask application
app = Flask(__name__)

# Define the main route for background removal
@app.route('/remove-bg', methods=['POST'])
def remove_bg_api():
    """
    API endpoint to remove image background.
    Expects a POST request with a file in the 'image' field.
    Returns the processed image as a PNG download.
    """
    # Check if the request has a file part
    if 'image' not in request.files:
        return {'error': 'No file uploaded'}, 400

    file = request.files['image']

    # Check if the file is empty
    if file.filename == '':
        return {'error': 'No selected file'}, 400

    # Check if the file is an allowed image type
    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        try:
            # Open the uploaded image
            input_image = Image.open(file.stream)

            # Process the image with rembg
            output_image = remove(input_image)

            # Save the result to a bytes buffer (in-memory file)
            img_byte_arr = io.BytesIO()
            output_image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)  # Move to the beginning of the BytesIO object

            # Send the result back as a downloadable file
            return send_file(
                img_byte_arr,
                mimetype='image/png',
                as_attachment=True,
                download_name='introibrotech-bg-removed.png'
            )

        except Exception as e:
            # Log the error for debugging
            print(f"Error processing image: {str(e)}")
            return {'error': 'Failed to process image. Please ensure it is a valid image file.'}, 500

    else:
        return {'error': 'Invalid file type. Please upload a PNG, JPG, or WEBP image.'}, 400

# Basic health check route
@app.route('/')
def health_check():
    return {'status': 'OK', 'message': 'Introibrotech BG Remover API is running!'}

# This block runs the app if this file is executed directly
if __name__ == '__main__':
    app.run(debug=True)