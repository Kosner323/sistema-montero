# 📄 Guía: Cómo Generar PDFs Rellenables

## ✅ Estado del Sistema

**¡TODO ESTÁ LISTO!** El sistema de generación de PDFs está 100% configurado y funcionando:

- ✅ Endpoint `/api/formularios/generar` implementado y funcionando
- ✅ Plantilla PDF disponible: `FORMULARIO EPS COMFENALCO`
- ✅ 8 usuarios registrados en la base de datos
- ✅ 6 empresas registradas en la base de datos
- ✅ Dependencias instaladas: `pypdf`, `werkzeug`
- ✅ Carpetas de almacenamiento configuradas

---

## 🚀 Cómo Usar (Paso a Paso)

### 1. Iniciar el Servidor

```bash
python src/dashboard/app.py
```

El servidor iniciará en: **http://localhost:5000**

### 2. Acceder a la Página de Formularios

Abre tu navegador y ve a:

```
http://localhost:5000/formularios
```

### 3. Iniciar Sesión

- Inicia sesión con cualquier usuario del sistema
- Por ejemplo: **Admin Sistema** (CC: 1000000)

### 4. Seleccionar Datos para el PDF

En la pestaña **"Generar Formulario"**:

1. **Seleccionar Formulario**:
   - Elige: `FORMULARIO EPS COMFENALCO`

2. **Buscar Empleado por Cédula**:
   - Escribe el número de cédula (por ejemplo: `100100100`)
   - Click en el botón de búsqueda 🔍
   - El nombre del empleado aparecerá automáticamente: `Pedro Pérez`

3. **Seleccionar Empresa**:
   - Elige una empresa del menú desplegable
   - Por ejemplo: `Empresa Montero Administradora` (NIT: 999999999)

### 5. Generar y Descargar el PDF

1. Click en el botón **"Generar y Descargar PDF"** 📄
2. El sistema:
   - Consulta los datos del empleado en la base de datos
   - Consulta los datos de la empresa en la base de datos
   - Rellena automáticamente el PDF con todos los datos
   - **Guarda una copia** en la carpeta del usuario
   - **Descarga el PDF** a tu carpeta de Descargas

---

## 📂 Dónde se Guardan los PDFs

Los PDFs generados se guardan automáticamente en:

```
D:\Mi-App-React\MONTERO_NEGOCIO\MONTERO_TOTAL\USUARIOS\
  └── {NÚMERO_CÉDULA}\
      └── EMPRESAS_AFILIADAS\
          └── {NOMBRE_EMPRESA}\
              └── {MES_AÑO}.pdf
```

### Ejemplo:

Para el empleado `Pedro Pérez` (CC: 100100100) afiliado a `Empresa Montero Administradora`:

```
D:\Mi-App-React\MONTERO_NEGOCIO\MONTERO_TOTAL\USUARIOS\
  └── 100100100\
      └── EMPRESAS_AFILIADAS\
          └── EMPRESA_MONTERO_ADMINISTRADORA\
              └── NOVIEMBRE_2025.pdf
```

---

## 🎯 Datos que se Rellenan Automáticamente

El sistema rellena estos campos en el PDF:

### Datos del Empleado (desde tabla `usuarios`)
- Tipo de identificación
- Número de cédula
- Primer y segundo nombre
- Primer y segundo apellido
- Correo electrónico
- Dirección
- Teléfono fijo y celular
- Barrio/Comuna
- Fecha de nacimiento
- Sexo biológico (checkbox)
- Departamento y municipio de nacimiento
- Nacionalidad
- AFP
- Fecha de ingreso
- IBC (Ingreso Base de Cotización)

### Datos de la Empresa (desde tabla `empresas`)
- Nombre de la empresa
- Tipo de identificación
- NIT
- Dirección
- Teléfono
- Correo electrónico
- AFP de la empresa
- ARL de la empresa
- IBC de la empresa
- Departamento y ciudad

---

## 📋 Usuarios Disponibles para Pruebas

| ID | Nombre Completo | Cédula | Rol |
|----|-----------------|--------|-----|
| 1 | Admin Sistema | 1000000 | SUPER |
| 2 | Pedro Pérez | 100100100 | EMPLEADO |
| 3 | Usuario Test | 86810362 | EMPLEADO |

---

## 🏢 Empresas Disponibles para Pruebas

| NIT | Nombre |
|-----|--------|
| 999999999 | Empresa Montero Administradora |
| 900111222 | Innovatech S.A.S |
| 9001234567 | Constructora El Futuro S.A.S. |

---

## 🔧 Importar Nuevas Plantillas PDF

Si quieres agregar más plantillas PDF:

1. Ve a la pestaña **"Importar Nuevo Formulario"**
2. Ingresa un nombre descriptivo (ej: "Formulario SURA ARL")
3. Selecciona el archivo PDF desde tu computadora
4. Click en **"Importar Formulario"**

**Importante**: El PDF debe tener campos rellenables (AcroForm fields) para que el sistema pueda completarlos automáticamente.

---

## ✅ Verificación del Sistema

Si quieres verificar que todo está configurado correctamente, ejecuta:

```bash
python test_pdf_readiness.py
```

Este script te mostrará un reporte completo del estado del sistema.

---

## 🐛 Solución de Problemas

### Problema: "No se encontraron plantillas"
**Solución**: Importa al menos una plantilla PDF desde la interfaz web.

### Problema: "Usuario no encontrado"
**Solución**: Verifica que el número de cédula sea correcto. Busca un usuario existente en la tabla `usuarios`.

### Problema: "Error al generar PDF"
**Solución**:
1. Verifica que el archivo PDF de plantilla exista en `src/dashboard/static/uploads`
2. Verifica que la plantilla tenga campos rellenables
3. Revisa los logs del servidor para más detalles

### Problema: El PDF se genera pero los campos están vacíos
**Solución**: Los nombres de los campos en el PDF deben coincidir con los nombres en el mapeo del código. Puedes verificar los nombres de los campos usando Adobe Acrobat o una herramienta similar.

---

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs del servidor (salida de consola)
2. Verifica que la base de datos tenga los datos necesarios
3. Ejecuta el script de diagnóstico: `python test_pdf_readiness.py`

---

**¡Listo para usar!** 🎉
