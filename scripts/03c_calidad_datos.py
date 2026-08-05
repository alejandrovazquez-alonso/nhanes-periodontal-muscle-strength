import warnings; warnings.simplefilter("ignore")
import pandas as pd
import numpy as np
from config import INTERIM, PROCESSED

print("=" * 55)
print("ANALISIS DE CALIDAD DE DATOS")
print("=" * 55)

# Sobre el merge crudo (antes de limpiar), variables de interes
df = pd.read_parquet(INTERIM / "nhanes_merged_raw.parquet")
cols = ["RIDAGEYR", "RIAGENDR", "BMXBMI", "MGDCGSZ", "INDFMPIR"]
cols = [c for c in cols if c in df.columns]

print("\n--- MISSING VALUES (merge crudo, variables clave) ---")
for c in cols:
    n_miss = df[c].isna().sum()
    print(f"  {c}: {n_miss} faltantes ({round(100*n_miss/len(df),1)}%)")

# Sobre el dataset limpio final
print("\n--- DATASET LIMPIO FINAL ---")
clean = pd.read_parquet(PROCESSED / "nhanes_real_clean.parquet")
print(f"Filas: {len(clean)} | Duplicados SEQN: {clean['SEQN'].duplicated().sum()}")

print("\n--- MISSING en dataset limpio ---")
miss = clean.isna().sum()
for c in miss[miss > 0].index:
    print(f"  {c}: {miss[c]} ({round(100*miss[c]/len(clean),1)}%)")
if miss.sum() == 0:
    print("  Sin valores faltantes tras el preprocesado.")

# Outliers por rango intercuartilico (IQR) en variables numericas
print("\n--- OUTLIERS (metodo IQR) ---")
numericas = ["fuerza_prension", "cal_medio", "ppd_medio", "edad", "imc", "n_dientes"]
for c in numericas:
    q1, q3 = clean[c].quantile(0.25), clean[c].quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - 1.5*iqr, q3 + 1.5*iqr
    n_out = ((clean[c] < lo) | (clean[c] > hi)).sum()
    print(f"  {c}: {n_out} outliers ({round(100*n_out/len(clean),1)}%) [rango normal: {round(lo,1)} a {round(hi,1)}]")

print("\n" + "=" * 55)
