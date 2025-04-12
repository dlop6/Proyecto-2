-- Insertar eventos
INSERT INTO eventos (name, date, location) VALUES
('Concierto UVG', '2025-05-15', 'Auditorio UVG'),
('Conferencia de Tecnología', '2025-06-20', 'Salón de Conferencias');

-- Insertar usuarios (solo 2 para prueba)
INSERT INTO usuarios (name, email) VALUES
('Usuario 1', 'usuario1@test.com'),
('Usuario 2', 'usuario2@test.com');

-- Insertar asientos (solo 10 por evento para prueba)
INSERT INTO asientos (id_evento, numero_asiento)
SELECT e.id_evento, nums.n
FROM eventos e
CROSS JOIN generate_series(1, 10) AS nums(n)
ORDER BY e.id_evento;

-- Verificación final
DO $$
BEGIN
    IF (SELECT COUNT(*) FROM asientos) < 20 THEN
        RAISE EXCEPTION 'No se insertaron suficientes asientos';
    END IF;
    RAISE NOTICE 'Datos iniciales insertados correctamente';
END $$;