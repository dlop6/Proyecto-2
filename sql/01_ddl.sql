-- Elimina tablas si existen para evitar conflictos al crear nuevas tablas
DROP TABLE IF EXISTS reservas CASCADE;
DROP TABLE IF EXISTS asientos CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;
DROP TABLE IF EXISTS eventos CASCADE;

-- Tabla de eventos
CREATE TABLE eventos (
    id_evento SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    fecha DATE NOT NULL,
    ubicacion VARCHAR(255) NOT NULL,
    capacidad INT NOT NULL
);

-- Tabla de asientos (relacionada con eventos)
CREATE TABLE asientos (
    id_asiento SERIAL PRIMARY KEY,
    id_evento INT NOT NULL REFERENCES eventos(id_evento),
    numero_asiento INT NOT NULL,
    fila VARCHAR(2) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'disponible' CHECK (estado IN ('disponible', 'reservado')),
    UNIQUE (id_evento, numero_asiento, fila)  -- Asiento único dentro del evento
);

-- Tabla de usuarios
CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);

-- Tabla de reservas (relacionada con asientos y usuarios)
CREATE TABLE reservas (
    id_reserva SERIAL PRIMARY KEY,
    id_asiento INT NOT NULL REFERENCES asientos(id_asiento),
    id_usuario INT NOT NULL REFERENCES usuarios(id_usuario),
    fecha_reserva TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (id_asiento)  -- Un asiento solo puede tener una reserva
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_asientos_evento ON asientos(id_evento);
CREATE INDEX idx_asientos_estado ON asientos(estado) WHERE estado = 'disponible';
CREATE INDEX idx_reservas_asiento ON reservas(id_asiento);