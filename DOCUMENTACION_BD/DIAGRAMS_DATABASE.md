# Diagrama de Base de Datos - Sistema Montero

## Diagrama ER (Entity Relationship)

```mermaid
erDiagram
    EMPRESAS ||--o{ USUARIOS : "tiene"
    
    EMPRESAS {
        INTEGER id PK "Identificador único"
        TEXT nombre_empresa "Razón social"
        TEXT tipo_identificacion_empresa "Tipo de documento"
        TEXT nit UK "NIT - Clave foránea referenciada"
        TEXT direccion_empresa "Dirección física"
        TEXT telefono_empresa "Teléfono principal"
        TEXT correo_empresa "Email corporativo"
        TEXT departamento_empresa "Departamento"
        TEXT ciudad_empresa "Ciudad"
        REAL ibc_empresa "Ingreso Base Cotización"
        TEXT afp_empresa "Fondo de pensiones"
        TEXT arl_empresa "ARL"
        TEXT rep_legal_nombre "Representante legal"
        TEXT rep_legal_tipo_id "Tipo ID rep legal"
        TEXT rep_legal_numero_id "# ID rep legal"
        TEXT created_at "Fecha creación"
    }
    
    USUARIOS {
        INTEGER id PK "Identificador único"
        TEXT empresa_nit FK "NIT empresa (FK)"
        TEXT tipoId "Tipo documento"
        TEXT numeroId "Número documento"
        TEXT primerNombre "Primer nombre"
        TEXT segundoNombre "Segundo nombre"
        TEXT primerApellido "Primer apellido"
        TEXT segundoApellido "Segundo apellido"
        TEXT sexoBiologico "Sexo biológico"
        TEXT sexoIdentificacion "Identidad género"
        TEXT nacionalidad "Nacionalidad"
        TEXT fechaNacimiento "Fecha nacimiento"
        TEXT paisNacimiento "País nacimiento"
        TEXT departamentoNacimiento "Depto nacimiento"
        TEXT municipioNacimiento "Municipio nacimiento"
        TEXT direccion "Dirección residencia"
        TEXT telefonoCelular "Celular"
        TEXT telefonoFijo "Teléfono fijo"
        TEXT correoElectronico "Email personal"
        TEXT comunaBarrio "Comuna/Barrio"
        TEXT afpNombre "AFP"
        REAL afpCosto "Costo AFP"
        TEXT epsNombre "EPS"
        REAL epsCosto "Costo EPS"
        TEXT arlNombre "ARL"
        REAL arlCosto "Costo ARL"
        TEXT ccfNombre "Caja Compensación"
        REAL ccfCosto "Costo CCF"
        TEXT administracion "Administración"
        REAL ibc "Ingreso Base Cotización"
        TEXT claseRiesgoARL "Clase riesgo"
        TEXT fechaIngreso "Fecha ingreso empresa"
        TEXT created_at "Fecha creación registro"
    }
    
    FORMULARIOS_IMPORTADOS {
        INTEGER id PK "Identificador único"
        TEXT nombre "Nombre formulario"
        TEXT nombre_archivo UK "Nombre archivo PDF"
        TEXT ruta_archivo "Ruta completa archivo"
        TEXT campos_mapeados "JSON con mapeo campos"
        TEXT created_at "Fecha importación"
    }
```

## Diagrama de Clases (Estructura de Datos)

```mermaid
classDiagram
    class Empresas {
        +INTEGER id
        +TEXT nombre_empresa
        +TEXT nit [UNIQUE]
        +TEXT direccion_empresa
        +TEXT correo_empresa
        +TEXT ciudad_empresa
        +TEXT rep_legal_nombre
        +obtener_empleados()
        +calcular_costos_totales()
        +validar_nit()
    }
    
    class Usuarios {
        +INTEGER id
        +TEXT empresa_nit [FK]
        +TEXT numeroId
        +TEXT primerNombre
        +TEXT primerApellido
        +TEXT correoElectronico
        +REAL ibc
        +TEXT fechaIngreso
        +obtener_empresa()
        +calcular_seguridad_social()
        +nombre_completo()
        +edad()
    }
    
    class FormulariosImportados {
        +INTEGER id
        +TEXT nombre
        +TEXT nombre_archivo [UNIQUE]
        +TEXT ruta_archivo
        +TEXT campos_mapeados [JSON]
        +cargar_formulario()
        +mapear_campos()
        +validar_pdf()
    }
    
    class AuditLog {
        +INTEGER id
        +TEXT tabla
        +INTEGER registro_id
        +TEXT accion
        +TEXT usuario
        +TEXT fecha_hora
        +TEXT datos_anteriores [JSON]
        +TEXT datos_nuevos [JSON]
        +registrar_cambio()
        +obtener_historial()
    }
    
    Empresas "1" --> "0..*" Usuarios : tiene >
    Usuarios "0..*" --> "1" Empresas : pertenece a >
```

## Flujo de Datos

```mermaid
flowchart TD
    A[Crear Empresa] --> B{Validar NIT}
    B -->|NIT Válido| C[Guardar en tabla EMPRESAS]
    B -->|NIT Duplicado| D[Error: NIT ya existe]
    
    C --> E[Registrar Empleados]
    E --> F{Validar Documento}
    F -->|Documento Válido| G[Guardar en tabla USUARIOS]
    F -->|Documento Duplicado| H[Error: Empleado ya existe]
    
    G --> I[Asociar empresa_nit con empresas.nit]
    I --> J[Calcular Costos Seguridad Social]
    
    K[Importar Formulario] --> L{Validar PDF}
    L -->|PDF Válido| M[Guardar en FORMULARIOS_IMPORTADOS]
    L -->|PDF Inválido| N[Error: PDF corrupto]
    
    M --> O[Mapear Campos JSON]
    O --> P[Listo para Rellenar]
    
    style C fill:#90EE90
    style G fill:#90EE90
    style M fill:#90EE90
    style D fill:#FFB6C1
    style H fill:#FFB6C1
    style N fill:#FFB6C1
```

## Índices y Performance

```mermaid
graph LR
    A[Consultas Frecuentes] --> B[empresas.nit]
    A --> C[usuarios.empresa_nit]
    A --> D[usuarios.numeroId]
    A --> E[usuarios.correoElectronico]
    A --> F[formularios.nombre_archivo]
    
    B --> G[ÍNDICE: idx_empresas_nit UNIQUE]
    C --> H[ÍNDICE: idx_usuarios_empresa]
    D --> I[ÍNDICE: idx_usuarios_documento UNIQUE]
    E --> J[ÍNDICE: idx_usuarios_email]
    F --> K[ÍNDICE: idx_formularios_archivo UNIQUE]
    
    style G fill:#87CEEB
    style H fill:#87CEEB
    style I fill:#87CEEB
    style J fill:#87CEEB
    style K fill:#87CEEB
```

## Estados de Migración (Recomendado)

```mermaid
stateDiagram-v2
    [*] --> EsquemaActual: Base de datos actual
    
    EsquemaActual --> BackupCreado: 1. Hacer backup
    BackupCreado --> IndicesCreados: 2. Crear índices UNIQUE
    IndicesCreados --> ConstraintsAgregados: 3. Agregar NOT NULL
    ConstraintsAgregados --> TablaAuditoria: 4. Crear audit_log
    TablaAuditoria --> VistasCreadas: 5. Crear vistas
    VistasCreadas --> TriggersCreados: 6. Crear triggers
    TriggersCreados --> EsquemaMejorado: 7. Esquema optimizado
    
    EsquemaMejorado --> [*]: ✅ Migración completa
    
    IndicesCreados --> BackupCreado: Error: Rollback
    ConstraintsAgregados --> BackupCreado: Error: Rollback
```

## Arquitectura de 3 Capas

```mermaid
graph TB
    subgraph "Capa de Presentación"
        A[Templates HTML]
        B[Formularios Web]
        C[Reportes PDF]
    end
    
    subgraph "Capa de Lógica de Negocio"
        D[Flask App]
        E[Blueprints]
        F[Validaciones]
        G[Business Rules]
    end
    
    subgraph "Capa de Datos"
        H[(empresas)]
        I[(usuarios)]
        J[(formularios_importados)]
        K[(audit_log)]
    end
    
    A --> D
    B --> D
    C --> D
    
    D --> E
    E --> F
    F --> G
    
    G --> H
    G --> I
    G --> J
    G --> K
    
    style H fill:#FFE4B5
    style I fill:#FFE4B5
    style J fill:#FFE4B5
    style K fill:#FFE4B5
```

## Timeline de Mejoras (Plan de Acción)

```mermaid
gantt
    title Plan de Mejoras - Base de Datos
    dateFormat YYYY-MM-DD
    section Semana 1
    Configurar .env           :done, s1d1, 2025-10-28, 1d
    Corregir encoding         :done, s1d2, 2025-10-29, 1d
    Implementar encriptación  :active, s1d3, 2025-10-30, 1d
    Refactorizar auth         :s1d4, 2025-10-31, 1d
    Implementar logging       :s1d5, 2025-11-01, 1d
    
    section Semana 2
    Reorganizar estructura    :s2d1, 2025-11-04, 2d
    Documentar BD             :crit, done, s2d3, 2025-10-30, 1d
    Implementar Alembic       :s2d4, 2025-11-07, 1d
    Corregir rutas assets     :s2d5, 2025-11-08, 1d
    
    section Semana 3
    Tests básicos             :s3d1, 2025-11-11, 2d
    Validaciones Pydantic     :s3d3, 2025-11-13, 2d
    Code review               :s3d5, 2025-11-15, 1d
```

---

## Notas de Implementación

### Prioridad Alta 🔴
- Agregar UNIQUE constraint en `empresas.nit`
- Agregar UNIQUE constraint en `usuarios(tipoId, numeroId)`
- Hacer NOT NULL campos críticos

### Prioridad Media 🟠
- Crear índices en campos de búsqueda frecuente
- Implementar tabla audit_log
- Crear vistas útiles

### Prioridad Baja 🟡
- Normalizar datos de seguridad social
- Migrar fechas de TEXT a INTEGER
- Implementar triggers de auditoría

---

*Diagramas generados para documentación de base de datos - 30 octubre 2025*
