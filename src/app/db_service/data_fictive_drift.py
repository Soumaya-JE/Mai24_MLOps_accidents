import numpy as np
import pandas as pd

data = pd.read_csv("data_fictive.csv")

# Simulation d'un drift dans la colonne continue 'circ' avec ajout d'un biais linéaire
data_drifted = data.copy()
data_drifted['circ'] = data_drifted['circ'] + np.random.normal(loc=0.5, scale=0.1, size=len(data_drifted))

# Simulation d'un drift sur la colonne catégorielle 'lum'
# On modifie la proportion des valeurs dans 'lum' en augmentant artificiellement la proportion de la classe 1 
lum_proportions = data_drifted['lum'].value_counts(normalize=True)
# On augmente la fréquence de la valeur 1
data_drifted['lum'] = data_drifted['lum'].apply(lambda x: 1.0 if np.random.rand() < 0.5 else x)

drifted_file_path = 'data_fictive_drifted.csv'
data_drifted.to_csv(drifted_file_path, index=False)

print(data_drifted.head())
