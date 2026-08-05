"""
generar_informe.py - Genera el informe del TFA (Módulo 3) en PDF con ReportLab.

EJECUTAR EN LA MV, desde ~/tfa-nhanes, donde están la carpeta results/ (21 figuras)
y los scripts .py del proyecto.

    cd ~/tfa-nhanes
    python3 generar_informe.py

Produce: informe_TFA_M3.pdf en la misma carpeta.

Estilo: teal #1f6f6f, registro impersonal, sin em-dashes, figuras "Figura N".
El anexo lee automáticamente los scripts del proyecto e incrusta su contenido.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                PageBreak, Preformatted, Table, TableStyle)

# ----------------------------------------------------------------------
# Configuración
# ----------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root (one level above scripts/)
RESULTS = os.path.join(ROOT, "results")
SALIDA = os.path.join(ROOT, "informe_TFA_M3.pdf")

TEAL = colors.HexColor("#1f6f6f")
GRIS = colors.HexColor("#555555")

# Scripts a incluir en el anexo (en orden lógico del pipeline)
SCRIPTS_ANEXO = [
    "config.py",
    "02_merge.py",
    "02b_exploracion_inicial.py",
    "02c_composicion_muestra.py",
    "03_preprocesado.py",
    "03b_filtrado.py",
    "03c_calidad_datos.py",
    "04_analisis_real.py",
    "04b_visualizaciones.py",
    "05_generar_sintetico.py",
    "06_spark_escalabilidad.py",
    "08a_spark_correlacion.py",
    "08b_spark_dientes.py",
    "08c_spark_sarcopenia.py",
    "08d_spark_perio_sexo.py",
    "08e_spark_composicion.py",
]

# ----------------------------------------------------------------------
# Estilos
# ----------------------------------------------------------------------
styles = getSampleStyleSheet()

h1 = ParagraphStyle("h1", parent=styles["Heading1"], textColor=TEAL,
                    fontSize=16, spaceBefore=16, spaceAfter=10)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=TEAL,
                    fontSize=13, spaceBefore=12, spaceAfter=6)
body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=10.5,
                      leading=15, alignment=TA_JUSTIFY, spaceAfter=8)
cap = ParagraphStyle("cap", parent=styles["BodyText"], fontSize=9,
                     textColor=GRIS, alignment=TA_CENTER, spaceAfter=14)
code = ParagraphStyle("code", parent=styles["Code"], fontSize=7.2, leading=8.5)
titulo = ParagraphStyle("titulo", parent=styles["Title"], textColor=TEAL,
                        fontSize=20, alignment=TA_CENTER, spaceAfter=6)
subtit = ParagraphStyle("subtit", parent=styles["Normal"], fontSize=12,
                        textColor=GRIS, alignment=TA_CENTER, spaceAfter=30)

story = []


def p(txt):
    story.append(Paragraph(txt, body))


def seccion(txt):
    story.append(Paragraph(txt, h1))


def sub(txt):
    story.append(Paragraph(txt, h2))


def figura(nombre, pie, ancho=15):
    ruta = os.path.join(RESULTS, nombre)
    if not os.path.exists(ruta):
        story.append(Paragraph("[FALTA: " + nombre + "]", cap))
        return
    from reportlab.lib.utils import ImageReader
    iw, ih = ImageReader(ruta).getSize()
    w = ancho * cm
    h = w * ih / iw
    story.append(Image(ruta, width=w, height=h))
    story.append(Paragraph(pie, cap))


# ======================================================================
# ENCABEZADO
# ======================================================================
story.append(Spacer(1, 2 * cm))
story.append(Paragraph("Análisis de Big Data en salud", titulo))
story.append(Paragraph(
    "Relación entre salud periodontal y fuerza muscular con PySpark sobre "
    "datos NHANES y validación de escalabilidad mediante datos sintéticos",
    subtit))
story.append(Paragraph("Trabajo final de la Asignatura 3 - Entornos Big Data "
                       "para el análisis de datos", cap))
story.append(PageBreak())

# ======================================================================
# 1. OBJETIVOS
# ======================================================================
seccion("1. Objetivos del análisis")
p("El presente trabajo aborda un caso de estudio integral de Big Data en el "
  "ámbito de la salud a partir del conjunto de datos NHANES (National Health "
  "and Nutrition Examination Survey) de los Centros para el Control y "
  "Prevención de Enfermedades de Estados Unidos, ciclo 2013-2014. El objetivo "
  "científico es examinar la asociación entre el estado de salud bucodental y "
  "la fuerza muscular, un puente clínico legítimo entre la odontología y la "
  "fisioterapia que la literatura relaciona con la fragilidad y la sarcopenia.")
p("El trabajo persigue un doble propósito diferenciado. En primer lugar, un "
  "objetivo de inferencia clínica, que se resuelve exclusivamente sobre los "
  "datos reales y establece la relación entre las variables de estudio. En "
  "segundo lugar, un objetivo de ingeniería de datos, consistente en demostrar "
  "la escalabilidad de un entorno de procesamiento distribuido (Apache Spark) "
  "sobre volúmenes masivos de datos. Para este segundo objetivo se genera una "
  "réplica sintética del conjunto real a gran escala, evitando cualquier "
  "contaminación entre ambos propósitos.")
p("Se establece como regla metodológica fundamental que las conclusiones "
  "clínicas se obtienen únicamente de los datos reales, mientras que los datos "
  "sintéticos se emplean solo para las pruebas de rendimiento y escalabilidad. "
  "Esta separación evita la circularidad que supondría inferir hallazgos "
  "clínicos a partir de datos que reproducen, por construcción, las "
  "correlaciones del conjunto original.")

# ======================================================================
# 2. DATASET Y EXPLORACIÓN INICIAL
# ======================================================================
seccion("2. Dataset, adecuación y preprocesado")

sub("2.1 Descripción de la fuente")
p("NHANES combina, sobre los mismos participantes, una entrevista domiciliaria, "
  "un examen físico en unidades móviles y analíticas de laboratorio. El ciclo "
  "2013-2014 se seleccionó porque es uno de los dos únicos que midió la fuerza "
  "de prensión manual y, simultáneamente, incluye el examen periodontal de boca "
  "completa. Esta coincidencia permite relacionar ambos dominios en los mismos "
  "individuos. Se descargaron doce tablas en formato SAS transport (.XPT): "
  "demografía (DEMO), fuerza de prensión (MGX), examen periodontal (OHXPER), "
  "dentición (OHXDEN), medidas corporales (BMX), y las covariables tabaquismo "
  "(SMQ), actividad física (PAQ), diabetes (DIQ), alcohol (ALQ), composición "
  "corporal por DXA (DXX), salud oral autoinformada (OHQ) y vitamina D (VID).")

sub("2.2 Integración de las tablas")
p("Las doce tablas se unieron por la variable identificadora de participante "
  "(SEQN) mediante uniones de tipo left tomando la tabla demográfica como base. "
  "El resultado fue una tabla única de 10.175 registros y 1.056 columnas, sin "
  "duplicados de identificador. La elección de la unión left, frente a una unión "
  "interna, permitió conservar la trazabilidad completa de la muestra y "
  "controlar de forma explícita los criterios de exclusión en la fase posterior.")

sub("2.3 Exploración inicial y composición de la muestra")
p("La caracterización inicial de la muestra depurada (3.389 participantes) "
  "muestra un equilibrio por sexo (1.729 mujeres y 1.660 hombres) y una "
  "distribución de severidad periodontal coherente con la epidemiología "
  "poblacional: mayoría sin afectación o leve (2.373), un grupo moderado (844) "
  "y un grupo severo minoritario (172). La distribución por etnia refleja la "
  "composición representativa del muestreo NHANES.")
figura("fig20_composicion_muestra.png",
       "Figura 20. Composición de la muestra real por sexo, severidad "
       "periodontal y etnia.")

sub("2.4 Derivación de variables")
p("El examen periodontal no proporciona indicadores clínicos agregados, sino "
  "mediciones por diente y cara. A partir de 168 columnas de profundidad de "
  "sondaje y 168 de pérdida de inserción se derivaron dos indicadores medios "
  "por participante (ppd_medio y cal_medio), descartando los códigos centinela "
  "que representan sitios no medidos. De forma análoga, el recuento de dientes "
  "permanentes se derivó de las 32 columnas de estado dental. La severidad "
  "periodontal se clasificó a partir de la pérdida de inserción media en tres "
  "categorías, criterio que queda sujeto a validación clínica por el "
  "especialista.")

sub("2.5 Filtrado y trazabilidad de la muestra")
p("Sobre el conjunto integrado se aplicaron criterios de inclusión sucesivos, "
  "documentando la pérdida de registros en cada paso: partiendo de 10.175 "
  "participantes, la restricción a adultos de 30 o más años (población elegible "
  "para el examen periodontal) redujo la muestra a 4.813; la exigencia de "
  "disponer simultáneamente de fuerza de prensión y medición periodontal la "
  "situó en 3.389; y la depuración de rangos imposibles no eliminó registros "
  "adicionales, lo que confirma la integridad de las variables derivadas.")

sub("2.6 Calidad de datos: valores faltantes y atípicos")
p("El análisis de valores faltantes en el conjunto crudo mostró proporciones "
  "coherentes con el diseño de NHANES, en el que no todas las pruebas se "
  "realizan a todos los participantes: la fuerza de prensión presentaba un "
  "24,6 por ciento de ausencias, el índice de masa corporal un 11 por ciento y "
  "el indicador socioeconómico un 7,7 por ciento. El análisis de valores "
  "atípicos mediante el rango intercuartílico identificó observaciones extremas "
  "en la pérdida de inserción (7 por ciento), el recuento dental (8,4 por "
  "ciento) y el índice de masa corporal (3,7 por ciento). Se adoptó la decisión "
  "de conservar estos valores, dado que corresponden a casos clínicamente "
  "plausibles (periodontitis severa, pérdida dental avanzada, obesidad) y no a "
  "errores de medida. Su eliminación habría introducido un sesgo al excluir "
  "precisamente los casos patológicos de mayor interés para el estudio. El "
  "tratamiento definitivo de estas observaciones y de los valores faltantes "
  "residuales queda sujeto a validación clínica.")

# ======================================================================
# 3. PROCESAMIENTO Y RESULTADOS SOBRE DATOS REALES
# ======================================================================
seccion("3. Procesamiento y resultados sobre datos reales")
p("Todos los resultados de esta sección se obtuvieron sobre los 3.389 "
  "participantes reales, y constituyen las conclusiones clínicas válidas del "
  "trabajo.")

sub("3.1 Relación entre estado periodontal y fuerza")
p("La correlación cruda entre la pérdida de inserción media y la fuerza de "
  "prensión resultó prácticamente nula (r = 0,02). Sin embargo, esta ausencia "
  "aparente de relación se explica por el efecto dominante de los factores de "
  "confusión. Un modelo de regresión lineal que ajusta la fuerza por severidad "
  "periodontal, edad, sexo e índice de masa corporal alcanzó un coeficiente de "
  "determinación de 0,655, revelando que la fuerza está gobernada por el sexo "
  "(33 kg menos en mujeres) y la edad (0,5 kg menos por año). Tras controlar "
  "estos factores, el grupo sin afectación o leve presentó una fuerza "
  "significativamente mayor (más de 3 kg, p menor que 0,001) que el grupo "
  "moderado, aunque sin un gradiente dosis-respuesta limpio hacia el grupo "
  "severo, limitado por su reducido tamaño.")
figura("fig1_fuerza_periodontitis.png",
       "Figura 1. Fuerza de prensión media por severidad periodontal (datos reales).")
figura("fig2_cal_fuerza.png",
       "Figura 2. Dispersión entre pérdida de inserción media y fuerza de prensión.")

sub("3.2 Distribuciones y factores dominantes")
p("El análisis exploratorio confirma la estructura de los datos. La fuerza de "
  "prensión presenta una distribución condicionada fuertemente por el sexo, "
  "mientras que las variables periodontales muestran la asimetría a la derecha "
  "típica de estos indicadores. La contraposición entre la escasa correlación "
  "de la fuerza con el estado periodontal y su correlación negativa con la edad "
  "ilustra la necesidad del ajuste por factores de confusión.")
figura("fig3_histogramas.png",
       "Figura 3. Distribución de las variables numéricas.")
figura("fig4_fuerza_sexo.png",
       "Figura 4. Fuerza de prensión por sexo.")
figura("fig5_fuerza_periodontitis.png",
       "Figura 5. Distribución de la fuerza por severidad periodontal.")
figura("fig6_fuerza_edad.png",
       "Figura 6. Fuerza de prensión frente a edad, por sexo.")
figura("fig7_correlaciones.png",
       "Figura 7. Matriz de correlaciones entre variables numéricas.")

sub("3.3 Estado periodontal por sexo")
p("La severidad periodontal mostró una asociación marcada con el sexo, con una "
  "prevalencia sensiblemente mayor de afectación moderada y severa en hombres. "
  "La prueba de chi-cuadrado confirmó que esta diferencia es estadísticamente "
  "significativa (p menor que 0,001). Este hallazgo refuerza la condición del "
  "sexo como factor de confusión que afecta simultáneamente a ambas variables "
  "del estudio.")
figura("fig8_perio_sexo.png",
       "Figura 8. Distribución de severidad periodontal por sexo.")

sub("3.4 Dentición funcional y vía nutricional")
p("El número de dientes funcionales mostró una asociación con la fuerza más "
  "robusta que la propia severidad periodontal. Tras el ajuste por edad, sexo e "
  "índice de masa corporal, cada diente adicional se asoció a un incremento "
  "significativo de la fuerza (p = 0,002), un resultado compatible con una vía "
  "nutricional y masticatoria por la cual la pérdida dental afectaría al estado "
  "muscular.")
figura("fig9_dientes_fuerza.png",
       "Figura 9. Fuerza de prensión según dentición funcional.")

sub("3.5 Fuerza baja como desenlace clínico")
p("Al operacionalizar la fuerza baja como el quintil inferior dentro de cada "
  "sexo, se observó una mayor prevalencia de fuerza baja en los grupos de mayor "
  "severidad periodontal, un patrón más visible que en el análisis continuo.")
figura("fig10_sarcopenia.png",
       "Figura 10. Prevalencia de fuerza baja por severidad periodontal.")

sub("3.6 Estratificación por edad y determinantes sociales")
p("Los análisis complementarios de estratificación por grupos de edad y de "
  "gradiente socioeconómico aportan profundidad a la caracterización. El "
  "indicador de renta permite explorar la dimensión de equidad, mientras que el "
  "tabaquismo, confusor clásico de la enfermedad periodontal, enriquece el "
  "marco de covariables.")
figura("fig11_estratificado_edad.png",
       "Figura 11. Análisis estratificado por grupos de edad.")
figura("fig12_equidad.png",
       "Figura 12. Desigualdad socioeconómica en salud dental y muscular.")
figura("fig13_tabaco.png",
       "Figura 13. Tabaquismo, periodontitis y fuerza baja.")

# ======================================================================
# 4. GENERACIÓN SINTÉTICA Y ESCALABILIDAD
# ======================================================================
seccion("4. Generación sintética, prestaciones y escalabilidad")

sub("4.1 Estrategia de generación sintética")
p("Para las pruebas de escalabilidad se generó una réplica sintética del "
  "conjunto real a gran escala. Se descartó el uso de bibliotecas especializadas "
  "de síntesis (SDV/CTGAN) por dos motivos: su dependencia de componentes "
  "pesados incompatibles con las restricciones de disco de la máquina virtual, y "
  "el hecho de que su capacidad para modelar relaciones no lineales resultaba "
  "innecesaria para el propósito de estrés del sistema. En su lugar se empleó un "
  "método de remuestreo con reposición (bootstrap) con adición de ruido "
  "gaussiano, coherente con la metodología de generación desde la terminal "
  "empleada en el módulo. Este enfoque presenta la ventaja de conservar de forma "
  "natural tanto las distribuciónes marginales como las correlaciones entre "
  "variables, dado que cada registro sintético se origina en un individuo real "
  "completo.")
p("La réplica se restringió a nueve variables (los dos ejes del estudio y las "
  "covariables principales). Se excluyeron las variables de diseño muestral, "
  "carentes de sentido en datos sintéticos, y las covariables secundarias, cuya "
  "inclusión habría complicado la generación sin aportar al objetivo de "
  "escalabilidad. La reproducibilidad se garantizó mediante una semilla fija.")

sub("4.2 El límite de memoria como hallazgo")
p("El primer intento de generar 50 millones de registros en una sola operación "
  "resultó en la terminación del proceso por agotamiento de la memoria RAM de la "
  "máquina virtual. Este comportamiento, lejos de constituir un fallo, ilustra "
  "empíricamente la limitación central que motiva el Big Data: cuando el volumen "
  "de datos supera la memoria de una única máquina, el procesamiento debe "
  "realizarse por lotes o de forma distribuida. La generación se resolvió "
  "mediante un esquema por lotes de cinco millones de registros, manteniendo el "
  "consumo de memoria acotado.")

sub("4.3 Formato de almacenamiento: CSV frente a Parquet")
p("La comparación entre formatos arrojó una diferencia sustancial. El conjunto "
  "de 50 millones de registros ocupó 8,6 GB en formato CSV frente a 2,4 GB en "
  "formato Parquet, y su escritura pasó de 239 a 31 segundos. Esta mejora se "
  "explica por el almacenamiento columnar comprimido de Parquet, que además "
  "constituye el formato nativo de lectura particionada de Spark. La adopción de "
  "Parquet resolvió la restricción de disco y optimizó la fase de procesamiento.")

sub("4.4 Escalabilidad del procesamiento en Spark")
p("El procesamiento se ejecutó en Apache Spark en modo local sobre la máquina "
  "virtual. Como demostración de la necesidad del entorno distribuido, la "
  "lectura de los 50 millones de registros con la biblioteca pandas resultó "
  "imposible por agotamiento de memoria, mientras que Spark los contó y "
  "agregó sin dificultad al procesarlos de forma particionada. La medición a escalas "
  "crecientes mostró que la operación de recuento se mantiene casi constante "
  "gracias a la optimización sobre metadatos de Parquet y a la evaluación "
  "perezosa, mientras que la agregación escala de forma sublineal con el "
  "volumen, comportamiento característico de un motor que aprovecha el "
  "paralelismo.")
figura("fig14_escalabilidad_spark.png",
       "Figura 14. Escalabilidad del procesamiento en Spark a distintas escalas.")

sub("4.5 Validación de fidelidad a escala")
p("Se replicaron en Spark, sobre los 50 millones de registros sintéticos, los "
  "análisis agregados realizados sobre el conjunto real, con el objetivo de "
  "validar la fidelidad de la réplica. Se seleccionaron para replicar únicamente "
  "los análisis que conservan sentido a gran escala, es decir, las agregaciones "
  "(correlaciones, medias y proporciones por grupo). Se excluyeron, de forma "
  "justificada, los diagramas de dispersión (ilegibles e inviables con 50 "
  "millones de puntos), los histogramas (de forma idéntica por construcción), el "
  "modelo de regresión (que requeriría la biblioteca MLlib) y los análisis de "
  "equidad, tabaquismo y estratificación por edad, cuyas variables no forman "
  "parte del subconjunto sintético.")
p("Los resultados confirmaron una fidelidad prácticamente exacta. Las "
  "correlaciones (cal-fuerza 0,017, dientes-fuerza 0,168, edad-fuerza -0,332), "
  "las medias de fuerza por grupo periodontal y por sexo, y las proporciones de "
  "severidad periodontal por sexo reprodujeron los valores del conjunto real "
  "hasta la segunda cifra decimal. Debe subrayarse que esta coincidencia "
  "constituye el éxito de la validación de fidelidad, y no una confirmación "
  "clínica independiente, dado que el sintético reproduce por construcción la "
  "estructura del conjunto real.")
figura("fig15_spark_periodontitis.png",
       "Figura 15. Fuerza por severidad periodontal (sintético 50M, Spark).")
figura("fig16_spark_sexo.png",
       "Figura 16. Fuerza por sexo (sintético 50M, Spark).")
figura("fig17_spark_dientes.png",
       "Figura 17. Fuerza según dentición (sintético 50M, Spark).")
figura("fig18_spark_sarcopenia.png",
       "Figura 18. Fuerza baja por periodontitis (sintético 50M, Spark).")
figura("fig19_spark_perio_sexo.png",
       "Figura 19. Periodontitis por sexo (sintético 50M, Spark).")
figura("fig21_spark_composicion.png",
       "Figura 21. Composición de la muestra (sintético 50M, Spark).")

# ======================================================================
# 5. CONCLUSIONES
# ======================================================================
seccion("5. Conclusiones del trabajo")
p("Desde la perspectiva clínica, el trabajo establece que la relación entre "
  "salud bucodental y fuerza muscular es débil y se encuentra dominada por "
  "factores de confusión, en especial el sexo y la edad. Tras el ajuste, emergen "
  "asociaciones significativas pero de magnitud modesta, siendo el número de "
  "dientes funcionales un predictor más robusto que la severidad periodontal. "
  "Estos hallazgos son coherentes con la literatura sobre salud oral y "
  "fragilidad, y reproducen el sentido de estudios previos sobre el mismo ciclo "
  "de NHANES.")
p("Desde la perspectiva de la ingeniería de datos, el trabajo demuestra de forma "
  "empírica las ventajas del procesamiento distribuido. La imposibilidad de "
  "pandas para manejar 50 millones de registros frente a la solvencia de Spark, "
  "la necesidad del procesamiento por lotes ante el límite de memoria, y la "
  "superioridad del formato columnar Parquet constituyen ilustraciones directas "
  "de los conceptos del módulo.")
p("Como ventaja de la metodología adoptada destaca la separación estricta entre "
  "inferencia (sobre datos reales) y escalabilidad (sobre datos sintéticos), que "
  "preserva la validez de las conclusiones clínicas. Como limitación principal, "
  "el conjunto real es transversal y de tamaño modesto, lo que impide "
  "establecer causalidad; y el entorno Spark en modo local sobre una única "
  "máquina demuestra el comportamiento de escalabilidad, pero no el rendimiento "
  "de un clúster distribuido real.")

seccion("6. Conclusiones generales del módulo")
p("El módulo ha permitido experimentar de forma práctica el ciclo completo del "
  "Big Data en salud: desde la ingesta y depuración de datos heterogéneos, "
  "pasando por el procesamiento con herramientas del ecosistema Hadoop y Spark, "
  "hasta el análisis de prestaciones y escalabilidad. La principal enseñanza "
  "reside en comprender, con evidencia obtenida en la propia infraestructura, "
  "por qué las herramientas tradicionales resultan insuficientes ante volúmenes "
  "masivos y cómo los entornos distribuidos resuelven esa limitación. Como "
  "aspecto de mejora para futuras ediciones, sería valioso disponer de acceso a "
  "un clúster multinodo real, que permitiría contrastar la escalabilidad "
  "horizontal frente al paralelismo local aquí demostrado.")

# ======================================================================
# ANEXO: SCRIPTS
# ======================================================================
story.append(PageBreak())
seccion("Anexo. Código desarrollado")
p("Se incluye a continuación el código fuente de los scripts del pipeline, en "
  "el orden lógico de ejecución. El proyecto completo, junto con la "
  "documentación de replicación, se encuentra versionado para su reproducción.")

for script in SCRIPTS_ANEXO:
    ruta = os.path.join(ROOT, script)
    if not os.path.exists(ruta):
        continue
    sub(script)
    with open(ruta, "r") as fh:
        contenido = fh.read()
    # Trocea en bloques para evitar desbordar la página
    lineas = contenido.splitlines()
    bloque = []
    for ln in lineas:
        bloque.append(ln[:110])  # recorta líneas muy largas
        if len(bloque) >= 45:
            story.append(Preformatted("\n".join(bloque), code))
            bloque = []
    if bloque:
        story.append(Preformatted("\n".join(bloque), code))

# ======================================================================
# GENERAR PDF
# ======================================================================
doc = SimpleDocTemplate(SALIDA, pagesize=A4,
                        leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=2 * cm, bottomMargin=2 * cm)
doc.build(story)
print("Informe generado:", SALIDA)
