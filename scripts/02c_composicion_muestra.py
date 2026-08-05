import warnings; warnings.simplefilter("ignore")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from config import PROCESSED, ROOT

TEAL = "#1f6f6f"

df = pd.read_parquet(PROCESSED / "nhanes_real_clean.parquet")
df = df[df["periodontitis"] != "desconocido"]

fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

# Sexo
s = df["sexo"].value_counts()
axes[0].bar(s.index, s.values, color=TEAL)
axes[0].set_title("Distribucion por sexo")
for i, v in enumerate(s.values):
    axes[0].text(i, v + 10, str(v), ha="center")

# Periodontitis
orden = ["sin_leve", "moderada", "severa"]
p = df["periodontitis"].value_counts().reindex(orden)
axes[1].bar(["Sin/leve", "Moderada", "Severa"], p.values, color=TEAL)
axes[1].set_title("Distribucion por severidad periodontal")
for i, v in enumerate(p.values):
    axes[1].text(i, v + 10, str(v), ha="center")

# Etnia (codigos NHANES)
etnias = {1: "Mex-Am", 2: "Hispano", 3: "Blanco", 4: "Negro", 6: "Asiat", 7: "Otro"}
e = df["etnia"].map(etnias).value_counts()
axes[2].bar(e.index, e.values, color=TEAL)
axes[2].set_title("Distribucion por etnia")
axes[2].tick_params(axis="x", rotation=45)

fig.suptitle("Figura 20. Composicion de la muestra (dataset real)", fontsize=13)
fig.tight_layout()
fig.savefig(ROOT / "results" / "fig20_composicion_muestra.png", dpi=150)
print("Figura 20 guardada.")
