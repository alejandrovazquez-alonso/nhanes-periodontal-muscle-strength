"""
Dashboard interactivo — Salud periodontal y fuerza muscular (NHANES 2013-2014)
Basado en el proyecto: github.com/alejandrovazquez-alonso/nhanes-periodontal-muscle-strength
"""
import json
from pathlib import Path

import streamlit as st

TEAL = "#1f6f6f"
ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts"
FIGURES = ROOT / "figures"

st.set_page_config(
    page_title="NHANES — Periodontal y fuerza muscular",
    page_icon="🦷",
    layout="wide",
)

with open(ARTIFACTS / "coeficientes_modelo.json", encoding="utf-8") as f:
    MODELO = json.load(f)


def predecir_fuerza(edad, sexo, imc, periodontitis):
    """Reconstruye a mano la prediccion del modelo OLS (statsmodels) original."""
    coef = MODELO["intercept"]["coef"]
    coef += MODELO["periodontitis"]["niveles"][periodontitis]["coef"]
    coef += MODELO["sexo"]["niveles"][sexo]["coef"]
    coef += MODELO["edad"]["coef_por_anio"] * edad
    coef += MODELO["imc"]["coef_por_unidad"] * imc
    return coef


st.markdown(
    f"""
    <div style="padding: 1rem 0 0.5rem 0;">
        <h1 style="color:{TEAL}; margin-bottom:0;">🦷 Salud periodontal y fuerza muscular</h1>
        <p style="color:#666; margin-top:0.2rem;">
            NHANES 2013-2014 · n = 3.389 adultos ≥30 años · Big Data pipeline (Apache Spark)
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.warning(
    "⚠️ **Herramienta educativa / de portfolio.** Reproduce el modelo estadístico "
    "(regresión OLS) del proyecto original. No es una herramienta de decisión clínica "
    "validada. Ver las [limitaciones del proyecto original]"
    "(https://github.com/alejandrovazquez-alonso/nhanes-periodontal-muscle-strength#limitations)."
)

tab_pred, tab_eda = st.tabs(["🔮 Predicción", "📊 Análisis exploratorio"])

# ------------------------------------------------------------------
# TAB 1 — Predicción
# ------------------------------------------------------------------
with tab_pred:
    st.subheader("Estimación de fuerza de prensión")
    st.caption(
        "Introduce los datos de una persona y obtén la fuerza de prensión combinada "
        "estimada según el modelo ajustado (regresión lineal OLS, R² = "
        f"{MODELO['r_squared']})."
    )

    col1, col2 = st.columns([1, 1.3])

    with col1:
        edad = st.slider("Edad (años)", min_value=30, max_value=90, value=55)
        sexo_label = st.radio("Sexo", ["Hombre", "Mujer"], horizontal=True)
        sexo = "hombre" if sexo_label == "Hombre" else "mujer"
        imc = st.slider("IMC (kg/m²)", min_value=15.0, max_value=50.0, value=27.0, step=0.5)
        periodontitis_label = st.selectbox(
            "Severidad periodontal",
            ["Sin afectación / leve", "Moderada", "Severa"],
        )
        periodontitis_map = {
            "Sin afectación / leve": "sin_leve",
            "Moderada": "moderada",
            "Severa": "severa",
        }
        periodontitis = periodontitis_map[periodontitis_label]

        prediccion = predecir_fuerza(edad, sexo, imc, periodontitis)

    with col2:
        st.metric("Fuerza de prensión estimada", f"{prediccion:.1f} kg")

        st.markdown("**Desglose de la predicción:**")
        base = MODELO["intercept"]["coef"]
        efecto_perio = MODELO["periodontitis"]["niveles"][periodontitis]["coef"]
        efecto_sexo = MODELO["sexo"]["niveles"][sexo]["coef"]
        efecto_edad = MODELO["edad"]["coef_por_anio"] * edad
        efecto_imc = MODELO["imc"]["coef_por_unidad"] * imc

        st.table(
            {
                "Componente": [
                    "Intercepto (base)",
                    f"Severidad periodontal ({periodontitis_label})",
                    f"Sexo ({sexo_label})",
                    f"Edad ({edad} años)",
                    f"IMC ({imc} kg/m²)",
                ],
                "Contribución (kg)": [
                    f"{base:+.1f}",
                    f"{efecto_perio:+.1f}",
                    f"{efecto_sexo:+.1f}",
                    f"{efecto_edad:+.1f}",
                    f"{efecto_imc:+.1f}",
                ],
            }
        )

        no_sig = MODELO["periodontitis"]["niveles"][periodontitis].get("p_value", 0) > 0.05
        if no_sig:
            st.caption(
                "⚠️ El coeficiente de 'severa' no fue estadísticamente significativo "
                "en el modelo original (p = 0.753, muestra pequeña, n=172). Interpretar "
                "con cautela."
            )

    st.divider()
    st.caption(
        "El modelo confirma que la fuerza está dominada por **sexo** (-33 kg en mujeres) "
        "y **edad** (-0,5 kg/año); la severidad periodontal tiene un efecto real pero "
        "modesto (~3 kg) una vez controlados esos factores."
    )

# ------------------------------------------------------------------
# TAB 2 — Análisis exploratorio
# ------------------------------------------------------------------
with tab_eda:
    st.subheader("Hallazgos clave del proyecto original")

    c1, c2, c3 = st.columns(3)
    c1.metric("Muestra real", "3.389", "adultos ≥30 años")
    c2.metric("R² modelo ajustado", "0.655")
    c3.metric("Correlación cruda (CAL vs fuerza)", "r = 0.02", "prácticamente nula")

    st.markdown("#### Figura 1 — La relación cruda es engañosa")
    st.image(
        str(FIGURES / "fig1_fuerza_periodontitis.png"),
        caption="Fuerza de prensión por severidad periodontal (datos reales)",
        width=700,
    )
    st.caption(
        "A simple vista, la fuerza parece plana entre grupos de severidad periodontal. "
        "Esto es lo que motiva el ajuste por confusores en el modelo."
    )

    st.markdown("#### Figura 2 — Estructura de confusión")
    st.image(
        str(FIGURES / "fig7_correlaciones.png"),
        caption="Matriz de correlaciones entre variables",
        width=700,
    )
    st.caption(
        "La edad correlaciona negativamente con la fuerza (r = -0.33) y positivamente "
        "con la pérdida de inserción (r = 0.25): la edad confunde la relación "
        "periodontal-fuerza desde ambos lados. El número de dientes funcionales "
        "correlaciona negativamente con la pérdida de inserción (r = -0.51) y "
        "positivamente con la fuerza (r = 0.17), sugiriendo una vía nutricional "
        "independiente."
    )

    st.markdown("#### Figura 3 — Validación de escalabilidad (datos sintéticos, hasta 50M registros)")
    st.image(
        str(FIGURES / "fig11_escalabilidad_spark.png"),
        caption="Escalabilidad del procesamiento en Spark",
        width=700,
    )
    st.caption(
        "El tiempo de lectura se mantiene casi constante entre escalas gracias a la "
        "optimización de metadatos de Parquet y la evaluación perezosa de Spark; la "
        "agregación escala de forma sub-lineal. Leer 50M de registros con pandas fue "
        "imposible (proceso eliminado por falta de RAM), mientras que Spark lo procesó "
        "sin problemas."
    )

    st.divider()
    st.markdown(
        "**Conclusión clínica:** la relación entre salud periodontal y fuerza muscular "
        "es real pero débil, y está dominada por la edad y el sexo como confusores; la "
        "dentición funcional es un predictor más robusto que la severidad periodontal "
        "en sí. **Nota metodológica:** las conclusiones clínicas provienen exclusivamente "
        "de los 3.389 participantes reales; los datos sintéticos se usaron únicamente "
        "para validar escalabilidad, nunca para inferencia clínica."
    )

st.divider()
st.caption(
    "Proyecto completo, código y metodología: "
    "[github.com/alejandrovazquez-alonso/nhanes-periodontal-muscle-strength]"
    "(https://github.com/alejandrovazquez-alonso/nhanes-periodontal-muscle-strength)"
)
