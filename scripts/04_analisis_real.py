"""Paso 04 - Relacion dental-fuerza sobre datos REALES (conclusiones clinicas)."""
import warnings
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.formula.api as smf
from config import PROCESSED, ROOT

warnings.simplefilter("ignore")

TEAL = "#1f6f6f"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)


def main():
    df = pd.read_parquet(PROCESSED / "nhanes_real_clean.parquet")
    df = df[df["periodontitis"] != "desconocido"]
    print(f"Muestra de analisis: {len(df)} personas\n")

    # 1) Correlacion cruda
    r = df["cal_medio"].corr(df["fuerza_prension"])
    print(f"Correlacion CAL vs fuerza: r = {r:.3f}")

    # 2) Modelo ajustado por edad, sexo, IMC
    modelo = smf.ols(
        "fuerza_prension ~ C(periodontitis) + edad + C(sexo) + imc",
        data=df).fit()
    print("\n--- Modelo (fuerza ~ periodontitis + edad + sexo + imc) ---")
    print(modelo.summary().tables[1])

    with open(RESULTS / "modelo_real.txt", "w") as f:
        f.write(str(modelo.summary()))

    # 3a) Figura: fuerza media por categoria
    orden = ["sin_leve", "moderada", "severa"]
    medias = df.groupby("periodontitis")["fuerza_prension"].agg(["mean", "sem"]).reindex(orden)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(orden, medias["mean"], yerr=medias["sem"], color=TEAL, capsize=4)
    ax.set_ylabel("Fuerza de prension (kg, combinada)")
    ax.set_xlabel("Severidad periodontal")
    ax.set_title("Figura 1. Fuerza de prension por severidad periodontal")
    fig.tight_layout()
    fig.savefig(RESULTS / "fig1_fuerza_periodontitis.png", dpi=150)

    # 3b) Figura: dispersion
    fig2, ax2 = plt.subplots(figsize=(7, 4.5))
    ax2.scatter(df["cal_medio"], df["fuerza_prension"], s=8, alpha=0.3, color=TEAL)
    ax2.set_xlabel("CAL medio (mm)")
    ax2.set_ylabel("Fuerza de prension (kg)")
    ax2.set_title(f"Figura 2. CAL vs fuerza (r = {r:.2f})")
    fig2.tight_layout()
    fig2.savefig(RESULTS / "fig2_cal_fuerza.png", dpi=150)

    print(f"\nFiguras y modelo guardados en: {RESULTS}")


if __name__ == "__main__":
    main()
