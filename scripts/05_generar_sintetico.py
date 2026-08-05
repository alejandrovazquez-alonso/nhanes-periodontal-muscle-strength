"""Paso 05 - Replica el dataset real a gran escala (bootstrap + ruido) POR LOTES.
Uso: python3 05_generar_sintetico.py NUM_REGISTROS"""
import sys
import time
import shutil
import numpy as np
import pandas as pd
from config import PROCESSED, ROOT, SEMILLA

SYNTH = ROOT / "data" / "synthetic"
SYNTH.mkdir(parents=True, exist_ok=True)

NUM_REGISTROS = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
LOTE = 5000000
NUMERICAS = ["edad", "imc", "fuerza_prension", "ppd_medio", "cal_medio", "n_dientes", "ratio_pobreza"]
RUIDO = 0.03


def generar_lote(df, n, rng):
    idx = rng.integers(0, len(df), size=n)
    syn = df.iloc[idx].reset_index(drop=True).copy()
    for c in NUMERICAS:
        sigma = df[c].std() * RUIDO
        syn[c] = syn[c].values + rng.normal(0, sigma, n)
        syn[c] = np.clip(syn[c], df[c].min(), df[c].max())
        if c == "n_dientes":
            syn[c] = np.round(syn[c])
    return syn


def main():
    df = pd.read_parquet(PROCESSED / "nhanes_real_clean.parquet")
    df = df[df["periodontitis"] != "desconocido"]
    cols = NUMERICAS + ["sexo", "periodontitis"]
    df = df[cols]

    rng = np.random.default_rng(SEMILLA)
    destino = SYNTH / ("sintetico_" + str(NUM_REGISTROS))
    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir()

    t0 = time.time()
    restantes = NUM_REGISTROS
    tanda = 0
    while restantes > 0:
        n = min(LOTE, restantes)
        syn = generar_lote(df, n, rng)
        syn.to_parquet(destino / ("part-" + str(tanda).zfill(3) + ".parquet"), index=False)
        tanda += 1
        restantes -= n
    t1 = time.time()

    print("Generados", NUM_REGISTROS, "registros en", round(t1 - t0, 2), "s ->", destino)


if __name__ == "__main__":
    main()
