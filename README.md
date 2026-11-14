# SaludVital BI

Proyecto de **Inteligencia de Negocio**: solución de BI (ETL + modelo dimensional + dashboard) para analizar las atenciones médicas de SaludVital, centro médico ambulatorio privado de la Región del Biobío.

## Contexto

SaludVital lleva 8 años operando, tiene 10 especialidades, más de 20 profesionales y ~2.000 consultas mensuales. Sus sistemas no permiten análisis multidimensional, lo que genera:

- Información dispersa en distintas fuentes
- Pacientes duplicados y especialidades con nombres inconsistentes
- Reservas que no terminan en atención (Atendida, Cancelada, No asistió, Pendiente)
- Reportes mensuales manuales y sin visión consolidada del desempeño

## Objetivo

Diseñar e implementar una solución de BI que permita analizar demanda, atención, desempeño médico, pacientes e ingresos para apoyar la toma de decisiones de la dirección.

## Estructura del repositorio

```text
SaludVital/
├── .venv/                      # Entorno virtual de Python
├── data/                       # Datos de origen y modelo dimensional generado
│   ├── modelo/                 # Esquema en estrella (CSV y control)
│   │   ├── DimFecha.csv
│   │   ├── DimMedico.csv
│   │   ├── DimPaciente.csv
│   │   ├── DimPrestacion.csv
│   │   ├── HechoReservas.csv
│   │   ├── HechoDetalle.csv
│   │   ├── SaludVital_ModeloDimensional.xlsx
│   │   └── control/            # Bitácoras de calidad y rechazos
│   ├── SaludVital_BaseDatos.xlsx
│   └── SaludVital_DatosAdicionales.xlsx
├── docs/                       # Documentación técnica y funcional
│   ├── documentacion_etl.md    # Especificación ETL y reglas de negocio
│   ├── guia_usuario.md         # Guía de uso y funcionamiento del repo
│   ├── Instrucciones.pdf       # Pauta original del proyecto
│   └── Proyecto_SaludVital_Analisis.md # Análisis analítico y estratégico
├── notebooks/                  # Análisis exploratorio interactivo
│   └── analisis_saludvital.ipynb # Notebook Jupyter para análisis y respuestas a preguntas de negocio
├── reports/                    # Visualización Power BI
│   └── SaludVital.pbix         # Dashboard de BI (Modelo dimensional + DAX)
├── scripts/                    # Scripts de procesamiento
│   └── modelo_dimensional.py   # Script ETL en Python (Pandas)
├── theme/                      # Recursos visuales
│   └── SaludVital.json         # Tema de diseño corporativo para Power BI
├── .gitignore                  # Archivos ignorados (CSV, XLSX, checkpoints y entornos)
├── README.md                   # Resumen ejecutivo del proyecto
└── requirements.txt            # Dependencias de Python
```

---

## Stack

Python (Pandas) + Jupyter Notebooks · Power BI + DAX (reporte) + Excel (fuente)

## Documentación y Guía de Uso

- **[Guía de Usuario (`docs/guia_usuario.md`)](docs/guia_usuario.md)**: Instrucciones detalladas de configuración, ejecución del pipeline ETL, uso del notebook y estructura.
- **Documentación ETL y de Negocio (`docs/documentacion_etl.md`)**: Reglas de negocio, mapeos, especificación ETL y 24 preguntas analíticas.
