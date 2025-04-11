-- Insertar eventos principales
INSERT INTO eventos (name, date, location) 
VALUES
    ('Concierto UVG', '2025-05-15', 'Auditorio UVG'),
    ('Conferencia de Tecnología', '2025-06-20', 'Salón de Conferencias'),
    ('Festival de Cine', '2025-07-10', 'Cineplex UVG'),
    ('Exposición de Arte', '2025-08-20', 'Galería de Arte UVG');

-- Insertar usuarios
INSERT INTO usuarios (name, email)
VALUES
    ('Juan Pérez', 'juan.perez@mail.com'),
    ('María González', 'maria.gonzalez@mail.com'),
    ('Carlos Ruiz', 'carlos.ruiz@mail.com'),
    ('Laura López', 'laura.lopez@mail.com'),
    ('Fernando Ramírez', 'fernando.ramirez@mail.com'),
    ('Beatriz Sánchez', 'beatriz.sanchez@mail.com'),
    ('Gabriela Torres', 'gabriela.torres@mail.com'),
    ('Ricardo Morales', 'ricardo.morales@mail.com'),
    ('Ana Castillo', 'ana.castillo@mail.com'),
    ('Jorge Vega', 'jorge.vega@mail.com'),
    ('Mónica Flores', 'monica.flores@mail.com');

-- Insertar asientos para todos los eventos
INSERT INTO asientos (id_evento, numero_asiento)
SELECT e.id_evento, nums.n
FROM eventos e
CROSS JOIN generate_series(1, 10) AS nums(n)
ORDER BY e.id_evento;

-- Insertar reservas usando IDs relativos
INSERT INTO reservas (id_asiento, id_usuario)
SELECT 
    a.id_asiento, 
    u.id_usuario
FROM 
    asientos a
JOIN 
    usuarios u ON u.id_usuario BETWEEN 1 AND 11
WHERE 
    (a.id_evento = (SELECT id_evento FROM eventos WHERE name = 'Festival de Cine') AND a.numero_asiento = u.id_usuario)
    OR
    (a.id_evento = (SELECT id_evento FROM eventos WHERE name = 'Exposición de Arte') AND a.numero_asiento = u.id_usuario - 5)
LIMIT 20;