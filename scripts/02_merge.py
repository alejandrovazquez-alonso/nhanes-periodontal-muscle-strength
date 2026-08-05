"""Paso 02 - Une las 12 tablas NHANES por SEQN (sin derivar aun)."""
import warnings
import pandas as pd
from config import RAW, INTERIM, FILES, COL_ID

warnings.simplefilter("ignore")  # silencia los PerformanceWarning de read_sas


def leer(fichero):
    return pd.read_sas(RAW / fichero, format="xport")


def main():
    # DEMO como tabla base
    print("Leyendo DEMO...")
    merged = leer(FILES["DEMO"])
    print(f"  DEMO: {merged.shape[0]} filas, {merged.shape[1]} columnas")

    # Pegar las demas por SEQN
    for nombre, fichero in FILES.items():
        if nombre == "DEMO":
            continue
        df = leer(fichero)
        print(f"Uniendo {nombre}: {df.shape[0]} filas, {df.shape[1]} columnas")
        merged = merged.merge(df, on=COL_ID, how="left")

    print(f"\nRESULTADO: {merged.shape[0]} filas, {merged.shape[1]} columnas")
    destino = INTERIM / "nhanes_merged_raw.parquet"
    merged.to_parquet(destino, index=False)
    print(f"Guardado en: {destino}")


if __name__ == "__main__":
    main()
