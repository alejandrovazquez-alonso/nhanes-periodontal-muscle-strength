import warnings; warnings.simplefilter("ignore")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from config import ROOT

spark = SparkSession.builder.appName("val-dientes").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

df = spark.read.parquet("file:///home/adminp/tfa-nhanes/data/synthetic/sintetico_50000000")
df = df.withColumn("gd", F.when(F.col("n_dientes") < 20, "pocos").otherwise("funcional"))

print("Corr n_dientes-fuerza:", round(df.stat.corr("n_dientes", "fuerza_prension"), 3))

res = {r["gd"]: r["fm"] for r in df.groupBy("gd").agg(F.avg("fuerza_prension").alias("fm")).collect()}
print("Grupos:", {k: round(v, 1) for k, v in res.items()})

orden = ["pocos", "funcional"]
fig, ax = plt.subplots(figsize=(6, 4.5))
ax.bar(["Pocos (1-19)", "Funcional (20+)"], [res[c] for c in orden], color="#1f6f6f")
ax.set_ylabel("Fuerza de prension (kg)")
ax.set_title("Figura 17. Fuerza segun denticion (sintetico 50M, Spark)")
fig.tight_layout()
fig.savefig(ROOT / "results" / "fig17_spark_dientes.png", dpi=150)
print("Figura 17 guardada.")

spark.stop()
