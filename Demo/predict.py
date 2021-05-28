import pickle
import numpy as np
import tensorflow as tf
from tensorflow import keras
from Demo.preprocessing import SamplePreprocessing

class SamplePredict:
    def __init__(self, url:str, model_path):
        self.url = url
        self.df = SamplePreprocessing(self.url).preprocess()
        self.model = keras.models.load_model(model_path)

    def predict(self):
        self.predictions = self.model(self.df)
        print(self.predictions[0])
        return self.predictions[0]
