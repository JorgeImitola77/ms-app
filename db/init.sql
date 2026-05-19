-- Habilitar extensión para UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Tabla Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    usuario_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    auth0_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    nombre_completo VARCHAR(255),
    rol VARCHAR(50) DEFAULT 'usuario',
    ultimo_acceso TIMESTAMP
);

-- 2. Tabla Personas
CREATE TABLE IF NOT EXISTS personas (
    nro_documento VARCHAR(10) PRIMARY KEY CHECK (nro_documento ~ '^[0-9]{1,10}$'),
    tipo_documento VARCHAR(30) NOT NULL CHECK (tipo_documento IN ('Tarjeta de identidad', 'Cédula')),
    primer_nombre VARCHAR(30) NOT NULL CHECK (primer_nombre !~ '[0-9]'),
    segundo_nombre VARCHAR(30) CHECK (segundo_nombre !~ '[0-9]'),
    apellidos VARCHAR(60) NOT NULL CHECK (apellidos !~ '[0-9]'),
    fecha_nacimiento DATE NOT NULL,
    genero VARCHAR(20) NOT NULL CHECK (genero IN ('Masculino', 'Femenino', 'No binario', 'Prefiero no reportar')),
    correo VARCHAR(100) NOT NULL,
    celular CHAR(10) NOT NULL CHECK (celular ~ '^[0-9]{10}$'),
    foto_ruta TEXT,
    creado_por UUID REFERENCES usuarios(usuario_id),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabla Logs
CREATE TABLE IF NOT EXISTS logs (
    id_log SERIAL PRIMARY KEY,
    usuario_id UUID REFERENCES usuarios(usuario_id),
    fecha_transaccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_transaccion VARCHAR(50) NOT NULL,
    documento_relacionado VARCHAR(10),
    pregunta_rag TEXT,
    respuesta_rag TEXT,
    detalle TEXT NOT NULL
);