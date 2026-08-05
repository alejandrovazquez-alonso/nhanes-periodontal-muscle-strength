"""Paso 04b - Visualizaciones EDA de las variables (dataset real)."""
import warnings
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from config import PROCESSED, ROOT

warnings.simplefilter("ignore")

TEAL = "#1f6f6f"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)


def main():
    df = pd.read_parquet(PROCESSED / "nhanes_real_clean.parquet")
    df = df[df["periodontitis"] != "desconocido"]
    print(f"Datos: {len(df)} personas")

    # --- 1) Histogramas de variables numericas ---
    numericas = ["fuerza_prension", "cal_medio", "ppd_medio", "edad", "imc", "n_dientes"]
    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    for ax, col in zip(axes.ravel(), numericas):
        ax.hist(df[col].dropna(), bins=35, color=TEAL, alpha=0.8)
        ax.set_title(col)
        ax.set_ylabel("frecuencia")
    fig.suptitle("Figura 3. Distribucion de las variables numericas", fontsize=13)
    fig.tight_layout()
    fig.savefig(RESULTS / "fig3_histogramas.png", dpi=150)
    print("  fig3 histogramas OK")

    # --- 2) Boxplot fuerza por sexo ---
    fig2, ax2 = plt.subplots(figsize=(6, 4.5))
    datos_sexo = [df[df["sexo"] == s]["fuerza_prension"] for s in ["hombre", "mujer"]]
    bp = ax2.boxplot(datos_sexo, labels=["hombre", "mujer"], patch_artist=True)
    for caja in bp["boxes"]:
        caja.set_facecolor(TEAL)
        caja.set_alpha(0.7)
    ax2.set_ylabel("Fuerza de prension (kg)")
    ax2.set_title("Figura 4. Fuerza por sexo")
    fig2.tight_layout()
    fig2.savefig(RESULTS / "fig4_fuerza_sexo.png", dpi=150)
    print("  fig4 fuerza-sexo OK")

    # --- 3) Boxplot fuerza por periodontitis ---
    orden = ["sin_leve", "moderada", "severa"]
    fig3, ax3 = plt.subplots(figsize=(6, 4.5))
    datos_p = [df[df["periodontitis"] == p]["fuerza_prension"] for p in orden]
    bp3 = ax3.boxplot(datos_p, labels=orden, patch_artist=True)
    for caja in bp3["boxes"]:
        caja.set_facecolor(TEAL)
        caja.set_alpha(0.7)
    ax3.set_ylabel("Fuerza de prension (kg)")
    ax3.set_title("Figura 5. Fuerza por severidad periodontal")
    fig3.tight_layout()
    fig3.savefig(RESULTS / "fig5_fuerza_periodontitis.png", dpi=150)
    print("  fig5 fuerza-periodontitis OK")

    # --- 4) Dispersion fuerza vs edad, coloreado por sexo ---
    fig4, ax4 = plt.subplots(figsize=(7, 4.5))
    for s, color in [("hombre", TEAL), ("mujer", "#c1666b")]:
        sub = df[df["sexo"] == s]
        ax4.scatter(sub["edad"], sub["fuerza_prension"], s=8, alpha=0.3, color=color, label=s)
    ax4.set_xlabel("Edad (anios)")
    ax4.set_ylabel("Fuerza de prension (kg)")
    ax4.set_title("Figura 6. Fuerza vs edad por sexo")
    ax4.legend()
    fig4.tight_layout()
    fig4.savefig(RESULTS / "fig6_fuerza_edad.png", dpi=150)
    print("  fig6 fuerza-edad OK")

    # --- 5) Matriz de correlaciones ---
    corr = df[numericas].corr()
    fig5, ax5 = plt.subplots(figsize=(7, 6))
    im = ax5.imshow(corr, cmap="BrBG", vmin=-1, vmax=1)
    ax5.set_xticks(range(len(numericas)))
    ax5.set_xticklabels(numericas, rotation=45, ha="right")
    ax5.set_yticks(range(len(numericas)))
    ax5.set_yticklabels(numericas)
    for i in range(len(numericas)):
        for j in range(len(numericas)):
            ax5.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8)
    fig5.colorbar(im)
    ax5.set_title("Figura 7. Matriz de correlaciones")
    fig5.tight_layout()
    fig5.savefig(RESULTS / "fig7_correlaciones.png", dpi=150)
    print("  fig7 correlaciones OK")

    print(f"\nTodas las figuras en: {RESULTS}")


if __name__ == "__main__":
    main()
