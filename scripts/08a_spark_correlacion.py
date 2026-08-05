"""Analisis 1 en Spark - Correlaciones, medias y graficos (sintetico 50M).
Spark calcula sobre 50M; matplotlib grafica el resumen agregado."""
import warnings
warnings.simplefilter("ignore")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from config import ROOT

TEAL = "#1f6f6f"
ROSA = "#c1666b"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

spark = SparkSession.builder.appName("val-correlacion").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

df = spark.read.parquet("file:///home/adminp/tfa-nhanes/data/synthetic/sintetico_50000000")
print("Filas procesadas:", df.count())

# --- Correlaciones ---
print("\n=== CORRELACIONES (sintetico 50M) ===")
for a, b in [("cal_medio", "fuerza_prension"), ("n_dientes", "fuerza_prension"), ("edad", "fuerza_prension")]:
    print("  " + a + " vs " + b + ": r =", round(df.stat.corr(a, b), 3))

# --- Spark agrega; el resumen (pequeño) se lleva a listas para graficar ---
peri = {r["periodontitis"]: (r["fm"], r["n"]) for r in
        df.groupBy("periodontitis").agg(F.avg("fuerza_prension").alias("fm"), F.count("*").alias("n")).collect()}
sexo = {r["sexo"]: r["fm"] for r in
        df.groupBy("sexo").agg(F.avg("fuerza_prension").alias("fm")).collect()}

print("\nPeriodontitis:", {k: round(v[0], 2) for k, v in peri.items()})
print("Sexo:", {k: round(v, 2) for k, v in sexo.items()})

# --- Figura 12: fuerza por periodontitis (equivalente a Fig 1, sobre 50M) ---
orden = ["sin_leve", "moderada", "severa"]
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.bar(["Sin/leve", "Moderada", "Severa"], [peri[c][0] for c in orden], color=TEAL)
for i, c in enumerate(orden):
    ax.text(i, peri[c][0] + 0.3, str(round(peri[c][0], 1)), ha="center")
ax.set_ylabel("Fuerza de prension (kg)")
ax.set_title("Figura 12. Fuerza por periodontitis (sintetico 50M, Spark)")
fig.tight_layout()
fig.savefig(RESULTS / "fig12_spark_periodontitis.png", dpi=150)

# --- Figura 13: fuerza por sexo (equivalente a Fig 4, sobre 50M) ---
fig2, ax2 = plt.subplots(figsize=(6, 4.5))
ax2.bar(["Hombre", "Mujer"], [sexo["hombre"], sexo["mujer"]], color=[TEAL, ROSA])
for i, s in enumerate(["hombre", "mujer"]):
    ax2.text(i, sexo[s] + 0.5, str(round(sexo[s], 1)), ha="center")
ax2.set_ylabel("Fuerza de prension (kg)")
ax2.set_title("Figura 13. Fuerza por sexo (sintetico 50M, Spark)")
fig2.tight_layout()
fig2.savefig(RESULTS / "fig13_spark_sexo.png", dpi=150)

print("\nFiguras 12 y 13 guardadas en results/")
spark.stop()
