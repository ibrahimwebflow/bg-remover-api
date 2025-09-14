# app.py
import os
from flask import Flask, request, send_file
from rembg import remove
from PIL import Image
import io
import logging
import threading

# Configure logging to see errors in Railway's logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Flask application
app = Flask(__name__)

# Configure CORS to allow requests from your GitHub Pages domain
from flask_cors import CORS
# Allow requests from your specific GitHub Pages URL and your localhost for testing
CORS(app, origins=["https://ibrahimwebflow.github.io"])

# --- CRITICAL FIX: Pre-load the rembg model on startup ---
def preload_model():
    """Force the rembg model to download on startup, not on the first request."""
    logger.info("Pre-loading rembg model...")
    try:
        # This forces the download. We use a small test image.
        test_image = Image.new('RGB', (10, 10), color='red')
        remove(test_image)
        logger.info("Rembg model successfully loaded and ready.")
    except Exception as e:
        logger.error(f"Failed to pre-load rembg model: {e}")

# Run the preload in a separate thread so it doesn't block the app from starting
threading.Thread(target=preload_model).start()

# --- Define the main route ---
@app.route('/remove-bg', methods=['POST'])
def remove_bg_api():
    """
    API endpoint to remove image background.
    Expects a POST request with a file in the 'image' field.
    Returns the processed image as a PNG download.
    """
    try:
        # Check if the request has a file part
        if 'image' not in request.files:
            return {'error': 'No file uploaded'}, 400

        file = request.files['image']

        # Check if the file is empty
        if file.filename == '':
            return {'error': 'No selected file'}, 400

        # Check if the file is an allowed image type
        allowed_extensions = ('.png', '.jpg', '.jpeg', '.webp')
        if file and file.filename.lower().endswith(allowed_extensions):
            # Open the uploaded image
            input_image = Image.open(file.stream)

            # Process the image with rembg
            logger.info("Starting background removal...")
            output_image = remove(input_image)
            logger.info("Background removal successful.")

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
        else:
            return {'error': f'Invalid file type. Please upload one of: {", ".join(allowed_extensions)}'}, 400

    except Exception as e:
        # Log the error for debugging in Railway's logs
        logger.error(f"Unexpected error in /remove-bg: {str(e)}", exc_info=True)
        return {'error': 'An internal server error occurred. Please try again.'}, 500

# Basic health check route
@app.route('/')
def health_check():
    return {'status': 'OK', 'message': 'Introibrotech BG Remover API is running!'}

# This block runs the app if this file is executed directly (e.g., for local testing)
if __name__ == '__main__':
    # Use the PORT environment variable provided by Railway, or default to 5000 for local development.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) # Debug must be False in production




