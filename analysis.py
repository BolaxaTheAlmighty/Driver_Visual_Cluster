import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler


# Data Reading
data = pd.read_csv("driver_data_accuton.csv")
data = data.set_index(["Brand", "Model"])


# Data Processing, Standardization
h=['Bl', 'Mmd', 'Rms', 'Cms', 'Sd', 'Le', 'Fs','Qts', 'Xmax', 'Pmax', 'frmin', 'frmax', 'spl1w']
non_normalizable_data = ["Re", "z"]

sc = StandardScaler()
scaled = sc.fit_transform(data[h])
scaled_data = pd.DataFrame(scaled, columns = h, index=data.index)

for parameter in non_normalizable_data:
    scaled_data.insert(len(scaled_data.columns), parameter, data[parameter].values)

#Another important things is magnitude, will log some parameters
param_log = ["Mmd", "Rms", "Cms", "Sd", "Le", "Fs", "Xmax", "Pmax"]



#print(data[h].isna().sum()) #4 missing values on min and max frequency

#For now, for testing purposes i will just drop the columns that have missing values
scaled_data = scaled_data.drop(["frmin", "frmax"], axis = 1)
print(scaled_data.columns)



