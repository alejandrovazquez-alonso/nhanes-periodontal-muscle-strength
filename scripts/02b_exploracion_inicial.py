import warnings; warnings.simplefilter("ignore")
import pandas as pd
from config import PROCESSED

pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 20)

df = pd.read_parquet(PROCESSED / "nhanes_real_clean.parquet")
df = df[df["periodontitis"] != "desconocido"]

print("=" * 60)
print("EXPLORACION INICIAL - DATASET REAL (NHANES 2013-2014)")
print("=" * 60)

print("\n--- DIMENSIONES ---")
print("Filas:", df.shape[0], "| Columnas:", df.shape[1])

print("\n--- TIPOS DE VARIABLES ---")
print(df.dtypes.to_string())

print("\n--- ESTADISTICOS DESCRIPTIVOS (numericas) ---")
num = ["edad", "fuerza_prension", "cal_medio", "ppd_medio", "n_dientes", "imc", "ratio_pobreza"]
print(df[num].describe().round(2).to_string())

print("\n--- VARIABLES CATEGORICAS ---")
for c in ["sexo", "periodontitis"]:
    print(f"\n{c}:")
    print(df[c].value_counts().to_string())

print("\n" + "=" * 60)
