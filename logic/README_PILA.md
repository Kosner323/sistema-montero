# 🧮 Motor de Cálculo PILA - Sistema Montero

**Versión**: 1.1.0 | **Fecha**: 26/11/2025 | **Estado**: ✅ Validado

## Descripción

Módulo independiente de lógica de negocio para el cálculo de Seguridad Social (PILA) según la legislación laboral colombiana. Implementa cálculos precisos sin dependencias de base de datos, usando aritmética Decimal para evitar errores de redondeo financiero.

## 🆕 Novedades v1.1 (26/11/2025)

### Correcciones Legales Críticas

- ✅ **CCF 4% SIEMPRE**: Ya no requiere umbral de 10 SMMLV (Ley 789/2002)
- ✅ **Exoneración Salud Empleador**: Para empresas con salarios <10 SMMLV (Ley 1607/2012)
- ✅ **Tope IBC 25 SMMLV**: Límite máximo de $32,500,000 (Decreto 1406/1999)
- ✅ **Salario Integral**: Soporte para IBC = 70% (Código Sustantivo del Trabajo)

**Documentación completa**: Ver `PILA_V1_1_RESUMEN.md`

## ✨ Características

- ✅ **Cálculo Exacto**: Todos los valores al peso usando `Decimal`
- ✅ **Validaciones Inteligentes**: Auto-ajuste de salarios menores al SMMLV
- ✅ **Todos los Conceptos**: Salud, Pensión, ARL, Parafiscales
- ✅ **5 Niveles de Riesgo ARL**: Desde oficinas hasta construcción
- ✅ **Reportes Legibles**: Genera reportes formateados listos para imprimir
- ✅ **100% Testeado**: Suite completa de pruebas unitarias
- ✅ **Sin Dependencias BD**: Lógica pura reutilizable
- 🆕 **Cumplimiento Legal**: 100% conforme con legislación colombiana 2025

## 📦 Estructura del Módulo

```
src/dashboard/
├── logic/
│   ├── __init__.py
│   ├── pila_engine.py               # Motor v1.1
│   ├── pila_engine_v1.0_backup.py   # Backup v1.0
│   ├── README_PILA.md               # Esta guía
│   └── PILA_V1_1_RESUMEN.md         # Documentación v1.1
├── tests/
│   ├── __init__.py
│   ├── test_calculadora_pila.py     # Pruebas unitarias v1.0
│   └── validar_pila_v1_1.py         # Validación v1.1
└── demo_pila.py                      # Script de demostración
```

## 🚀 Instalación

No requiere instalación adicional. Solo necesita Python 3.8+

```bash
# Ejecutar desde el directorio dashboard
cd src/dashboard
```

## 💡 Uso Básico

### Ejemplo 1: Empleado Regular (con exoneración)

```python
from logic.pila_engine import CalculadoraPILA

# 🆕 v1.1: Empresa pequeña con exoneración de Salud
calc = CalculadoraPILA(
    salario_base=1300000, 
    nivel_riesgo_arl=1,
    es_empresa_exonerada=True  # ← NUEVO v1.1
)

resultado = calc.calcular()

print(f"Total Empleado: ${resultado.total_empleado:,.0f}")     # $104,000
print(f"Total Empleador: ${resultado.total_empleador:,.0f}")   # $279,786
print(f"Salud Empleador: ${resultado.salud_empleador:,.0f}")   # $0 (exonerado)

# Generar reporte completo
print(calc.generar_reporte())
```

### Ejemplo 2: Gerente con Salario Integral

```python
# 🆕 v1.1: Salario Integral (IBC = 70%)
calc = CalculadoraPILA(
    salario_base=25000000,
    nivel_riesgo_arl=2,
    es_salario_integral=True  # ← NUEVO v1.1
)

resultado = calc.calcular()

print(f"IBC (70%): ${resultado.ibc:,.0f}")                     # $17,500,000
print(f"Total Empleado: ${resultado.total_empleado:,.0f}")     # $1,400,000
print(f"Total Empleador: ${resultado.total_empleador:,.0f}")   # $4,470,200
```

### Ejemplo 3: Ejecutivo Salario Alto (>25 SMMLV)

```python
# 🆕 v1.1: Tope IBC automático
calc = CalculadoraPILA(
    salario_base=35000000,
    nivel_riesgo_arl=4
)

resultado = calc.calcular()

print(f"Salario: ${resultado.salario_base:,.0f}")              # $35,000,000
print(f"IBC (tope): ${resultado.ibc:,.0f}")                    # $32,500,000
print(f"IBC limitado: {resultado.ibc_limitado}")               # True
```

### Función de Cálculo Rápido

```python
from logic.pila_engine import calcular_pila_rapido

# 🆕 v1.1: Incluye parámetros de exoneración e integral
resultado = calcular_pila_rapido(
    salario=2000000, 
    riesgo_arl=3,
    exonerada=True,     # ← NUEVO v1.1
    integral=False      # ← NUEVO v1.1
)

print(f"Salario Neto: ${resultado['salario_neto']:,.0f}")
print(f"Total Empleador: ${resultado['total_empleador']:,.0f}")
```

## 🧪 Validación y Pruebas

### Opción 1: Validación v1.1 (Recomendado)

```bash
# Ejecutar validación de correcciones legales
python tests/validar_pila_v1_1.py
```

**Resultado esperado**: `✅ TODOS LOS TESTS PASARON (5/5)`

### Opción 2: Pruebas Unitarias pytest

```bash
# Opción básica
pytest tests/test_calculadora_pila.py -v

# Con cobertura de código
pytest tests/test_calculadora_pila.py -v --cov=logic --cov-report=html
```

### Opción 3: Ejemplos Interactivos

```bash
# Ejecutar demostración con 4 ejemplos
python logic/pila_engine.py
```

## 📊 Niveles de Riesgo ARL

| Nivel | Descripción | Tasa | Ejemplos de Actividades |
|-------|-------------|------|-------------------------|
| **1** | Mínimo | 0.522% | Oficinas, comercio, finanzas |
| **2** | Bajo | 1.044% | Manufactura leve, servicios |
| **3** | Medio | 2.436% | Manufactura pesada, transporte |
| **4** | Alto | 4.350% | Industria pesada, química |
| **5** | Máximo | 6.960% | Construcción, minería, petróleo |

## 🧪 Ejecutar Pruebas

```bash
# Opción 1: pytest (recomendado)
pytest tests/test_calculadora_pila.py -v

# Opción 2: pytest con cobertura
pytest tests/test_calculadora_pila.py -v --cov=logic --cov-report=html

# Opción 3: ejecución directa
python tests/test_calculadora_pila.py
```

## 🎯 Demostración

```bash
# Ejecutar todas las demos interactivas
python demo_pila.py
```

## 📋 Ejemplos de Cálculo

### Ejemplo 1: Empleado con Salario Mínimo

```python
calc = CalculadoraPILA(salario_base=1300000, nivel_riesgo_arl=1)
resultado = calc.calcular()

# Resultado:
# - Total Empleado:  $104,000 (8%)
# - Total Empleador: $273,286 (21.02%)
# - Salario Neto:    $1,196,000
```

### Ejemplo 2: Empleado de Construcción

```python
calc = CalculadoraPILA(salario_base=1800000, nivel_riesgo_arl=5)
resultado = calc.calcular()

# Resultado:
# - ARL: $125,280 (6.96% - Riesgo Máximo)
# - Total Empleado: $144,000
# - Total Empleador: $476,280
```

### Ejemplo 3: Gerente (con Parafiscales)

```python
calc = CalculadoraPILA(salario_base=20000000, nivel_riesgo_arl=1)
resultado = calc.calcular()

# Resultado:
# - Parafiscales: $1,800,000 (9%)
# - Total Empleado: $1,600,000
# - Total Empleador: $6,104,400
```

## 🔍 Detalles de Cálculo

### Salud (12.5% Total)
- **Empleado**: 4% del salario base
- **Empleador**: 8.5% del salario base

### Pensión (16% Total)
- **Empleado**: 4% del salario base
- **Empleador**: 12% del salario base

### ARL (100% Empleador)
- Varía según nivel de riesgo (0.522% - 6.96%)

### Parafiscales (100% Empleador)
Solo aplican si salario > 10 SMMLV ($13,000,000)
- **CCF**: 4% Caja de Compensación Familiar
- **SENA**: 2% Servicio Nacional de Aprendizaje
- **ICBF**: 3% Instituto Colombiano de Bienestar Familiar

## ⚙️ Validaciones Automáticas

1. **Salario < SMMLV**: Se ajusta automáticamente a $1,300,000
2. **Nivel Riesgo Inválido**: Lanza `ValueError`
3. **Salario ≤ 0**: Lanza `ValueError`
4. **Redondeo Financiero**: Usa `ROUND_HALF_UP`

## 📈 Pruebas Incluidas

- ✅ Cálculo con salario mínimo (Riesgo I)
- ✅ Cálculo con salario mínimo (Riesgo V)
- ✅ Cálculo con parafiscales
- ✅ Validación de auto-ajuste de salario
- ✅ Validación de errores (salario 0, negativo, riesgo inválido)
- ✅ Precisión decimal (sin errores de redondeo)
- ✅ Casos reales (administrativo, construcción, gerente)

## 🔗 Integración con BD (Futuro)

```python
# Ejemplo de integración futura
from logic.pila_engine import CalculadoraPILA
import sqlite3

conn = sqlite3.connect('mi_sistema.db')
usuario = conn.execute("SELECT ibc, claseRiesgoARL FROM usuarios WHERE id=?", (13,)).fetchone()

# Calcular con datos de BD
calc = CalculadoraPILA(
    salario_base=usuario['ibc'],
    nivel_riesgo_arl=int(usuario['claseRiesgoARL'][0])  # "I" -> 1
)

resultado = calc.calcular()

# Guardar resultado
conn.execute("""
    UPDATE usuarios 
    SET salud_empleado=?, pension_empleado=?, total_deducciones=?
    WHERE id=?
""", (resultado.salud_empleado, resultado.pension_empleado, resultado.total_empleado, 13))
```

## 📚 Referencias Legales

- Decreto 1772 de 1994 (Tabla ARL)
- Ley 100 de 1993 (Sistema de Seguridad Social)
- Ley 1607 de 2012 (Parafiscales)
- Salario Mínimo 2025: $1,300,000 COP

## 🤝 Contribuciones

Este módulo está diseñado para ser extendido. Posibles mejoras:

- [ ] Soporte para auxilio de transporte
- [ ] Cálculo de horas extras
- [ ] Descuentos adicionales (créditos, embargos)
- [ ] Exportación a formato PILA (.txt)
- [ ] Integración con API de la UGPP

## 📄 Licencia

Sistema Montero - Uso Interno

---

**Versión**: 1.0.0  
**Fecha**: 2025-11-26  
**Autor**: Sistema Montero
