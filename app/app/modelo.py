"""
Logica del modelo OLS reconstruido a mano, separada de la interfaz Streamlit.

Se mantiene en un modulo aparte (sin importar streamlit) para poder testear
predecir_fuerza() y error_estandar_aproximado() de forma aislada y rapida,
sin arrastrar la ejecucion de toda la interfaz (sliders, columnas, etc.).
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts"

# Rangos observados en la muestra real (NHANES 2013-2014, adultos >=30 años).
# La edad esta censurada ("topcoded") a 80 en los ficheros publicos de NHANES:
# nadie en la muestra tiene una edad registrada mayor a 80.
EDAD_MIN_MUESTRA, EDAD_MAX_MUESTRA = 30, 80
IMC_MIN_HABITUAL, IMC_MAX_HABITUAL = 16.0, 45.0  # rango clinico habitual en adultos


def cargar_modelo():
    with open(ARTIFACTS / "coeficientes_modelo.json", encoding="utf-8") as f:
        return json.load(f)


MODELO = cargar_modelo()


def predecir_fuerza(edad, sexo, imc, periodontitis):
    """Reconstruye a mano la prediccion del modelo OLS (statsmodels) original."""
    coef = MODELO["intercept"]["coef"]
    coef += MODELO["periodontitis"]["niveles"][periodontitis]["coef"]
    coef += MODELO["sexo"]["niveles"][sexo]["coef"]
    coef += MODELO["edad"]["coef_por_anio"] * edad
    coef += MODELO["imc"]["coef_por_unidad"] * imc
    return coef


def error_estandar_aproximado(edad, sexo, imc, periodontitis):
    """SE aproximado de la prediccion media, combinando los SE de cada coeficiente.

    Simplificacion: asume independencia entre coeficientes (ignora covarianzas
    reales del modelo) y NO incluye la varianza residual individual, por lo que
    es un intervalo para el valor medio esperado del grupo, no para una persona
    concreta. Sirve como aproximacion ilustrativa, no como intervalo estadistico
    riguroso.
    """
    se_intercept = MODELO["intercept"]["std_err"]
    se_perio = MODELO["periodontitis"]["niveles"][periodontitis].get("std_err", 0.0)
    se_sexo = MODELO["sexo"]["niveles"][sexo].get("std_err", 0.0)
    se_edad = MODELO["edad"]["std_err"] * edad
    se_imc = MODELO["imc"]["std_err"] * imc
    return math.sqrt(se_intercept**2 + se_perio**2 + se_sexo**2 + se_edad**2 + se_imc**2)
