import warnings; warnings.simplefilter("ignore")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from config import ROOT

spark = SparkSession.builder.appName("val-sarcopenia").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

df = spark.read.parquet("file:///home/adminp/tfa-nhanes/data/synthetic/sintetico_50000000")

# Umbral de fuerza baja = percentil 20 por sexo (aprox con approxQuantile)
umbrales = {}
for s in ["hombre", "mujer"]:
    q = df.filter(F.col("sexo") == s).approxQuantile("fuerza_prension", [0.20], 0.01)
    umbrales[s] = q[0]
print("Umbrales P20:", {k: round(v, 1) for k, v in umbrales.items()})

# Marca fuerza baja segun umbral del sexo
df = df.withColumn("fuerza_baja",
    ((F.col("sexo") == "hombre") & (F.col("fuerza_prension") <= umbrales["hombre"])) |
    ((F.col("sexo") == "mujer") & (F.col("fuerza_prension") <= umbrales["mujer"])))

# % fuerza baja por periodontitis
res = {r["periodontitis"]: r["p"] * 100 for r in
       df.groupBy("periodontitis").agg(F.avg(F.col("fuerza_baja").cast("double")).alias("p")).collect()}
print("% fuerza baja:", {k: round(v, 1) for k, v in res.items()})

orden = ["sin_leve", "moderada", "severa"]
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.bar(["Sin/leve", "Moderada", "Severa"], [res[c] for c in orden], color="#1f6f6f")
for i, c in enumerate(orden):
    ax.text(i, res[c] + 0.3, str(round(res[c], 1)) + "%", ha="center")
ax.set_ylabel("% con fuerza baja")
ax.set_xlabel("Severidad periodontal")
ax.set_title("Figura 18. Fuerza baja por periodontitis (sintetico 50M, Spark)")
fig.tight_layout()
fig.savefig(ROOT / "results" / "fig18_spark_sarcopenia.png", dpi=150)
print("Figura 18 guardada.")

spark.stop()
