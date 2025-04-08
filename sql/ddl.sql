CREATE TABLE eventos (
    id_evento SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    location VARCHAR(255) NOT NULL
);

CREATE TABLE usuarios(
    id_usuario SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    
);

CREATE TABLE reservas(
    id_reserva SERIAL PRIMARY KEY,
    id_asiento INT NOT NULL,
    id_usuario INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (id_asiento, id_usuario),
    FOREIGN KEY (id_asiento) REFERENCES asientos(id_asiento),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
    
);