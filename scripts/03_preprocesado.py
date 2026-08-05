"""Paso 03 - Deriva las variables nucleo (ejes del estudio)."""
import re
import warnings
import pandas as pd
from config import INTERIM, PROCESSED, DEMO_COLS, GRIP_COL, COL_ID, CENTINELAS_PERIO

warnings.simplefilter("ignore")


def media_periodontal(df, patron):
    """Media por persona de las columnas que casan el patron, quitando centinelas."""
    cols = [c for c in df.columns if re.fullmatch(patron, c)]
    sub = df[cols].apply(pd.to_numeric, errors="coerce")
    sub = sub.mask(sub.isin(CENTINELAS_PERIO))
    print(f"  patron {patron}: {len(cols)} columnas")
    return sub.mean(axis=1)


def main():
    df = pd.read_parquet(INTERIM / "nhanes_merged_raw.parquet")
    print(f"Entrada: {df.shape[0]} filas, {df.shape[1]} columnas")

    out = pd.DataFrame()
    out[COL_ID] = df[COL_ID]

    # 1) Demografia + covariables base (renombradas)
    for nhanes, legible in DEMO_COLS.items():
        if nhanes in df.columns:
            out[legible] = df[nhanes]

    # 2) IMC (de BMX)
    if "BMXBMI" in df.columns:
        out["imc"] = df["BMXBMI"]

    # 3) Fuerza de prension (de MGX)
    out["fuerza_prension"] = df[GRIP_COL]

    # 4) Derivados periodontales
    print("Derivando periodontal:")
    out["ppd_medio"] = media_periodontal(df, r"OHX\d{2}PC.")
    out["cal_medio"] = media_periodontal(df, r"OHX\d{2}LA.")

    # 5) Recuento de dientes permanentes (valor 2 en OHX##TC)
    tc_cols = [c for c in df.columns if re.fullmatch(r"OHX\d{2}TC", c)]
    out["n_dientes"] = (df[tc_cols].apply(pd.to_numeric, errors="coerce") == 2).sum(axis=1)
    print(f"  recuento dental: {len(tc_cols)} columnas TC")

    print(f"\nSalida: {out.shape[0]} filas, {out.shape[1]} columnas")
    print("Columnas:", list(out.columns))

    destino = PROCESSED / "nhanes_core.parquet"
    out.to_parquet(destino, index=False)
    print(f"Guardado en: {destino}")


if __name__ == "__main__":
    main()
