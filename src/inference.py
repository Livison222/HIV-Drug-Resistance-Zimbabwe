import joblib
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class ModelInference:
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = self.load_model()
        self.cache = {}

    def load_model(self):
        try:
            model = joblib.load(self.model_path)
            logging.info("Model loaded successfully")
            return model
        except Exception as e:
            logging.error(f"Error loading model: {e}")
            raise

    def get_predictions(self, data):
        # Check cache
        data_hash = hash(tuple(map(tuple, data)))
        if data_hash in self.cache:
            logging.info("Returning cached predictions")
            return self.cache[data_hash]

        # Process batch
        try:
            predictions = self.model.predict(data)
            self.cache[data_hash] = predictions
            logging.info("Predictions generated successfully")
            return predictions
        except Exception as e:
            logging.error(f"Error during prediction: {e}")
            raise

if __name__ == '__main__':
    # Example usage
    model_inference = ModelInference('path/to/your/model.joblib')
    # Example input data
    test_data = np.array([[1, 2, 3], [4, 5, 6]])
    predictions = model_inference.get_predictions(test_data)
    print(predictions)