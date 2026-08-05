"""Paso 06 - Escalabilidad en Spark: mide las 4 escalas y grafica (Spyder, F5)."""
import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from config import ROOT

TEAL = "#1f6f6f"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

spark = SparkSession.builder.appName("NHANES-escalabilidad").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

BASE = "file:///home/adminp/tfa-nhanes/data/synthetic/"
ESCALAS = [100000, 1000000, 10000000, 50000000]

resultados = []
for n in ESCALAS:
    ruta = BASE + "sintetico_" + str(n)

    t0 = time.time()
    df = spark.read.parquet(ruta)
    filas = df.count()
    t1 = time.time()
    t_lectura = round(t1 - t0, 2)

    t2 = time.time()
    df.groupBy("periodontitis").agg(F.avg("fuerza_prension")).collect()
    t3 = time.time()
    t_agg = round(t3 - t2, 2)

    resultados.append((n, filas, t_lectura, t_agg))
    print(">>>", n, "filas:", filas, "| lectura:", t_lectura, "s | agregacion:", t_agg, "s")

print("\n===== TABLA DE ESCALABILIDAD =====")
print("Escala | Lectura+count (s) | Agregacion (s)")
for n, filas, tl, ta in resultados:
    print(str(n) + " | " + str(tl) + " | " + str(ta))

# --- Grafica ---
escalas = [r[0] for r in resultados]
t_agg = [r[3] for r in resultados]
t_lec = [r[2] for r in resultados]

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(escalas, t_agg, "o-", color=TEAL, linewidth=2, markersize=8, label="Agregacion")
ax.plot(escalas, t_lec, "s--", color="#c1666b", linewidth=2, markersize=7, label="Lectura + count")
ax.set_xscale("log")
ax.set_xlabel("Numero de registros (escala log)")
ax.set_ylabel("Tiempo (s)")
ax.set_title("Figura 11. Escalabilidad del procesamiento en Spark")
ax.legend()
ax.grid(True, which="both", ls=":", alpha=0.5)
for x, y in zip(escalas, t_agg):
    ax.annotate(str(y) + "s", (x, y), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=8)
fig.tight_layout()
fig.savefig(RESULTS / "fig11_escalabilidad_spark.png", dpi=150)
print("\nFigura 11 guardada en results/")

spark.stop()
