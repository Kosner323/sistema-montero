# -*- coding: utf-8 -*-
"""
Blueprint para las rutas principales de las páginas HTML
(index, login, registro, dashboard, etc.)
"""

from flask import Blueprint, render_template, redirect, url_for
from utils import login_required # <<< IMPORTANTE: Para proteger el dashboard

# 1. Crea el Blueprint principal
# El nombre 'bp_main' debe coincidir con el que importa app.py
bp_main = Blueprint("main", __name__)


# 2. Define la ruta principal ("/")
@bp_main.route("/")
def index():
    """
    Página principal. 
    Redirige al login, que es 'ingresoportal.html'.
    """
    # Redirige a la función 'login' de este mismo blueprint
    return redirect(url_for('main.login'))


# ✅ Ruta de compatibilidad para ingresoportal.html
@bp_main.route("/ingresoportal.html")
def ingresoportal_redirect():
    """
    Redirección de compatibilidad para /ingresoportal.html → /login
    """
    return redirect(url_for('main.login'))


# 3. Define la ruta de LOGIN
@bp_main.route("/login")
def login():
    """
    Muestra la página de inicio de sesión ('auth/login.html').
    """
    return render_template("auth/login.html")


# 4. Define la ruta de REGISTRO
@bp_main.route("/registro")
def register():
    """
    Muestra la página de registro ('auth/register.html').
    """
    return render_template("auth/register.html")


# 5. Define la ruta del DASHBOARD PRINCIPAL
@bp_main.route("/dashboard")
@login_required # <<< PROTECCIÓN: Solo usuarios logueados pueden acceder
def dashboard():
    """
    Muestra la página principal del dashboard ('main/dashboard.html').
    """
    return render_template("main/dashboard.html")


# =============================================================================
# RUTAS DE ADMINISTRACIÓN Y FINANZAS
# =============================================================================

@bp_main.route("/usuarios/gestion")
@login_required
def usuarios_gestion():
    """
    Muestra la página de gestión de usuarios (base de datos).
    """
    return render_template("usuarios/gestion.html")


@bp_main.route("/empresas/ingresar")
@login_required
def empresas_ingresar():
    """
    Muestra la página para ingresar empresas.
    """
    return render_template("empresas/ingresar.html")


@bp_main.route("/unificacion")
@login_required
def unificacion():
    """
    Muestra la página de unificación de datos.
    """
    return render_template("unificacion/panel.html")


@bp_main.route("/test-dropdown")
def test_dropdown():
    """
    Página de prueba para verificar dropdowns Bootstrap 5
    """
    return render_template("test_dropdown.html")


# =============================================================================
# RUTAS DE CONTABILIDAD
# =============================================================================

@bp_main.route("/pagos/recaudo")
@login_required
def pagos_recaudo():
    """
    Muestra la página de recaudo de pagos.
    """
    return render_template("pagos/recaudo.html")


@bp_main.route("/pagos/control")
@login_required
def pagos_control():
    """
    Muestra la tabla de control de pagos.
    """
    return render_template("pagos/control_tabla.html")


@bp_main.route("/pagos/planillas")
@login_required
def pagos_planillas():
    """
    Muestra la página de pago de planillas.
    """
    return render_template("pagos/planillas.html")


@bp_main.route("/planillas/enviar")
@login_required
def planillas_enviar():
    """
    Muestra la página para enviar planillas.
    """
    return render_template("pagos/enviar_planillas.html")


# =============================================================================
# RUTAS DE GESTIÓN OPERATIVA
# =============================================================================

@bp_main.route("/novedades")
@login_required
def novedades_page():
    """
    Muestra la página de novedades del sistema.
    """
    return render_template("novedades/index.html")


@bp_main.route("/novedades/crear")
@login_required
def novedades_crear():
    """
    Muestra el formulario para crear una nueva novedad (página dedicada).
    """
    return render_template("novedades/crear.html")


@bp_main.route("/formularios")
@login_required
def formularios():
    """
    Muestra la página de gestión de formularios.
    """
    return render_template("formularios/index.html")


# =============================================================================
# RUTAS DE GESTIÓN JURÍDICA
# =============================================================================

@bp_main.route("/incapacidades")
@login_required
def incapacidades():
    """
    Muestra la página de gestión de incapacidades.
    """
    return render_template("juridico/incapacidades.html")


@bp_main.route("/incapacidades/crear")
@login_required
def incapacidades_crear():
    """
    Muestra el formulario para crear una nueva incapacidad (página dedicada).
    """
    return render_template("incapacidades/crear.html")


@bp_main.route("/tutelas")
@login_required
def tutelas():
    """
    Muestra la página de gestión de tutelas.
    """
    return render_template("juridico/tutelas.html")


@bp_main.route("/tutelas/crear")
@login_required
def tutelas_crear():
    """
    Muestra el formulario para crear una nueva tutela (página dedicada).
    """
    return render_template("tutelas/crear.html")


@bp_main.route("/depuraciones")
@login_required
def depuraciones():
    """
    Muestra la página de depuraciones.
    """
    return render_template("juridico/depuraciones.html")


@bp_main.route("/depuraciones/crear")
@login_required
def depuraciones_crear():
    """
    Muestra el formulario para iniciar una nueva depuración (página dedicada).
    """
    return render_template("depuraciones/crear.html")


# =============================================================================
# RUTAS DE DOCUMENTACIÓN Y SERVICIO
# =============================================================================

@bp_main.route("/pagos/impuestos")
@login_required
def pagos_impuestos():
    """
    Muestra la página de pago de impuestos.
    """
    return render_template("pagos/impuestos.html")


@bp_main.route("/cotizaciones")
@login_required
def cotizaciones():
    """
    Muestra la página de cotizaciones.
    """
    return render_template("pagos/cotizaciones.html")


@bp_main.route("/informacion/clientes")
@login_required
def informacion_clientes():
    """
    Muestra la página de información para clientes.
    """
    return render_template("informacion-clientes.HTML")


@bp_main.route("/informacion/empleados")
@login_required
def informacion_empleados():
    """
    Muestra la página de información para empleados.
    """
    return render_template("usuarios/info_empleados.html")


# =============================================================================
# RUTAS DE GUÍAS Y ACCESO
# =============================================================================

@bp_main.route("/credenciales")
@login_required
def credenciales():
    """
    Muestra la página de gestión de usuarios y contraseñas.
    """
    return render_template("usuarios/contrasenas.html")


# =============================================================================
# RUTAS DE NUEVAS SECCIONES (Marketing, Copiloto ARL, Gestor de Archivos, Seguridad)
# =============================================================================

@bp_main.route("/copiloto/arl")
@login_required
def copiloto_arl():
    """
    Muestra la página del Copiloto ARL (IA asistente).
    """
    return render_template("copiloto/arl.html")


@bp_main.route("/marketing/redes")
@login_required
def marketing_redes():
    """
    Muestra la página de gestión de redes sociales.
    """
    return render_template("marketing/redes.html")


@bp_main.route("/marketing/campanas")
@login_required
def marketing_campanas():
    """
    Muestra la página de gestión de campañas de marketing.
    """
    return render_template("marketing/campanas.html")


@bp_main.route("/pagos/cartera")
@login_required
def pagos_cartera():
    """
    Muestra la página de gestión de cartera (deudas).
    """
    return render_template("pagos/cartera.html")


@bp_main.route("/gestor-archivos")
@login_required
def gestor_archivos():
    """
    Muestra el gestor de archivos del sistema.
    """
    return render_template("archivos/gestor.html")


@bp_main.route("/auditoria")
@login_required
def auditoria():
    """
    Muestra la página de auditoría y logs del sistema.
    """
    return render_template("auditoria/logs.html")


# =============================================================================
# RUTAS ADICIONALES DE UNIFICACIÓN Y SEGURIDAD
# =============================================================================

@bp_main.route("/unificacion/panel")
@login_required
def unificacion_panel():
    """
    Ruta alternativa para el panel de unificación.
    Apunta al mismo template que /unificacion.
    """
    return render_template("unificacion/panel.html")


@bp_main.route("/seguridad/usuarios")
@login_required
def seguridad_usuarios():
    """
    Muestra la página de gestión de usuarios y contraseñas (Seguridad).
    """
    return render_template("usuarios/contrasenas.html")


@bp_main.route("/marketing/prospectos")
@login_required
def marketing_prospectos():
    """
    Muestra la página de gestión de prospectos de marketing.
    """
    return render_template("marketing/prospectos.html")
