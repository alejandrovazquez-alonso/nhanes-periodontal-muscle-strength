"""
Dashboard interactivo — Salud periodontal y fuerza muscular (NHANES 2013-2014)
Basado en el proyecto: github.com/alejandrovazquez-alonso/nhanes-periodontal-muscle-strength
"""
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

from modelo import (
    EDAD_MAX_MUESTRA,
    EDAD_MIN_MUESTRA,
    IMC_MAX_HABITUAL,
    IMC_MIN_HABITUAL,
    MODELO,
    error_estandar_aproximado,
    predecir_fuerza,
)

TEAL = "#1f6f6f"
TEAL_LIGHT = "#a9c9c9"
ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / "figures"

st.set_page_config(
    page_title="NHANES — Periodontal y fuerza muscular",
    page_icon="🦷",
    layout="wide",
)


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

    # --- Casos típicos (presets) ---
    st.markdown("**Cargar un caso típico:**")
    presets = {
        "Hombre 70 años": dict(edad=70, sexo="Hombre", imc=27.0, perio="Moderada"),
        "Mujer 40 años": dict(edad=40, sexo="Mujer", imc=24.0, perio="Sin afectación / leve"),
        "Hombre 55 años, periodontitis severa": dict(
            edad=55, sexo="Hombre", imc=30.0, perio="Severa"
        ),
    }
    preset_cols = st.columns(len(presets))
    for col, (nombre, valores) in zip(preset_cols, presets.items()):
        if col.button(nombre, use_container_width=True):
            st.session_state["edad_input"] = valores["edad"]
            st.session_state["sexo_input"] = valores["sexo"]
            st.session_state["imc_input"] = valores["imc"]
            st.session_state["perio_input"] = valores["perio"]

    st.divider()

    col1, col2 = st.columns([1, 1.3])

    with col1:
        edad = st.slider(
            "Edad (años)",
            min_value=EDAD_MIN_MUESTRA,
            max_value=EDAD_MAX_MUESTRA,
            value=55,
            key="edad_input",
        )
        st.caption(
            f"NHANES censura la edad a {EDAD_MAX_MUESTRA} años en los ficheros públicos: "
            "nadie en la muestra real tiene una edad registrada mayor."
        )
        sexo_label = st.radio("Sexo", ["Hombre", "Mujer"], horizontal=True, key="sexo_input")
        sexo = "hombre" if sexo_label == "Hombre" else "mujer"
        imc = st.slider(
            "IMC (kg/m²)", min_value=15.0, max_value=50.0, value=27.0, step=0.5, key="imc_input"
        )
        if imc < IMC_MIN_HABITUAL or imc > IMC_MAX_HABITUAL:
            st.caption(
                f"⚠️ IMC fuera del rango clínico habitual en adultos "
                f"({IMC_MIN_HABITUAL}-{IMC_MAX_HABITUAL} kg/m²). La predicción en este "
                "extremo es menos fiable: hay pocos o ningún caso así en la muestra de "
                "entrenamiento."
            )
        periodontitis_label = st.selectbox(
            "Severidad periodontal",
            ["Sin afectación / leve", "Moderada", "Severa"],
            key="perio_input",
        )
        periodontitis_map = {
            "Sin afectación / leve": "sin_leve",
            "Moderada": "moderada",
            "Severa": "severa",
        }
        periodontitis = periodontitis_map[periodontitis_label]

        prediccion = predecir_fuerza(edad, sexo, imc, periodontitis)
        se_aprox = error_estandar_aproximado(edad, sexo, imc, periodontitis)
        ci_low, ci_high = prediccion - 1.96 * se_aprox, prediccion + 1.96 * se_aprox

    with col2:
        st.metric("Fuerza de prensión estimada", f"{prediccion:.1f} kg")
        st.caption(
            f"Intervalo aproximado (95%): **{ci_low:.1f} – {ci_high:.1f} kg**. "
            "Aproximación que combina los errores estándar de cada coeficiente sin "
            "considerar sus covarianzas ni la variabilidad individual real; úsese como "
            "referencia orientativa, no como intervalo estadístico riguroso."
        )

        base = MODELO["intercept"]["coef"]
        efecto_perio = MODELO["periodontitis"]["niveles"][periodontitis]["coef"]
        efecto_sexo = MODELO["sexo"]["niveles"][sexo]["coef"]
        efecto_edad = MODELO["edad"]["coef_por_anio"] * edad
        efecto_imc = MODELO["imc"]["coef_por_unidad"] * imc

        componentes = [
            ("Intercepto (base)", base),
            (f"Periodontal ({periodontitis_label})", efecto_perio),
            (f"Sexo ({sexo_label})", efecto_sexo),
            (f"Edad ({edad} años)", efecto_edad),
            (f"IMC ({imc} kg/m²)", efecto_imc),
        ]

        st.markdown("**Desglose de la predicción:**")
        etiquetas = [c[0] for c in componentes][::-1]
        valores = [c[1] for c in componentes][::-1]
        colores = [TEAL if v >= 0 else "#b5533c" for v in valores]

        fig, ax = plt.subplots(figsize=(6, 3))
        ax.barh(etiquetas, valores, color=colores)
        ax.axvline(0, color="#333", linewidth=0.8)
        ax.set_xlabel("Contribución a la fuerza estimada (kg)")
        for i, v in enumerate(valores):
            ax.text(v, i, f" {v:+.1f}", va="center",
                     ha="left" if v >= 0 else "right", fontsize=9)
        fig.tight_layout()
        st.pyplot(fig)

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

    fig_col1, fig_col2 = st.columns(2)

    with fig_col1:
        st.markdown("#### Figura 1 — La relación cruda es engañosa")
        st.image(
            str(FIGURES / "fig1_fuerza_periodontitis.png"),
            caption="Fuerza de prensión por severidad periodontal (datos reales)",
            width=480,
        )
        st.caption(
            "A simple vista, la fuerza parece plana entre grupos de severidad "
            "periodontal. Esto es lo que motiva el ajuste por confusores en el modelo."
        )

    with fig_col2:
        st.markdown("#### Figura 2 — Estructura de confusión")
        st.image(
            str(FIGURES / "fig7_correlaciones.png"),
            caption="Matriz de correlaciones entre variables",
            width=480,
        )
        st.caption(
            "La edad correlaciona negativamente con la fuerza (r = -0.33) y "
            "positivamente con la pérdida de inserción (r = 0.25): la edad confunde "
            "la relación periodontal-fuerza desde ambos lados. El número de dientes "
            "funcionales correlaciona negativamente con la pérdida de inserción "
            "(r = -0.51) y positivamente con la fuerza (r = 0.17), sugiriendo una vía "
            "nutricional independiente."
        )

    st.markdown("#### Figura 3 — Validación de escalabilidad (datos sintéticos, hasta 50M registros)")
    fig_col3, fig_col4 = st.columns([1, 1])
    with fig_col3:
        st.image(
            str(FIGURES / "fig11_escalabilidad_spark.png"),
            caption="Escalabilidad del procesamiento en Spark",
            width=480,
        )
    with fig_col4:
        st.caption(
            "El tiempo de lectura se mantiene casi constante entre escalas gracias a "
            "la optimización de metadatos de Parquet y la evaluación perezosa de "
            "Spark; la agregación escala de forma sub-lineal. Leer 50M de registros "
            "con pandas fue imposible (proceso eliminado por falta de RAM), mientras "
            "que Spark lo procesó sin problemas."
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
