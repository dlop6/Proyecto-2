-- Insertar eventos
INSERT INTO eventos (name, date, location) 
VALUES
    ('Concierto de Música', '2025-05-01', 'Auditorio Principal'),
    ('Conferencia de Tecnología', '2025-05-15', 'Salón de Conferencias A'),
    ('Obra de Teatro', '2025-06-01', 'Teatro Central');

-- Insertar asientos para cada evento
-- Para el evento 'Concierto de Música' (id_evento = 1)
INSERT INTO asientos (id_evento, numero_asiento) 
VALUES
    (1, 1),
    (1, 2),
    (1, 3),
    (1, 4),
    (1, 5),
    (1, 6),
    (1, 7),
    (1, 8),
    (1, 9),
    (1, 10);

-- Para el evento 'Conferencia de Tecnología' (id_evento = 2)
INSERT INTO asientos (id_evento, numero_asiento) 
VALUES
    (2, 1),
    (2, 2),
    (2, 3),
    (2, 4),
    (2, 5),
    (2, 6),
    (2, 7),
    (2, 8),
    (2, 9),
    (2, 10);

-- Para el evento 'Obra de Teatro' (id_evento = 3)
INSERT INTO asientos (id_evento, numero_asiento) 
VALUES
    (3, 1),
    (3, 2),
    (3, 3),
    (3, 4),
    (3, 5),
    (3, 6),
    (3, 7),
    (3, 8),
    (3, 9),
    (3, 10);

-- Insertar usuarios
INSERT INTO usuarios (name, email)
VALUES
    ('Juan Pérez', 'juan.perez@mail.com'),
    ('María González', 'maria.gonzalez@mail.com'),
    ('Carlos Ruiz', 'carlos.ruiz@mail.com'),
    ('Laura López', 'laura.lopez@mail.com'),
    ('Fernando Ramírez', 'fernando.ramirez@mail.com'),
    ('Sofía Martínez', 'sofia.martinez@mail.com'),
    ('Luis García', 'luis.garcia@mail.com'),
    ('Paola Díaz', 'paola.diaz@mail.com'),
    ('Andrés Herrera', 'andres.herrera@mail.com'),
    ('Beatriz Sánchez', 'beatriz.sanchez@mail.com');

-- Insertar reservas (asumiendo que los usuarios y asientos están disponibles)
INSERT INTO reservas (id_asiento, id_usuario)
VALUES
    -- Reservas para el evento 'Concierto de Música' (id_evento = 1)
    (1, 1),  -- Juan Pérez reserva el asiento 1
    (2, 2),  -- María González reserva el asiento 2
    (3, 3),  -- Carlos Ruiz reserva el asiento 3
    (4, 4),  -- Laura López reserva el asiento 4
    (5, 5),  -- Fernando Ramírez reserva el asiento 5
    (6, 6),  -- Sofía Martínez reserva el asiento 6
    (7, 7),  -- Luis García reserva el asiento 7
    (8, 8),  -- Paola Díaz reserva el asiento 8
    (9, 9),  -- Andrés Herrera reserva el asiento 9
    (10, 10), -- Beatriz Sánchez reserva el asiento 10

    -- Reservas para el evento 'Conferencia de Tecnología' (id_evento = 2)
    (11, 1),  -- Juan Pérez reserva el asiento 1
    (12, 2),  -- María González reserva el asiento 2
    (13, 3),  -- Carlos Ruiz reserva el asiento 3
    (14, 4),  -- Laura López reserva el asiento 4
    (15, 5),  -- Fernando Ramírez reserva el asiento 5
    (16, 6),  -- Sofía Martínez reserva el asiento 6
    (17, 7),  -- Luis García reserva el asiento 7
    (18, 8),  -- Paola Díaz reserva el asiento 8
    (19, 9),  -- Andrés Herrera reserva el asiento 9
    (20, 10), -- Beatriz Sánchez reserva el asiento 10

    -- Reservas para el evento 'Obra de Teatro' (id_evento = 3)
    (21, 1),  -- Juan Pérez reserva el asiento 1
    (22, 2),  -- María González reserva el asiento 2
    (23, 3),  -- Carlos Ruiz reserva el asiento 3
    (24, 4),  -- Laura López reserva el asiento 4
    (25, 5),  -- Fernando Ramírez reserva el asiento 5
    (26, 6),  -- Sofía Martínez reserva el asiento 6
    (27, 7),  -- Luis García reserva el asiento 7
    (28, 8),  -- Paola Díaz reserva el asiento 8
    (29, 9),  -- Andrés Herrera reserva el asiento 9
    (30, 10); -- Beatriz Sánchez reserva el asiento 10
