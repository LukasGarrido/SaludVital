# AGENT.md - SaludVital BI Project

Welcome to the **SaludVital** Business Intelligence and Analytics workspace. This document serves as the core reference guide for AI agents and developers working on this codebase.

## Project Overview
- **Name:** SaludVital (Centro Medico Ambulatorio Privado)
- **Location:** Region del Biobio, Chile (8 anos de operacion, ~2,000 consultas mensuales, 10 especialidades medicas, >20 profesionales).
- **Purpose:** Provide a multidimensional Business Intelligence (BI) solution (ETL pipeline + Star Schema dimensional model + interactive Streamlit dashboard + Power BI reports) to replace manual monthly reports and support strategic decision-making in demand, productivity, patient profiling, and financial valuation.

---

## Repository Architecture & Directory Structure
```text
SaludVital/
├── app/                        # Modular Streamlit application
│   ├── app.py                  # Main entrypoint, page routing, global filters, and UI layout
│   ├── data.py                 # Data preparation, Star Schema modeling, and 1:N/N:M merges
│   └── medidas.py              # Business metrics calculation, formatters (CLP, %, numbers), & acceptance tests
├── data/                       # Source data and generated dimensional model
│   ├── modelo/                 # Dimensional model CSVs (DimFecha, DimMedico, DimPaciente, DimPrestacion, HechoReservas, HechoDetalle)
│   │   └── control/            # Quality logs, rejection logs, merge audits, idempotency verification
│   ├── SaludVital_BaseDatos.xlsx        # Base period raw data (Jan 5 - Feb 3, 2026)
│   └── SaludVital_DatosAdicionales.xlsx # Additional period raw data (Feb 4 - Mar 31, 2026)
├── docs/                       # Technical & Functional Documentation
│   ├── documentacion_etl.md    # Complete ETL specifications & business rules catalog
│   ├── guia_usuario.md         # User guide and instructions
│   ├── informe/                # Formal project report (v2.0)
│   │   └── Informe_SaludVital.md # Comprehensive integral report with 17 figures & analysis
│   ├── Instrucciones.pdf       # Original project guidelines
│   └── Proyecto_SaludVital_Analisis.md # Analytical and business strategy document
├── notebooks/                  # Exploratory & validation notebooks
│   └── analisis_saludvital.ipynb # Jupyter notebook answering 24 business questions
├── reports/                    # Power BI visualization
│   └── SaludVital.pbix         # BI Dashboard (Star schema + DAX measures)
├── scripts/                    # ETL & processing scripts
│   └── modelo_dimensional.py   # Python Pandas ETL pipeline script
├── theme/                      # Corporate visual styling
│   └── SaludVital.json         # Power BI custom theme
├── app.py                      # Convenience entrypoint runner
├── README.md                   # Executive summary & setup instructions
└── requirements.txt            # Python dependencies
```

---

## Key Business Rules & ETL Logic
1. **Patient Deduplication (RN03):** Resolves duplicate patient records resulting from variations in casing, spacing, or abbreviations (e.g., "Juan Perez" vs "JUAN PEREZ").
2. **Inconsistent Specialties:** Standardizes specialty names across source files (e.g., "Traumatologia", "TRAUMATOLOGIA", "Trauma").
3. **Appointment Lifecycle & Status:** Every reservation starts as `Pendiente` and resolves to one of three final states:
   - `Atendida`: Patient attended; generates a medical consultation and performance/service details.
   - `No asistio`: Patient did not show up; results in wasted hours (`BloqueMinutos`).
   - `Cancelada`: Reservation cancelled; no consultation generated.
4. **Valued Income (Ingreso Valorizado):** Calculated as `Cantidad x ValorUnitario` from consultation service details (`HechoDetalle`). There are no direct payment gateway sources.

---

## Execution & Development Commands
- **Run Streamlit Dashboard:**
  ```bash
  streamlit run app/app.py
  ```
- **Run Python ETL Pipeline:**
  ```bash
  python scripts/modelo_dimensional.py
  ```

---

## Development Guidelines for Agents
- **Scope Restriction:** Maintain strict adherence to user prompts. Do not modify business logic unless explicitly requested.
- **Styling:** Streamlit UI styling enhancements should leverage modern CSS/HTML injection while preserving all session state variables (`st.session_state.filtro_fechas`, `st.session_state.filtro_comuna`, `st.session_state.filtro_sexo`) and core logic.
- **Validation:** Always verify application functionality and ensure tests (`ejecutar_pruebas_aceptacion`) pass successfully.
