# SaludVital - Business Intelligence Project

## Overview
SaludVital is a Business Intelligence (BI) solution designed for a private ambulatory medical center in the Biobío Region. The project implements a complete BI lifecycle, from data extraction and transformation (ETL) to dimensional modeling and interactive dashboards.

## Team
- **Integrantes:** Lukas Garrido, Octavio Valencia
- **Grupo:** 07
- **Profesor:** Alexandra Matus

## Tech Stack
- **Dashboarding & ETL:** Power BI (Power Query / M, DAX)
- **Validation & Analysis:** Python (Pandas, Matplotlib) in Jupyter Notebooks.
- **Application:** Streamlit (Python) for potential web deployment.
- **Version Control:** Git.

## Project Structure
- `app/`: Streamlit application source code.
- `assets/`: Project assets (logos and generated figures).
  - `img/`: Contains figures (`fig01` to `fig17`) generated during analysis.
- `data/`: Data storage (models, control files).
- `docs/`: Documentation (User guide, Final report).
- `notebooks/`: Jupyter notebooks for data validation and exploratory analysis.
- `scripts/`: Python scripts for dimensional modeling.
- `theme/`: Theme configurations (JSON).

## Data Sources
1. `SaludVital_BaseDatos.xlsx`: Original database (7 sheets).
2. `SaludVital_DatosAdicionales_ETL.xlsx`: Additional data for ETL stress testing.

## Conventions & Rules
- **Image Paths:** Documentation images should refer to the `assets/` folder. For files in `docs/`, use relative paths `../assets/` or `../assets/img/`.
- **Validation:** All BI results must be validated against the Jupyter notebook `notebooks/analisis_saludvital.ipynb`.
- **Privacy:** Patient names and sensitive data are excluded from the dimensional model; only IDs and non-identifying attributes (Age, Communa, etc.) are used.

## Ongoing Tasks
- [x] Fix broken image paths in `docs/Informe_SaludVital.md`.
- [ ] Ensure consistent referencing of assets across all documentation.
