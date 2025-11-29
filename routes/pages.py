# -*- coding: utf-8 -*-
"""
Blueprint para páginas HTML (vistas web)
"""

from flask import Blueprint, render_template, redirect, url_for, session

# Crear Blueprint para páginas
pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/')
def index():
    """Ruta raíz - redirige según estado de sesión"""
    if 'user_id' in session:
        return redirect('/dashboard')
    return redirect('/login')


@pages_bp.route('/login')
def login_page():
    """Muestra la página de login"""
    # Si ya está logueado, redirigir al dashboard
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('auth/login.html')


@pages_bp.route('/registro')
def registro_page():
    """Muestra la página de registro"""
    # Si ya está logueado, redirigir al dashboard
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('auth/register.html')


@pages_bp.route('/dashboard')
def dashboard():
    """Muestra el dashboard principal"""
    # Verificar si está logueado
    if 'user_id' not in session:
        return redirect('/login')

    # Aquí puedes pasar datos del usuario a la plantilla
    return render_template('main/dashboard.html', user=session.get('user'))


@pages_bp.route('/pagos/recaudo')
def pagos_recaudo():
    """Muestra la página de recibo de caja"""
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('pagos/recaudo.html')
