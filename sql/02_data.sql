-- Insertar eventos principales
INSERT INTO eventos (nombre, fecha, ubicacion, capacidad) 
VALUES
    ('Concierto UVG', '2025-05-15', 'Auditorio UVG', 100),
    ('Conferencia de Tecnología', '2025-06-20', 'Salón de Conferencias', 50),
    ('Festival de Cine', '2025-07-10', 'Cineplex UVG', 80),
    ('Exposición de Arte', '2025-08-20', 'Galería de Arte UVG', 30);

-- Insertar usuarios
INSERT INTO usuarios (nombre, email)
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
    ('Mónica Flores', 'monica.flores@mail.com'),
    ('Sofía Martínez', 'sofia.martinez@mail.com'),
    ('Luis Hernández', 'luis.hernandez@mail.com'),
    ('Patricia Ortiz', 'patricia.ortiz@mail.com'),
    ('Andrés Gómez', 'andres.gomez@mail.com'),
    ('Valeria Díaz', 'valeria.diaz@mail.com'),
    ('Diego Navarro', 'diego.navarro@mail.com'),
    ('Camila Rojas', 'camila.rojas@mail.com'),
    ('Sebastián Méndez', 'sebastian.mendez@mail.com'),
    ('Isabel Vargas', 'isabel.vargas@mail.com'),
    ('Daniela Fuentes', 'daniela.fuentes@mail.com'),
    ('Héctor Salazar', 'hector.salazar@mail.com'),
    ('Paola Miranda', 'paola.miranda@mail.com'),
    ('Tomás Castillo', 'tomas.castillo@mail.com'),
    ('Lucía Peña', 'lucia.pena@mail.com'),
    ('Emilio Soto', 'emilio.soto@mail.com'),
    ('Regina Paredes', 'regina.paredes@mail.com'),
    ('Mateo Luna', 'mateo.luna@mail.com'),
    ('Victoria Campos', 'victoria.campos@mail.com'),
    ('Martín Reyes', 'martin.reyes@mail.com'),
    ('Elena Silva', 'elena.silva@mail.com'),
    ('Pablo Ortega', 'pablo.ortega@mail.com'),
    ('Carolina Méndez', 'carolina.mendez@mail.com'),
    ('Álvaro Cruz', 'alvaro.cruz@mail.com'),
    ('Natalia Herrera', 'natalia.herrera@mail.com'),
    ('Javier Ramos', 'javier.ramos@mail.com'),
    ('Claudia Núñez', 'claudia.nunez@mail.com'),
    ('Esteban Vargas', 'esteban.vargas@mail.com'),
    ('Mariana Lozano', 'mariana.lozano@mail.com');

-- Insertar asientos para el concierto (filas A-J, asientos 1-10)
DO $$
DECLARE
    filas TEXT[] := ARRAY['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'];
    fila TEXT;
BEGIN
    FOREACH fila IN ARRAY filas LOOP
        FOR num IN 1..10 LOOP
            INSERT INTO asientos (id_evento, numero_asiento, fila)
            VALUES (1, num, fila);
        END LOOP;
    END LOOP;
END $$;

-- Insertar asientos para los otros eventos
INSERT INTO asientos (id_evento, numero_asiento, fila)
SELECT id_evento, generate_series(1, capacidad), 'A'
FROM eventos WHERE id_evento != 1;

-- Insertar algunas reservas iniciales
INSERT INTO reservas (id_asiento, id_usuario)
SELECT 
    a.id_asiento, 
    u.id_usuario
FROM 
    asientos a
JOIN 
    usuarios u ON u.id_usuario BETWEEN 1 AND 5
WHERE 
    a.id_evento = 1 AND a.numero_asiento = u.id_usuario
LIMIT 5;

-- Actualizar estado de asientos reservados
UPDATE asientos SET estado = 'reservado'
WHERE id_asiento IN (SELECT id_asiento FROM reservas);