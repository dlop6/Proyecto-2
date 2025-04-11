-- Elimina tablas si existen (para desarrollo)
DROP TABLE IF EXISTS reservas CASCADE;
DROP TABLE IF EXISTS asientos CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;
DROP TABLE IF EXISTS eventos CASCADE;


-- Tabla de eventos
CREATE TABLE eventos (
    id_evento SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    location VARCHAR(255) NOT NULL
);

-- Tabla de asientos (relacionada con eventos)
CREATE TABLE asientos (
    id_asiento SERIAL PRIMARY KEY,
    id_evento INT REFERENCES eventos(id_evento),  -- Relaciona el asiento con el evento
    numero_asiento INT NOT NULL,                   -- Número del asiento
    UNIQUE (id_evento, numero_asiento)             -- Asiento único dentro del evento
);

-- Tabla de usuarios
CREATE TABLE usuarios (
    id_usuario SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE  -- Email único
);

-- Tabla de reservas (relacionada con asientos y usuarios)
CREATE TABLE reservas (
    id_reserva SERIAL PRIMARY KEY,
    id_asiento INT NOT NULL,
    id_usuario INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (id_asiento, id_usuario),  -- No se permite que el mismo usuario reserve el mismo asiento
    FOREIGN KEY (id_asiento) REFERENCES asientos(id_asiento),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);
