-- Insert users (including at least one owner)
INSERT INTO User (name, password, is_owner) VALUES
('admin', SHA2('admin123', 256), 1),
('juan', SHA2('juan123', 256), 0),
('maria', SHA2('maria123', 256), 0),
('carlos', SHA2('carlos123', 256), 0),
('ana', SHA2('ana123', 256), 0);

-- Insert payment methods
INSERT INTO Payment_Method (name) VALUES
('Efectivo'),
('Tarjeta de credito'),
('Tarjeta de debito'),
('Transferencia'),
('Vales');

-- Insert product types
INSERT INTO Product_Type (name, description) VALUES
('Abarrotes', 'Productos básicos y comestibles'),
('Bebidas', 'Refrescos, jugos y bebidas'),
('Lácteos', 'Leche, quesos y derivados'),
('Limpieza', 'Productos de limpieza del hogar'),
('Botanas', 'Frituras y snacks');

-- Insert stock records
INSERT INTO Stock (available, minimum, last_restock) VALUES
(100.00, 20.00, CURRENT_TIMESTAMP),
(50.00, 10.00, CURRENT_TIMESTAMP),
(75.00, 15.00, CURRENT_TIMESTAMP),
(200.00, 30.00, CURRENT_TIMESTAMP),
(150.00, 25.00, CURRENT_TIMESTAMP),
(80.00, 20.00, CURRENT_TIMESTAMP),
(120.00, 25.00, CURRENT_TIMESTAMP),
(90.00, 15.00, CURRENT_TIMESTAMP),
(60.00, 10.00, CURRENT_TIMESTAMP),
(180.00, 30.00, CURRENT_TIMESTAMP);

-- Insert products
INSERT INTO Product (name, type_id, description, barcode, unit_price, stock_id) VALUES
('Arroz Premium 1kg', 1, 'Arroz grano largo', '7501234567890', 32.50, 1),
('Coca-Cola 2L', 2, 'Refresco cola', '7501234567891', 28.00, 2),
('Leche Alpura 1L', 3, 'Leche entera', '7501234567892', 26.50, 3),
('Fabuloso 1L', 4, 'Limpiador multiusos', '7501234567893', 18.00, 4),
('Sabritas Original 45g', 5, 'Papas fritas', '7501234567894', 15.50, 5),
('Frijoles 1kg', 1, 'Frijoles negros', '7501234567895', 35.00, 6),
('Agua Epura 1.5L', 2, 'Agua purificada', '7501234567896', 12.00, 7),
('Queso Oaxaca 400g', 3, 'Queso para quesadillas', '7501234567897', 85.00, 8),
('Pinol 1L', 4, 'Limpiador para pisos', '7501234567898', 22.00, 9),
('Doritos Nacho 65g', 5, 'Frituras de maíz', '7501234567899', 18.50, 10);

-- Insert tickets
INSERT INTO Ticket (user_id, payment_id, amount) VALUES
(2, 1, 126.50),  -- Juan, efectivo
(3, 2, 85.00),   -- Maria, tarjeta de crédito
(4, 1, 56.50),   -- Carlos, efectivo
(5, 3, 198.00),  -- Ana, tarjeta de débito
(2, 1, 45.50);   -- Juan, efectivo

-- Insert ticket products
INSERT INTO Ticket_Product (ticket_id, product_id, quantity) VALUES
(1, 1, 2.00),  -- 2 kg de arroz
(1, 3, 1.00),  -- 1 leche
(2, 8, 1.00),  -- 1 queso oaxaca
(3, 2, 1.00),  -- 1 coca cola
(3, 5, 2.00),  -- 2 sabritas
(4, 1, 3.00),  -- 3 kg de arroz
(4, 4, 2.00),  -- 2 fabuloso
(5, 5, 1.00),  -- 1 sabritas
(5, 10, 2.00); -- 2 doritos