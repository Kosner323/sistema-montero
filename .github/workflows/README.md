# GitHub Actions Workflows - Sistema Montero

Este directorio contiene los workflows de GitHub Actions para automatizar CI/CD.

## Workflows Disponibles

### 1. `format-and-test.yml` - Pipeline Simplificado
**Propósito:** Verificación rápida de formateo y tests
**Trigger:** Push y PR a `main` o `master`
**Jobs:**
- ✅ Format Check (Black)
- ✅ Run Tests (Python 3.10, 3.11, 3.12)
- ✅ Summary

**Uso recomendado:** Para desarrollo diario y PRs pequeños

### 2. `ci.yml` - Pipeline Completo
**Propósito:** Verificación exhaustiva de calidad y tests
**Trigger:** Push y PR a `main` o `develop`
**Jobs:**
- ✅ Tests & Coverage (Python 3.10, 3.11)
- ✅ Code Quality & Linting (Black, Flake8, Pylint, isort)
- ✅ Build Check

**Uso recomendado:** Para releases y cambios importantes

### 3. `security.yml` (existente)
**Propósito:** Análisis de seguridad del código

### 4. `deploy.yml` (existente)
**Propósito:** Despliegue automático

## Cómo Funcionan

### Proceso Automático

1. **Desarrollador hace push:**
```bash
git push origin main
```

2. **GitHub Actions se activa automáticamente**

3. **Ejecuta los workflows:**
   - Format Check (verifica Black)
   - Tests (ejecuta pytest)
   - Linting (analiza calidad)

4. **Muestra resultados:**
   - ✅ Verde: Todo OK
   - ❌ Rojo: Algo falló

### Ver Resultados

1. Ve a la pestaña **Actions** en GitHub
2. Haz clic en el workflow que se ejecutó
3. Ve los logs de cada job

## Configuración de Protección de Rama

Para hacer que los checks sean obligatorios:

1. **Settings** > **Branches**
2. **Add rule** para `main`
3. Marca:
   - ☑ Require status checks to pass
   - ☑ Format Check (Black)
   - ☑ Run Tests
4. **Save**

Ahora no se podrá hacer merge si los checks fallan.

## Solución de Problemas

### El workflow no se ejecuta
- Verifica que el archivo esté en `.github/workflows/`
- Verifica que la sintaxis YAML sea correcta
- Verifica que el trigger esté configurado para la rama correcta

### Los checks fallan
- Ve los logs en la pestaña Actions
- Ejecuta los mismos comandos localmente:
  ```bash
  black --check .
  pytest
  ```
- Arregla los errores y vuelve a hacer push

## Modificar Workflows

Para modificar un workflow:

1. Edita el archivo `.yml`
2. Haz commit y push
3. El nuevo workflow se ejecutará en el siguiente push

## Referencias

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
