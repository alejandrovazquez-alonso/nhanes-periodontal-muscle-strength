import warnings; warnings.simplefilter("ignore")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from config import ROOT

TEAL = "#1f6f6f"

spark = SparkSession.builder.appName("val-composicion").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

df = spark.read.parquet("file:///home/adminp/tfa-nhanes/data/synthetic/sintetico_50000000")

# Spark cuenta sobre 50M, devuelve resumen pequeno
sexo = {r["sexo"]: r["n"] for r in df.groupBy("sexo").agg(F.count("*").alias("n")).collect()}
peri = {r["periodontitis"]: r["n"] for r in df.groupBy("periodontitis").agg(F.count("*").alias("n")).collect()}

print("Sexo:", sexo)
print("Periodontitis:", peri)

fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

s_ord = ["hombre", "mujer"]
axes[0].bar(["Hombre", "Mujer"], [sexo[k] for k in s_ord], color=TEAL)
axes[0].set_title("Distribucion por sexo")
for i, k in enumerate(s_ord):
    axes[0].text(i, sexo[k], str(sexo[k]), ha="center", va="bottom")

p_ord = ["sin_leve", "moderada", "severa"]
axes[1].bar(["Sin/leve", "Moderada", "Severa"], [peri[k] for k in p_ord], color=TEAL)
axes[1].set_title("Distribucion por severidad periodontal")
for i, k in enumerate(p_ord):
    axes[1].text(i, peri[k], str(peri[k]), ha="center", va="bottom")

fig.suptitle("Figura 21. Composicion de la muestra (sintetico 50M, Spark)", fontsize=13)
fig.tight_layout()
fig.savefig(ROOT / "results" / "fig21_spark_composicion.png", dpi=150)
print("Figura 21 guardada.")

spark.stop()
