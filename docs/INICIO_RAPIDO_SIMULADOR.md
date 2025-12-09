# ⚡ INICIO RÁPIDO - SIMULADOR PILA

## 🚀 EN 3 PASOS

### Paso 1: Iniciar Servidor
```powershell
cd "d:\Mi-App-React\src\dashboard"
python app.py
```

Espera ver:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

---

### Paso 2: Hacer Login
Abre en navegador:
```
http://localhost:5000/login
```

Ingresa credenciales de tu sistema.

---

### Paso 3: Acceder al Simulador
```
http://localhost:5000/api/cotizaciones/simulador
```

O navega desde el menú:  
**Cotizaciones → Simulador PILA**

---

## 📝 EJEMPLO DE USO

**Input**:
- Salario Base: `1300000`
- Nivel Riesgo: `1` (Oficinas)
- Salario Integral: ⬜ (OFF)
- Empresa Exonerada: ✅ (ON)

**Click**: "Calcular Aportes PILA"

**Output**:
- 🔴 Empleado: $104,000
- 🔵 Empleador: $214,786
- 🟢 TOTAL: $318,786

---

## ✅ VERIFICAR INSTALACIÓN

```powershell
python TEST_SIMULADOR_UI.py
```

Resultado esperado:
```
✅ TODAS LAS VALIDACIONES PASARON
```

---

## 📚 DOCUMENTACIÓN COMPLETA

- **Guía Visual**: `SIMULADOR_PILA_UI.md`
- **Entrega**: `ENTREGA_SIMULADOR_UI.md`
- **API**: `INTEGRACION_PILA_API.md`
- **Motor**: `PILA_V1_1_RESUMEN.md`

---

## 🆘 PROBLEMAS COMUNES

### ❌ "Template not found"
```powershell
# Verifica que el archivo existe
Test-Path "templates/simulador_pila.html"
# Debe retornar: True
```

### ❌ "JavaScript no carga"
```powershell
# Verifica ruta
Test-Path "assets/js/simulador-pila.js"
# Abre DevTools → Network → Busca simulador-pila.js (200 OK)
```

### ❌ "Error 401"
```
Solución: Hacer login primero en /login
```

---

## 🎯 URL IMPORTANTE

```
http://localhost:5000/api/cotizaciones/simulador
```

¡Eso es todo! 🚀
