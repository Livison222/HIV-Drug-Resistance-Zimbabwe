import pickle
from pathlib import Path

class ModelSaver:
    def __init__(self, model, model_name="model.pkl"):
        self.model = model
        self.model_name = model_name

    def save_model(self):
        with open(self.model_name, 'wb') as file:
            pickle.dump(self.model, file)
        print(f"Model saved as '{self.model_name}'")

    @staticmethod
    def load_model(model_name):
        with open(model_name, 'rb') as file:
            model = pickle.load(file)
        print(f"Model loaded from '{model_name}'")
        return model


def export_from_notebook(model, model_name="model.pkl"):
    saver = ModelSaver(model, model_name)
    saver.save_model()
