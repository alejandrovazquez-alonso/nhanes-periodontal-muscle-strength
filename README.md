# Periodontal Health and Muscle Strength — Big Data Pipeline (NHANES)

Big Data pipeline (Apache Spark) analyzing the association between periodontal health and
grip strength using real NHANES 2013-2014 data, with a separate scalability validation on
synthetic data up to 50 million records.

**Authors:** Alejandro Vázquez Alonso and Daniel Vidal Silván (dentist)
**Context:** Master's in AI and Big Data in Health, Universitat Autònoma de Barcelona (UAB) —
Module 3, "Entornos Big Data para el análisis de datos" — Trabajo Final de Asignatura, graded 9.8/10
**Infrastructure:** OpenNebula virtual machines (Debian 12, BigTop 2.0), Apache Spark local mode

## Project origin

This was a two-person assignment. The methodological design — the strict separation between
real-data clinical inference and synthetic-data scalability testing — was a joint decision;
implementation was distributed across both members' VMs. This repository contains the full
pipeline as submitted, reproducible end to end from the public data source.

## Objective

Two distinct, deliberately separated goals:

1. **Clinical inference** (real data only): test the association between periodontal disease
   severity and grip strength, a documented link between oral health and sarcopenia/frailty.
2. **Data engineering** (synthetic data only): demonstrate the scalability of a distributed
   processing pipeline (Apache Spark) against data volumes that exceed single-machine memory.

The two objectives never mix data: **clinical conclusions come exclusively from the 3,389 real
participants; synthetic data is used only for performance and scalability testing.** Inferring
clinical findings from synthetic data would be circular, since the synthetic data reproduces
the real data's correlations by construction.

## Data access

NHANES is a **public** dataset published by the CDC/NCHS — no credentialing or Data Use
Agreement required (unlike MIMIC-III in a related repository). Raw `.XPT` files are not
included in this repository (per assignment rules, which required either open data or its
source URL, not the raw binaries); see [`scripts/README_DATASET.md`](scripts/README_DATASET.md)
for the direct download URLs of all 12 tables and the full pipeline execution order.

## Dataset construction

- 12 NHANES tables (demographics, grip strength, periodontal exam, dentition, body measures,
  smoking, physical activity, diabetes, alcohol, DXA body composition, self-reported oral
  health, vitamin D) joined on participant ID (`SEQN`) via left joins, base table demographics
  → **10,175 participants × 1,056 columns**.
- Sequential inclusion filters, each documented: adults ≥30 (periodontal exam eligibility) →
  4,813; requiring both grip strength and periodontal measurement → **3,389 participants**
  (final analysis sample); implausible-range cleaning removed no further records, confirming
  derived-variable integrity.
- Periodontal indicators (`ppd_medio`, `cal_medio`) derived by averaging 168 probing-depth and
  168 attachment-loss columns per participant (per-tooth, per-surface measurements), excluding
  sentinel codes for unmeasured sites. Severity thresholds were grounded in scientific
  evidence and official clinical guidelines, and validated by co-author Daniel Vidal Silván
  (dentist).

## Key clinical findings (real data, n=3,389)

📊 **[See the full EDA & findings summary with figures →](docs/eda_summary.md)**

- Crude correlation between periodontal attachment loss and grip strength: **r = 0.02**
  (practically null).
- This near-null correlation is explained by strong confounding: a linear regression
  adjusting for periodontal severity, age, sex, and BMI reached **R² = 0.655**, revealing
  grip strength is governed primarily by sex (−33 kg in women) and age (−0.5 kg/year).
- After adjustment, the no/mild periodontal group showed significantly greater strength
  (>3 kg, p<0.001) than the moderate group, without a clean dose-response gradient into the
  severe group (limited by its small size).
- Functional tooth count was a more robust strength predictor than periodontal severity
  itself (p=0.002 per additional tooth after adjustment) — consistent with a
  nutritional/masticatory pathway linking tooth loss to muscle status.
- Socioeconomic and smoking gradients were also explored as complementary stratifications.

**Conclusion:** the periodontal-strength relationship is weak and dominated by confounders
(sex, age); after adjustment, associations are significant but modest, consistent with prior
literature on oral health and frailty using the same NHANES cycle.

## Data engineering results (synthetic data, up to 50M records)

- **Synthetic generation:** bootstrap resampling with Gaussian noise (not SDV/CTGAN — avoided
  due to heavy dependencies incompatible with VM disk constraints, and because modeling
  non-linear relationships was unnecessary for the stress-testing goal). Each synthetic record
  originates from a real individual, naturally preserving marginal distributions and
  correlations.
- **Memory limit as a finding, not a failure:** the first attempt to generate 50M records in a
  single operation was killed by the OS for RAM exhaustion — empirical illustration of exactly
  the limitation that motivates Big Data. Resolved via batched generation (5M records/batch).
- **Storage format:** 50M records occupied 8.6 GB as CSV vs. **2.4 GB as Parquet**; write time
  dropped from 239.5s to 31.2s — columnar compression and Spark's native partitioned reads.
- **Pandas vs. Spark:** reading 50M records with pandas was impossible (OS killed the process,
  RAM exhaustion, confirmed empirically). Spark counted and aggregated the same volume without
  difficulty via partitioned processing.
- **Scalability behavior:** read+count time stayed near-constant across scales (Parquet
  metadata optimization + lazy evaluation); aggregation scaled sub-linearly with volume,
  characteristic of a parallelism-exploiting engine.
- **Fidelity validation:** aggregated statistics computed in Spark on the 50M synthetic
  records (correlations, group means, proportions) reproduced the real-data values to the
  second decimal place — validating replica fidelity, **not** an independent clinical
  confirmation (the synthetic set reproduces the real structure by construction).

## Repository structure

```
nhanes-periodontal-muscle-strength/
├── scripts/
│   ├── README_DATASET.md        # data source URLs, download script, execution order
│   ├── config.py                 # shared config (paths, columns, seed)
│   ├── 02_merge.py               # joins the 12 NHANES tables by SEQN
│   ├── 02b_exploracion_inicial.py
│   ├── 02c_composicion_muestra.py
│   ├── 03_preprocesado.py        # derives core variables (ppd_medio, cal_medio, n_dientes)
│   ├── 03b_filtrado.py           # inclusion filters + periodontitis classification
│   ├── 03c_calidad_datos.py      # missing values and outlier analysis
│   ├── 04_analisis_real.py       # OLS model + Figures 1-2 (real data)
│   ├── 04b_visualizaciones.py    # Figures 3-7 (EDA, real data)
│   ├── 05_generar_sintetico.py   # batched synthetic data generation
│   ├── 06_spark_escalabilidad.py # Spark scalability benchmark (4 scales)
│   ├── 08a-08e_spark_*.py        # fidelity validation on 50M synthetic records (Spark)
│   └── generar_informe.py        # builds the final PDF report (ReportLab)
├── docs/
│   ├── eda_summary.md            # condensed EDA + key findings, with figures
│   └── figures/                  # key figures extracted from the original report
├── data/                          # not versioned — see Data access above
│   ├── raw/                       # place downloaded .XPT files here
│   ├── interim/                   # merged raw parquet (generated)
│   ├── processed/                 # cleaned/derived parquet (generated)
│   └── synthetic/                 # generated synthetic replicas (generated)
├── results/                       # generated figures (not versioned)
├── requirements.txt
└── README.md
```

## Requirements

```bash
pip install -r requirements.txt
```

Apache Spark (PySpark) is required for the `06_*` and `08*_spark_*` scripts. The Spark scripts
reference absolute paths from the original VM execution environment
(`file:///home/adminp/tfa-nhanes/data/synthetic/`) — adjust these to your local path before
running.

## Pipeline execution order

See [`scripts/README_DATASET.md`](scripts/README_DATASET.md) for the full order and a
description of each script's output.

## Limitations

- **Cross-sectional data.** The real sample (n=3,389) is a single cross-sectional cycle
  (NHANES 2013-2014); no causal claims can be made about periodontal disease causing reduced
  strength (or vice versa) — only association after adjustment for measured confounders.
- **Local Spark, not a real cluster.** All Spark processing ran in local mode on a single VM.
  This demonstrates the scalability *behavior* (batched processing, columnar storage,
  partitioned reads) but not the performance characteristics of a genuinely distributed
  multi-node cluster.
- **Synthetic data validates fidelity, not clinical findings.** The 50M-record synthetic
  replica reproducing real-data statistics to the second decimal confirms the generation
  method works — it is not independent evidence for the clinical association, since the
  synthetic data is derived from and reproduces the real data's structure by construction.

## Author's note on AI assistance

This project was developed with the assistance of generative AI (Claude, Anthropic) as general
support during preparation, per the Master's program's academic integrity policy. The authors
reviewed, validated, and assume full responsibility for the final content of the report,
presentation, and submitted code, regardless of the tools used during development.

## Related work

- [MIMIC-III AKI in-hospital mortality prediction](https://github.com/alejandrovazquez-alonso/mimic-aki-mortality-prediction)
- [BRFSS health risk clustering & classification](#) — link to be added

## License

Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0),
per the original assignment submission license.
