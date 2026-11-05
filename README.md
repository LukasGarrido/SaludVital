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

```
SaludVital/
├── .obsidian
├── README.md
├── .gitignore
├── data/
│   ├── Catalogo_Reglas_SaludVital_v1.0_2026-11-04.xlsx
│   ├── Inventario_SaludVital_v1.0_2026-11-04.xlsx
│   ├── SaludVital_BaseDatos.xlsx
│   ├── SaludVital_DatosAdicionales.xlsx
├── docs/
│   ├── documentacion_etl.md
│   └── instruciones.pdf
│   └── Proyecto_SaludVital_Analisis.md
├── reports/
    └── SaludVital.pbix
```
---

## Stack

Excel (fuente) · Power BI + DAX (reporte) + Obsidian (Documentacion)

## Documentación

El análisis completo está en [`Docs`](docs/): análisis del negocio, reglas de negocio, requerimientos BI (24 preguntas), perfilamiento de datos, modelo dimensional y medidas.
