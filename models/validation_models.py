# -*- coding: utf-8 -*-
"""
Modelos de Validación Pydantic - Sistema Montero
================================================
Versión: 2.6 - FUSIONADO y CORREGIDO (Pydantic V2)
Fecha: 5 de noviembre de 2025

Este archivo contiene TODOS los modelos de validación:
- Login/Registro actualizados (Sin Snapchat)
- Modelos de Empresa (NIT, Razon Social, etc.)
- Corregida la sintaxis de Config a ConfigDict (Pydantic V2)
"""

import re
from datetime import date
from typing import Optional

# Se añade ConfigDict para la sintaxis moderna de Pydantic V2
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# --- Funciones de Validación Personalizadas (de tu archivo original) ---


def validar_nit(v: str) -> str:
    """Valida formato de NIT colombiano (9-10 dígitos)"""
    if v is None:
        return v
    nit_clean = re.sub(r"[.-]", "", v)
    if not nit_clean.isdigit() or not (9 <= len(nit_clean) <= 10):
        raise ValueError("El NIT debe tener entre 9 y 10 dígitos numéricos")
    return nit_clean


def validar_telefono(v: str) -> str:
    """Valida Teléfono CO (7 o 10 dígitos)"""
    if v is None:
        return v
    tel_clean = re.sub(r"[\s()+-]", "", v)
    if not tel_clean.isdigit() or not len(tel_clean) in (7, 10):
        raise ValueError("El Teléfono debe tener 7 o 10 dígitos numéricos")
    return tel_clean


# --- Modelos de Autenticación (ACTUALIZADOS A Pydantic V2) ---


class LoginRequest(BaseModel):
    """
    Modelo para validar solicitudes de login.
    (Versión actualizada de validation_models2.py)
    """

    email: EmailStr = Field(..., description="Email del usuario", json_schema_extra={"example": "usuario@ejemplo.com"})
    password: str = Field(
        ...,
        min_length=6,
        description="Contraseña del usuario (mínimo 6 caracteres)",
        json_schema_extra={"example": "miPassword123"},
    )

    # --- CORRECCIÓN Pydantic V2 ---
    # Se reemplaza 'class Config:' por 'model_config'
    model_config = ConfigDict(json_schema_extra={"example": {"email": "kevinlomasd@gmail.com", "password": "miPassword123"}})


class RegisterRequest(BaseModel):
    """
    Modelo para validar solicitudes de registro de nuevos usuarios.
    (Versión actualizada de validation_models2.py - SIN SNAPCHAT)
    """

    nombre: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nombre completo del usuario",
        json_schema_extra={"example": "Kevin Montero"},
    )
    email: EmailStr = Field(..., description="Email único del usuario", json_schema_extra={"example": "kevinlomasd@gmail.com"})
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Contraseña del usuario (mínimo 6 caracteres)",
        json_schema_extra={"example": "miPassword123"},
    )
    password_confirm: Optional[str] = Field(
        None,
        min_length=6,
        max_length=128,
        description="Confirmación de contraseña (opcional)",
        json_schema_extra={"example": "miPassword123"},
    )

    # --- NUEVOS CAMPOS OPCIONALES (SIN SNAPCHAT) ---
    telefono: Optional[str] = Field(
        None,
        min_length=8,
        max_length=20,
        pattern=r"^\+?\d{8,20}$",
        description="Teléfono con código de país (ejemplo: +573001234567)",
        json_schema_extra={"example": "+573001234567"},
    )
    fecha_nacimiento: Optional[date] = Field(
        None, description="Fecha de nacimiento en formato YYYY-MM-DD", json_schema_extra={"example": "1990-05-15"}
    )

    @field_validator("password_confirm")
    def passwords_match(cls, v, info):
        """Valida que las contraseñas coincidan (solo si se proporciona)"""
        if v is not None and "password" in info.data and v != info.data["password"]:
            raise ValueError("Las contraseñas no coinciden")
        return v

    @field_validator("nombre")
    def nombre_valido(cls, v):
        """Valida que el nombre no contenga números"""
        if any(char.isdigit() for char in v):
            raise ValueError("El nombre no puede contener números")
        return v.strip()

    @field_validator("email")
    def email_lowercase(cls, v):
        """Convierte el email a minúsculas"""
        return v.lower()

    @field_validator("fecha_nacimiento")
    def fecha_nacimiento_valida(cls, v):
        """Valida que la fecha de nacimiento sea válida y el usuario sea mayor de edad"""
        if v is None:
            return v

        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))

        if age < 13:
            raise ValueError("Debes tener al menos 13 años para registrarte")
        if age > 120:
            raise ValueError("Fecha de nacimiento inválida")

        return v

    # --- CORRECCIÓN Pydantic V2 ---
    # Se reemplaza 'class Config:' por 'model_config'
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Kevin Montero",
                "email": "kevinlomasd@gmail.com",
                "password": "miPassword123",
                "password_confirm": "miPassword123",
                "telefono": "+573001234567",
                "fecha_nacimiento": "1990-05-15",
            }
        }
    )


# --- Modelo de Empresa (DE TU ARCHIVO ORIGINAL) ---


class EmpresaCreate(BaseModel):
    """Esquema para crear una nueva empresa."""

    nit: str
    nombre_empresa: str = Field(..., min_length=3, max_length=200)
    representante_legal: Optional[str] = None
    email: EmailStr
    telefono: str
    direccion: str
    ciudad: str
    cantidad_empleados: Optional[int] = Field(None, gt=0)

    _validate_nit = field_validator("nit", mode="before")(validar_nit)
    _validate_telefono = field_validator("telefono", mode="before")(validar_telefono)


class EmpresaUpdate(BaseModel):
    """Esquema para actualizar una empresa (todos los campos opcionales)."""

    nit: Optional[str] = None
    nombre_empresa: Optional[str] = Field(None, min_length=3, max_length=200)
    representante_legal: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    cantidad_empleados: Optional[int] = Field(None, gt=0)

    # Validadores para campos opcionales
    _validate_nit_opcional = field_validator("nit", mode="before")(validar_nit)
    _validate_telefono_opcional = field_validator("telefono", mode="before")(validar_telefono)


# (Aquí puedes añadir los otros 8 modelos (Incapacidad, Pagos, etc.) cuando los necesites)
