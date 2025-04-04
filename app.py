"""
Flask Application used to serve our model and return a response.
"""
import torch.nn as nn
import torch
import io
import base64
from torchvision import models
from image_transformations import preprocess
from PIL import Image
# Import modules
from flask import Flask, request, jsonify, render_template


# Initialize Flask app
app = Flask(__name__)

# Load any other environment variables or variables here
label_encoding = {"malignant": 0, "benign": 1}

#Load any other environment variables or variables here 
index_to_class_map = {v: k for k, v in label_encoding.items()}

# Load the MobileNetV3 Large pre-trained model
model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT)

# Modify last layer of the model for 2 classes as output
model.classifier[-1] = nn.Linear(1280, 2)

# Load the model from `model/mobilenet_checkpoint.tar` from the model directory.
checkpoint = torch.load('model/mobilenet_checkpoint.tar', weights_only=True)

# Load the parameters from the checkpoint
model.load_state_dict(checkpoint['model_state_dict'])

# Set model to evaluation mode
model.eval()

# Initialize Flask app
app = Flask(__name__)

# --- ADD THIS ROUTE ---
@app.route('/')
def index():
    """Renders the main HTML page for the UI."""
    return render_template('index.html') # Render the template
# --- END OF ADDED ROUTE ---

# Load any other environment variables or variables here
label_encoding = {"malignant": 0, "benign": 1}

# Configuration of the Health endpoint at /health using get method.
@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint to confirm the app is running.
    """
    # Return JSON response with status is healthy with a 200 code
    return jsonify({'status': 'healthy'}), 200


# Configuration of the Prediction endpoint at /predict. Use post method.
@app.route('/predict', methods=['POST'])
def predict():
    # Error handling
    try:
        # Extract Base64 string from request JSON
        data = request.json
        if 'image' not in data:
            # Return an error if there is no image in the request with a 400 status code
            return jsonify({'error': 'No image provided'}), 400

        # Decode the Base64 image string
        image_data = base64.b64decode(data['image'])
        image = Image.open(io.BytesIO(image_data)).convert('RGB')

        # Preprocess the image
        transformed_img = preprocess(image).unsqueeze(0)

        # Perform inference
        with torch.no_grad():
            output = model(transformed_img)
            _, predicted = torch.max(output.data, 1)

        # Return our prediction mapped to real label
        return jsonify({'prediction': index_to_class_map[predicted.item()]})

    # Fail with our error in the response and 500 status code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)