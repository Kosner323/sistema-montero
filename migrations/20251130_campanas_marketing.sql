-- =====================================================================
-- MIGRACIÓN: TABLA CAMPAÑAS DE MARKETING
-- Fecha: 2024-11-30
-- Descripción: Sistema de gestión de campañas en redes sociales
-- =====================================================================

-- Crear tabla campanas_marketing
CREATE TABLE IF NOT EXISTS campanas_marketing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    plataforma TEXT NOT NULL CHECK(plataforma IN ('Facebook', 'TikTok', 'Instagram', 'LinkedIn', 'Google Ads')),
    estado TEXT DEFAULT 'Borrador' CHECK(estado IN ('Borrador', 'Activa', 'Pausada', 'Finalizada')),
    presupuesto REAL DEFAULT 0.0,
    guion_ia TEXT,
    objetivo TEXT,
    publico_objetivo TEXT,
    fecha_inicio DATE,
    fecha_fin DATE,
    metricas_json TEXT,  -- JSON con impresiones, clics, conversiones
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_campanas_plataforma ON campanas_marketing(plataforma);
CREATE INDEX IF NOT EXISTS idx_campanas_estado ON campanas_marketing(estado);
CREATE INDEX IF NOT EXISTS idx_campanas_fecha_inicio ON campanas_marketing(fecha_inicio);

-- Trigger para actualizar updated_at
CREATE TRIGGER IF NOT EXISTS update_campanas_timestamp 
AFTER UPDATE ON campanas_marketing
BEGIN
    UPDATE campanas_marketing SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Datos de prueba
INSERT INTO campanas_marketing (nombre, plataforma, estado, presupuesto, guion_ia, objetivo) VALUES
    ('Lanzamiento Q1 2025', 'Facebook', 'Borrador', 5000000.0, 'Guion generado por IA: Enfoque en nuevos emprendedores...', 'Generar leads para PILA'),
    ('Campaña TikTok Jóvenes', 'TikTok', 'Activa', 3000000.0, 'Video corto con música trending. CTA: Regístrate ya!', 'Awareness marca'),
    ('LinkedIn Empresas B2B', 'LinkedIn', 'Pausada', 8000000.0, 'Contenido profesional sobre seguridad social empresarial', 'Captación empresas');
