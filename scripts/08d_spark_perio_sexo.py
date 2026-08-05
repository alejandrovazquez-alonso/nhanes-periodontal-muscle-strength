import warnings; warnings.simplefilter("ignore")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from config import ROOT

spark = SparkSession.builder.appName("val-perio-sexo").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

df = spark.read.parquet("file:///home/adminp/tfa-nhanes/data/synthetic/sintetico_50000000")

# % de cada severidad DENTRO de cada sexo (Spark agrega, se grafica el resumen)
tabla = {r["sexo"] + "_" + r["periodontitis"]: r["n"] for r in
         df.groupBy("sexo", "periodontitis").agg(F.count("*").alias("n")).collect()}

orden = ["sin_leve", "moderada", "severa"]
prop = {}
for s in ["hombre", "mujer"]:
    total = sum(tabla.get(s + "_" + c, 0) for c in orden)
    prop[s] = [100 * tabla.get(s + "_" + c, 0) / total for c in orden]

print("Hombre %:", [round(x, 1) for x in prop["hombre"]])
print("Mujer %:", [round(x, 1) for x in prop["mujer"]])

x = np.arange(3); w = 0.38
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(x - w/2, prop["hombre"], w, label="hombre", color="#1f6f6f")
ax.bar(x + w/2, prop["mujer"], w, label="mujer", color="#c1666b")
ax.set_xticks(x); ax.set_xticklabels(["Sin/leve", "Moderada", "Severa"])
ax.set_ylabel("% dentro de cada sexo")
ax.set_title("Figura 19. Periodontitis por sexo (sintetico 50M, Spark)")
ax.legend()
fig.tight_layout()
fig.savefig(ROOT / "results" / "fig19_spark_perio_sexo.png", dpi=150)
print("Figura 19 guardada.")

spark.stop()
