import os
import cv2
from ultralytics import YOLO
import supervision as sv
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import io

app = Flask(__name__)
CORS(app)

# Load model YOLO
model = YOLO("best.pt")

@app.route('/predict/', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and file.content_type.startswith("image/"):
        try:
            image_bytes = file.read()
            image = cv2.imdecode(np.frombuffer(np.frombuffer(image_bytes, np.uint8), np.uint8), cv2.IMREAD_COLOR)
            height, width, _ = image.shape

            results = model(image, verbose=False)[0]
            detections = sv.Detections.from_ultralytics(results)

            predictions = []
            for i, (xyxy, confidence, class_id) in enumerate(
                    zip(detections.xyxy, detections.confidence, detections.class_id)
            ):
                x_min, y_min, x_max, y_max = map(int, xyxy)
                x_center = (x_min + x_max) / 2
                y_center = (y_min + y_max) / 2
                width_box = x_max - x_min
                height_box = y_max - y_min
                class_name = detections.data["class_name"][i]
                detection_id = str(uuid.uuid4())

                prediction = {
                    "width": width_box,
                    "height": height_box,
                    "x": x_center,
                    "y": y_center,
                    "confidence": float(confidence),
                    "class_id": int(class_id),
                    "class": class_name,
                    "detection_id": i,
                    "parent_id": "image",
                }
                predictions.append(prediction)

            output_json = {
                "model_predictions": {
                    "image": {"width": width, "height": height},
                    "predictions": predictions,
                }
            }

            return jsonify(output_json)

        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'File is not an image'}), 400

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))