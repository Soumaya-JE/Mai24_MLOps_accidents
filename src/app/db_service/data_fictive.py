import pandas as pd
from imblearn.over_sampling import SMOTE

df = pd.read_csv('data_2005a2021_final.csv')
colonnes_initiales = df.columns

X = df.drop(['num_acc', 'grav'], axis=1) 
y = df['grav']

# On fait un over sampling pour générer de nouvelles données
smote = SMOTE()
X_resampled, y_resampled = smote.fit_resample(X, y)

df_resampled = pd.DataFrame(X_resampled, columns=X.columns)
df_resampled['grav'] = y_resampled

# On crée de nouveau num d'accidents à partir du dernier numéro du dernier accident de la bdd
new_num_acc = range(df['num_acc'].max() + 1, df['num_acc'].max() + 1 + len(df_resampled))
df_resampled['num_acc'] = new_num_acc

# On remet les colonnes dans l'ordre initial et on ne conserve que les nouvelles données
df_resampled = df_resampled[colonnes_initiales]
df_new_data = df_resampled[~df_resampled.isin(df)].dropna()

# On sauvegarde le fichier qui sera à intégrer dans la bdd postgreSql des accidents, dans la table data_accidents
df_new_data.to_csv('data_fictive.csv', index=False)

print(f"{len(df_new_data)} nouvelles lignes sauvegardées dans 'data_fictive.csv'.")
