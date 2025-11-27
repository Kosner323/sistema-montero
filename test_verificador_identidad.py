#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de validación para el Verificador de Identidad (Bloque 1 Refinado).
Verifica que:
1. El HTML del Bloque 1 tenga los 4 campos correctos
2. La función buscarAfiliado esté implementada
3. Las librerías SweetAlert2 y Toastify estén incluidas
4. Los event listeners estén configurados correctamente
"""

import os
import sys

# Colores para terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")

def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")

def print_info(msg):
    print(f"{BLUE}ℹ{RESET} {msg}")

def print_warning(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")

def check_html_structure():
    """Verifica la estructura HTML del Bloque 1."""
    index_path = "templates/formularios/index.html"
    if not os.path.exists(index_path):
        print_error("index.html no encontrado")
        return False
    
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("BLOQUE 1: VERIFICADOR DE IDENTIDAD", "Título del bloque actualizado"),
        ('id="selectTipoId"', "Campo Tipo ID (select)"),
        ('id="inputNumeroId"', "Campo Número ID (input)"),
        ('id="inputNombreUsuario"', "Campo Nombre Usuario (readonly)"),
        ('class="form-control bg-light"', "Campo readonly con bg-light"),
        ('onsubmit="buscarAfiliado(event)"', "Form con onsubmit configurado"),
        ('<i class="ti ti-user-search', "Icono de búsqueda de usuario"),
    ]
    
    all_ok = True
    for pattern, description in checks:
        if pattern in content:
            print_success(description)
        else:
            print_error(f"{description} NO encontrado")
            all_ok = False
    
    return all_ok

def check_javascript_function():
    """Verifica que la función buscarAfiliado esté implementada."""
    index_path = "templates/formularios/index.html"
    if not os.path.exists(index_path):
        return False
    
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("function buscarAfiliado(event)", "Función buscarAfiliado definida"),
        ("event.preventDefault()", "Prevención de submit por defecto"),
        ("usuarioEncontrado = usuariosStore.find", "Búsqueda estricta en usuariosStore"),
        ("u.numeroId.toString() === numeroId", "Comparación exacta por numeroId"),
        ("Swal.fire", "Uso de SweetAlert2 para alertas"),
        ("Toastify", "Uso de Toastify para notificaciones toast"),
        ("Usuario Encontrado:", "Mensaje de éxito implementado"),
        ("Usuario No Encontrado", "Mensaje de error implementado"),
        ("renderizarTablaUsuarios([usuarioEncontrado])", "Renderizado con único usuario"),
    ]
    
    all_ok = True
    for pattern, description in checks:
        if pattern in content:
            print_success(description)
        else:
            print_error(f"{description} NO encontrado")
            all_ok = False
    
    return all_ok

def check_libraries():
    """Verifica que las librerías necesarias estén incluidas."""
    index_path = "templates/formularios/index.html"
    if not os.path.exists(index_path):
        return False
    
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("sweetalert2@11", "SweetAlert2 CDN incluido"),
        ("toastify-js", "Toastify CDN incluido"),
        ("sweetalert2.min.css", "SweetAlert2 CSS incluido"),
        ("toastify.min.css", "Toastify CSS incluido"),
    ]
    
    all_ok = True
    for pattern, description in checks:
        if pattern in content:
            print_success(description)
        else:
            print_error(f"{description} NO encontrado")
            all_ok = False
    
    return all_ok

def check_removed_elements():
    """Verifica que los elementos antiguos hayan sido eliminados."""
    index_path = "templates/formularios/index.html"
    if not os.path.exists(index_path):
        return False
    
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    removed_checks = [
        ('id="searchUsuario"', "Input searchUsuario (debe estar eliminado)"),
        ('id="filterEmpresa"', "Select filterEmpresa (debe estar eliminado)"),
        ('id="filterEstado"', "Select filterEstado (debe estar eliminado)"),
        ("function poblarFiltroEmpresas", "Función poblarFiltroEmpresas (debe estar eliminada)"),
        ("function filtrarUsuarios", "Función filtrarUsuarios (debe estar eliminada)"),
    ]
    
    all_ok = True
    for pattern, description in removed_checks:
        if pattern not in content:
            print_success(f"✓ {description} - Correctamente eliminado")
        else:
            print_warning(f"⚠ {description} - AÚN EXISTE (debería estar eliminado)")
            all_ok = False
    
    return all_ok

def check_event_listeners():
    """Verifica que los event listeners estén correctamente configurados."""
    index_path = "templates/formularios/index.html"
    if not os.path.exists(index_path):
        return False
    
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("inputNumeroId')?", "Event listener para Enter en inputNumeroId"),
        ("e.key === 'Enter'", "Detección de tecla Enter"),
        ("formBuscarAfiliado')?", "Referencia al form de búsqueda"),
    ]
    
    all_ok = True
    for pattern, description in checks:
        if pattern in content:
            print_success(description)
        else:
            print_error(f"{description} NO encontrado")
            all_ok = False
    
    return all_ok

def main():
    print("\n" + "="*70)
    print("  VALIDACIÓN - VERIFICADOR DE IDENTIDAD (BLOQUE 1 REFINADO)")
    print("="*70 + "\n")
    
    all_checks_passed = True
    
    # 1. Verificar estructura HTML
    print_info("1. Verificando estructura HTML del Bloque 1...")
    if not check_html_structure():
        all_checks_passed = False
    print()
    
    # 2. Verificar función JavaScript
    print_info("2. Verificando función buscarAfiliado()...")
    if not check_javascript_function():
        all_checks_passed = False
    print()
    
    # 3. Verificar librerías
    print_info("3. Verificando librerías (SweetAlert2 y Toastify)...")
    if not check_libraries():
        all_checks_passed = False
    print()
    
    # 4. Verificar elementos eliminados
    print_info("4. Verificando eliminación de elementos antiguos...")
    if not check_removed_elements():
        all_checks_passed = False
    print()
    
    # 5. Verificar event listeners
    print_info("5. Verificando event listeners...")
    if not check_event_listeners():
        all_checks_passed = False
    print()
    
    # Resumen final
    print("="*70)
    if all_checks_passed:
        print_success("TODAS LAS VERIFICACIONES PASARON ✓")
        print_info("\nFuncionalidad del Verificador de Identidad:")
        print("  1. Usuario selecciona Tipo ID (CC, CE, PEP, etc.)")
        print("  2. Ingresa Número de Documento")
        print("  3. Click en 'Buscar Afiliado' o Enter")
        print("  4. Sistema busca por numeroId (exacto)")
        print("  5. Si existe:")
        print("     → Llena campo Nombre (readonly)")
        print("     → Muestra usuario en tabla")
        print("     → Toast verde: 'Usuario Encontrado: [Empresa]'")
        print("  6. Si NO existe:")
        print("     → Limpia campo Nombre")
        print("     → SweetAlert: 'Usuario No Encontrado'")
        print("     → Tabla vacía")
    else:
        print_error("ALGUNAS VERIFICACIONES FALLARON ✗")
        print_warning("\nRevisa los errores anteriores y corrige los archivos necesarios.")
    
    print("="*70 + "\n")
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())
