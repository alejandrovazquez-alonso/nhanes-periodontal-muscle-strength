"""
Tests de sanidad para la reconstruccion manual del modelo OLS.

Verifican que predecir_fuerza() reproduce el valor exacto que dio
statsmodels al ejecutar 04_analisis_real.py sobre los 3.389 participantes
reales, para el caso Hombre / 55 años / IMC 27 / periodontitis moderada,
que fue el output real copiado a mano en artifacts/coeficientes_modelo.json.

Ejecutar con: pytest test_prediccion.py -v
(o simplemente: python3 test_prediccion.py)
"""
import math

from modelo import (
    error_estandar_aproximado,
    predecir_fuerza,
)

# Caso de referencia: intercepto puro (periodontitis=moderada es la categoria
# de referencia, coef=0) + sexo hombre (coef=0) + edad 55 + imc 27.
# Valor esperado calculado a mano a partir de coeficientes_modelo.json:
#   101.3910 + 0.0 + 0.0 + (-0.5018 * 55) + (0.3660 * 27)
#   = 101.3910 - 27.599 + 9.882 = 83.674
CASO_REFERENCIA = dict(edad=55, sexo="hombre", imc=27.0, periodontitis="moderada")
ESPERADO_REFERENCIA = 101.3910 + (-0.5018 * 55) + (0.3660 * 27.0)


def test_prediccion_caso_referencia():
    resultado = predecir_fuerza(**CASO_REFERENCIA)
    assert math.isclose(resultado, ESPERADO_REFERENCIA, abs_tol=0.01), (
        f"Esperado {ESPERADO_REFERENCIA:.3f}, obtenido {resultado:.3f}"
    )


def test_prediccion_sin_leve_suma_3_18():
    """El coeficiente de 'sin_leve' respecto a 'moderada' debe ser +3.1851 kg."""
    base = predecir_fuerza(edad=55, sexo="hombre", imc=27.0, periodontitis="moderada")
    con_sin_leve = predecir_fuerza(edad=55, sexo="hombre", imc=27.0, periodontitis="sin_leve")
    assert math.isclose(con_sin_leve - base, 3.1851, abs_tol=0.001)


def test_prediccion_mujer_resta_33_kg():
    """El coeficiente de sexo mujer debe restar 33.0577 kg respecto a hombre."""
    hombre = predecir_fuerza(edad=55, sexo="hombre", imc=27.0, periodontitis="moderada")
    mujer = predecir_fuerza(edad=55, sexo="mujer", imc=27.0, periodontitis="moderada")
    assert math.isclose(hombre - mujer, 33.0577, abs_tol=0.001)


def test_error_estandar_no_negativo():
    """El error estandar aproximado siempre debe ser positivo."""
    se = error_estandar_aproximado(edad=55, sexo="hombre", imc=27.0, periodontitis="moderada")
    assert se > 0


def test_error_estandar_crece_con_edad():
    """A mayor edad, mayor contribucion de incertidumbre del termino edad*SE_edad."""
    se_joven = error_estandar_aproximado(edad=30, sexo="hombre", imc=27.0, periodontitis="moderada")
    se_mayor = error_estandar_aproximado(edad=80, sexo="hombre", imc=27.0, periodontitis="moderada")
    assert se_mayor > se_joven


if __name__ == "__main__":
    test_prediccion_caso_referencia()
    test_prediccion_sin_leve_suma_3_18()
    test_prediccion_mujer_resta_33_kg()
    test_error_estandar_no_negativo()
    test_error_estandar_crece_con_edad()
    print("Todos los tests pasaron correctamente.")
