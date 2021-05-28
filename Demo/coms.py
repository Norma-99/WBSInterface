import pandas as pd
from Demo.predict import SamplePredict
from Demo.preprocessing import SamplePreprocessing
import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow import keras

class Analyzer:
	def __init__(self):
		self.database = pd.read_csv("Demo/Datasets/database.csv", delimiter=",")
		self.df = pd.DataFrame()

	def predict(self, url:str):
		self.df = self.database.loc[self.database['url'] == url]

		if len(self.df.index) != 0:
			print("Database prediction")
			model = keras.models.load_model("Demo/Results/model.h5")
			del self.df['url'], self.df['label']
			return model.predict(self.df)

		else:
			print("Sample prediction")
			return SamplePredict(url, "Demo/Results/model.h5").predict()
		
