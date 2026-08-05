# Dataset: NHANES 2013-2014

El dataset utilizado es público y pertenece al National Health and Nutrition
Examination Survey (NHANES), publicado por los Centers for Disease Control
and Prevention (CDC) de Estados Unidos, ciclo 2013-2014.

Página oficial del ciclo: https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?BeginYear=2013

Por ser un dataset abierto, y siguiendo el enunciado de la actividad ("el
dataset utilizado si es abierto, o la URL de donde se ha obtenido"), aquí se
indican las URL directas de descarga en lugar de incluir los binarios
`.XPT` en el .zip.

## Tablas utilizadas (12) y URL de descarga directa

Descargar cada archivo y colocarlo en `data/raw/`:

| Tabla | Contenido | URL |
|---|---|---|
| DEMO_H | Demografía, socioeconómico, pesos muestrales | https://wwwn.cdc.gov/Nchs/Nhanes/2013-2014/DEMO_H.XPT |
| MGX_H | Fuerza de prensión (eje muscular) | https://wwwn.cdc.gov/Nchs/Nhanes/2013-2014/MGX_H.XPT |
| OHXPER_H | Examen periodontal (eje dental) | https://wwwn.cdc.gov/Nchs/Nhanes/2013-2014/OHXPER_H.XPT |
| OHXDEN_H | Dentición (recuento de dientes) | https://wwwn.cdc.gov/Nchs/Nhanes/2013-2014/OHXDEN_H.XPT |
| BMX_H | Medidas corporales (IMC) | https://wwwn.cdc.gov/Nchs/Nhanes/2013-2014/BMX_H.XPT |
| SMQ_H | Tabaquismo | https://wwwn.cdc.gov/Nchs/Nhanes/2013-2014/SMQ_H.XPT |
| PAQ_H | Actividad física | https://wwwn.cdc.gov/Nchs/Nhanes/2013-2014/PAQ_H.XPT |
| DIQ_H | Diabetes | https://wwwn.cdc.gov/Nchs/Nhanes/2013-2014/DIQ_H.XPT |
| ALQ_H | Alcohol | https://wwwn.cdc.gov/Nchs/Nhanes/2013-2014/ALQ_H.XPT |
| DXX_H | Composición corporal (DXA) | https://wwwn.cdc.gov/Nchs/Nhanes/2013-2014/DXX_H.XPT |
| OHQ_H | Salud oral autoinformada | https://wwwn.cdc.gov/Nchs/Nhanes/2013-2014/OHQ_H.XPT |
| VID_H | Vitamina D | https://wwwn.cdc.gov/Nchs/Nhanes/2013-2014/VID_H.XPT |

Documentación/diccionario de cada tabla (mismo prefijo, extensión `.htm`
en lugar de `.XPT`), por ejemplo:
https://wwwn.cdc.gov/Nchs/Nhanes/2013-2014/DEMO_H.htm

## Descarga por script (opcional)

```python
import urllib.request
from pathlib import Path

BASE = "https://wwwn.cdc.gov/Nchs/Nhanes/2013-2014/"
TABLAS = ["DEMO_H", "MGX_H", "OHXPER_H", "OHXDEN_H", "BMX_H", "SMQ_H",
          "PAQ_H", "DIQ_H", "ALQ_H", "DXX_H", "OHQ_H", "VID_H"]

Path("data/raw").mkdir(parents=True, exist_ok=True)
for tabla in TABLAS:
    url = BASE + tabla + ".XPT"
    destino = f"data/raw/{tabla}.XPT"
    print("Descargando", tabla)
    urllib.request.urlretrieve(url, destino)
print("Descarga completa.")
```

## Datos antes y después del preprocesado

- **Antes del preprocesado:** los 12 archivos `.XPT` originales (ver tabla
  arriba), sin modificar, tal como los distribuye la CDC.
- **Después del preprocesado:** el pipeline genera, en este orden:
  1. `data/interim/nhanes_merged_raw.parquet` — las 12 tablas unidas por
     `SEQN` (10.175 filas x 1.056 columnas), sin derivar variables aún
     (`02_merge.py`).
  2. `data/processed/nhanes_core.parquet` — variables núcleo derivadas:
     `ppd_medio`, `cal_medio`, `n_dientes`, fuerza de prensión, IMC, etc.
     (`03_preprocesado.py`).
  3. `data/processed/nhanes_real_clean.parquet` — muestra final filtrada
     y clasificada (3.389 participantes), la que se usa en el análisis
     clínico (`03b_filtrado.py`).

Estos tres ficheros parquet no se incluyen en este .zip porque se generan
al ejecutar el pipeline sobre los `.XPT` descargados; no son necesarios
como entrega aparte según el enunciado, que pide el dataset original (o
su URL) y el código para reproducir el preprocesado.

## Orden de ejecución del pipeline

```
config.py                      # configuración compartida (rutas, columnas, semilla)
02_merge.py                    # une las 12 tablas por SEQN
02b_exploracion_inicial.py     # exploración inicial del dataset limpio
02c_composicion_muestra.py     # Figura 20 (composición de la muestra real)
03_preprocesado.py             # deriva las variables núcleo
03b_filtrado.py                # filtra población adulta y clasifica periodontitis
03c_calidad_datos.py           # valores faltantes y atípicos
04_analisis_real.py            # modelo OLS y Figuras 1-2 (datos reales)
04b_visualizaciones.py         # Figuras 3-7 (EDA datos reales)
05_generar_sintetico.py N      # genera réplica sintética de N registros por lotes
06_spark_escalabilidad.py      # mide escalabilidad en Spark a 4 escalas, Figura 11/14
08a_spark_correlacion.py       # validación de fidelidad: correlaciones y Figuras 12-13
08b_spark_dientes.py           # Figura 17 (dentición, sintético 50M)
08c_spark_sarcopenia.py        # Figura 18 (fuerza baja, sintético 50M)
08d_spark_perio_sexo.py        # Figura 19 (periodontitis por sexo, sintético 50M)
08e_spark_composicion.py       # Figura 21 (composición muestra sintética)
generar_informe.py             # genera el PDF final con ReportLab a partir de results/
```

## Entorno de ejecución

- Máquina virtual OpenNebula, Debian 12 - BigTop V2.0.
  - MV ID 7731 (Alejandro Vázquez Alonso)
  - MV ID 4122 (Daniel Vidal Silván)
- Python 3.11/3.12, Spyder IDE, Apache Spark en modo local, pandas,
  matplotlib, statsmodels, ReportLab.

## Licencia

Este trabajo se entrega bajo licencia Creative Commons
Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0).
El dataset NHANES es de dominio público, distribuido por la CDC/NCHS.
