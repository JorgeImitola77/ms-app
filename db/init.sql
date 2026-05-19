-- Habilitar extensión para IA (n8n RAG)
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. TABLA PRINCIPAL: Personas
CREATE TABLE IF NOT EXISTS personas (
    nro_documento VARCHAR(10) PRIMARY KEY,
    tipo_documento VARCHAR(30) NOT NULL CHECK (tipo_documento IN ('Tarjeta de identidad', 'Cédula')),
    primer_nombre VARCHAR(30) NOT NULL,
    segundo_nombre VARCHAR(30),
    apellidos VARCHAR(60) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    genero VARCHAR(20) NOT NULL CHECK (genero IN ('Masculino', 'Femenino', 'No binario', 'Prefiero no reportar')),
    correo VARCHAR(100) NOT NULL,
    celular VARCHAR(10) NOT NULL,
    foto_ruta VARCHAR(255), -- Ajustado según el documento de diseño
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABLA DE AUDITORÍA: Logs
CREATE TABLE IF NOT EXISTS logs (
    id_log SERIAL PRIMARY KEY,
    fecha_transaccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_transaccion VARCHAR(50) NOT NULL,
    documento_relacionado VARCHAR(10), -- Ajustado según el documento de diseño
    detalle TEXT NOT NULL -- Ajustado según el documento de diseño
);

INSERT INTO logs (tipo_transaccion, detalle)
VALUES ('SISTEMA', 'Inicialización de la base de datos completada exitosamente.');