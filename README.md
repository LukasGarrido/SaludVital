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

## Modelo dimensional

Constelación de hechos con dimensiones conformadas:

| Tabla | Grano |
|---|---|
| `FACT_RESERVAS` | Una fila por reserva |
| `FACT_PRESTACIONES` | Una fila por prestación realizada (solo reservas "Atendida") |

**Dimensiones:** `DIM_PACIENTE`, `DIM_MEDICO`, `DIM_ESPECIALIDAD`, `DIM_PRESTACION`, `DIM_ESTADO_RESERVA`, `DIM_TIEMPO`.

## KPIs principales

Total de reservas · Atenciones realizadas · Tasa de atención · Tasa de inasistencia · Tasa de cancelación · Ingresos · Ingreso promedio por atención · Utilización de horas.

## Calidad de datos (hallazgos clave)

Fuente: `SaludVital_BaseDatos.xlsx` (7 tablas).

- `03_ESPECIALIDADES` está corrupta (copia de `02_MEDICOS`): la dimensión de especialidad se reconstruye desde `04_PRESTACIONES` (RN01).
- `01_PACIENTES`: columna vacía y 3 registros incompletos (P031–P033), que se excluyen o ponen en cuarentena.
- Tablas transaccionales limpias y con integridad referencial correcta.
- Se mantienen reglas preventivas de normalización y deduplicación de pacientes y especialidades (RN02, RN03).

## Stack

Python (ETL) · Excel (fuente) · Power BI + DAX (reporte)

## Documentación

El análisis completo está en [`Proyecto_SaludVital_Analisis.md`](./Proyecto_SaludVital_Analisis.md): análisis del negocio, reglas de negocio, requerimientos BI (24 preguntas), perfilamiento de datos, modelo dimensional y medidas.


## Estructura del repositorio

```
SaludVital/
├── .obsidian
├── README.md
├── .gitignore
├── data/
│   ├── SaludVital_BaseDatos.xlsx
│   ├── SaludVital_DatosAdicionales.xlsx
├── docs/
│   ├── documentacion_etl.md
│   └── instruciones.pdf
│   └── Proyecto_SaludVital_Analisis.md
├── reports/
    └── Salud_Vital.pbix

```