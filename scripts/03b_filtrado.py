"""Paso 03b - Filtra poblacion y clasifica periodontitis (umbrales validados)."""
import warnings
import pandas as pd
from config import PROCESSED, EDAD_MIN_PERIODONTAL

warnings.simplefilter("ignore")


def clasificar_periodontitis(cal):
    # Umbrales por CAL medio (mm), fundamentados en evidencia cientifica y guias
    # clinicas oficiales, validados por Daniel (coautor, dentista).
    if pd.isna(cal):
        return "desconocido"
    if cal < 2.0:
        return "sin_leve"
    if cal < 4.0:
        return "moderada"
    return "severa"


def main():
    df = pd.read_parquet(PROCESSED / "nhanes_core.parquet")
    n0 = len(df)
    print(f"Entrada: {n0} filas")

    # 1) Adultos >= 30
    df = df[df["edad"] >= EDAD_MIN_PERIODONTAL]
    print(f"Tras edad >= {EDAD_MIN_PERIODONTAL}: {len(df)} filas")

    # 2) Exigir fuerza y periodontal medidos
    df = df.dropna(subset=["fuerza_prension", "cal_medio"])
    print(f"Tras exigir fuerza + periodontal: {len(df)} filas")

    # 3) Descartar rangos imposibles
    df = df[(df["fuerza_prension"] > 0) & (df["fuerza_prension"] < 200)]
    df = df[(df["cal_medio"] >= 0) & (df["cal_medio"] < 20)]
    print(f"Tras limpiar rangos: {len(df)} filas")

    # 4) Tipar sexo
    df["sexo"] = df["sexo"].map({1: "hombre", 2: "mujer"})

    # 5) Clasificar periodontitis (umbrales validados por Daniel)
    df["periodontitis"] = df["cal_medio"].apply(clasificar_periodontitis)

    print(f"\nMuestra final: {len(df)} filas ({n0 - len(df)} descartadas)")
    print("\nDistribucion de periodontitis:")
    print(df["periodontitis"].value_counts())
    print("\nDistribucion por sexo:")
    print(df["sexo"].value_counts())

    destino = PROCESSED / "nhanes_real_clean.parquet"
    df.to_parquet(destino, index=False)
    print(f"\nGuardado en: {destino}")


if __name__ == "__main__":
    main()
