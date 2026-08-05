"""Configuracion compartida del pipeline. NHANES 2013-2014."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # project root (one level above scripts/)
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
PROCESSED = ROOT / "data" / "processed"

for _p in (INTERIM, PROCESSED):
    _p.mkdir(parents=True, exist_ok=True)

# Las 12 tablas descargadas, agrupadas por rol
FILES = {
    # --- Base + ejes del estudio ---
    "DEMO": "DEMO_H.XPT",     # demografia + socioeconomico + pesos
    "MGX": "MGX_H.XPT",       # fuerza de prension (eje muscular)
    "OHXPER": "OHXPER_H.XPT", # periodontal (eje dental)
    "OHXDEN": "OHXDEN_H.XPT", # denticion (recuento de dientes)
    "BMX": "BMX_H.XPT",       # medidas corporales (IMC)
    # --- Covariables / confusores ---
    "SMQ": "SMQ_H.XPT",       # tabaquismo
    "PAQ": "PAQ_H.XPT",       # actividad fisica
    "DIQ": "DIQ_H.XPT",       # diabetes
    "ALQ": "ALQ_H.XPT",       # alcohol
    # --- Refuerzos ---
    "DXX": "DXX_H.XPT",       # DXA: masa muscular
    "OHQ": "OHQ_H.XPT",       # salud oral autoinformada
    "VID": "VID_H.XPT",       # vitamina D
}

COL_ID = "SEQN"

# Columnas de DEMO que nos interesan (nombre NHANES -> nombre legible)
DEMO_COLS = {
    "SEQN": "SEQN",
    "RIAGENDR": "sexo",
    "RIDAGEYR": "edad",
    "RIDRETH3": "etnia",
    "INDFMPIR": "ratio_pobreza",
    "WTMEC2YR": "peso_mec",
    "SDMVPSU": "psu",
    "SDMVSTRA": "estrato",
}

# Fuerza de prension combinada (verificado: existe en MGX_H)
GRIP_COL = "MGDCGSZ"

# Codigos centinela del examen periodontal (sitio no medido)
CENTINELAS_PERIO = {99, 99.0}

EDAD_MIN_PERIODONTAL = 30
SEMILLA = 42
