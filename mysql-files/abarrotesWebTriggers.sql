USE abarrotesWeb;

DELIMITER //
CREATE TRIGGER tr_pt_prevent_creation_date_modification BEFORE UPDATE ON Product_Type
FOR EACH ROW
BEGIN
	SET NEW.creation_date = OLD.creation_date;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER tr_p_creation_date_modification BEFORE UPDATE ON Product
FOR EACH ROW
BEGIN
	SET NEW.creation_date = OLD.creation_date;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER tr_p_prevent_negative_unit_price BEFORE INSERT ON Product
FOR EACH ROW
BEGIN
    IF NEW.unit_price <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Price must be a positive value.';
    END IF;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER tr_s_prevent_negative_available BEFORE INSERT ON Stock
FOR EACH ROW
BEGIN
	IF NEW.available <= 0 THEN
		SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Stock must be a positive number.';
	END IF;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER tr_s_prevent_negative_minimum BEFORE INSERT ON Stock
FOR EACH ROW
BEGIN
	IF NEW.minimum <= 0 THEN
		SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Minimum stock must be a positive number.';
	END IF;
END;
DELIMITER ;

DELIMITER //
CREATE TRIGGER tr_tp_prevent_negative_quantity BEFORE INSERT ON Ticket_Product
FOR EACH ROW
BEGIN
	IF NEW.quantity <= 0 THEN
		SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Quantity must be a positive number.';
	END IF;
END;
DELIMTIER ;

DELIMITER //
CREATE TRIGGER tr_t_prevent_negative_amount BEFORE INSERT ON Ticket
FOR EACH ROW
BEGIN
	IF NEW.amount <= 0 THEN
		SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Ticket amount must be a positive number.';
	END IF;
END;
DELIMITER ;

DELIMITER //
CREATE TRIGGER tr_u_prevent_more_owners BEFORE INSERT ON User
FOR EACH ROW
BEGIN
	IF NEW.isOwner = 1 AND (SELECT COUNT(*) FROM User WHERE isOwner = 1) > 0 THEN
		SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'There must be only one owner.';
	END IF;
END;
DELIMITER ;

DELIMITER //
CREATE TRIGGER tr_u_prevent_new_owner BEFORE UPDATE ON User
FOR EACH ROW
BEGIN
	IF NEW.isOwner = 1 AND (SELECT COUNT(*) FROM User WHERE isOwner = 1) > 0 THEN
		SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'There must be only one owner.';
	END IF;
END;
DELIMITER ;

DELIMITER //
CREATE TRIGGER tr_tp_validate_stock_in_quantity 
BEFORE INSERT ON Ticket_Product
FOR EACH ROW
BEGIN
    DECLARE available_stock DECIMAL(6,2);
    
    SELECT s.available INTO available_stock
    FROM Product p
    JOIN Stock s ON s.stock_id = p.stock_id
    WHERE p.product_id = NEW.product_id;
    
    IF available_stock IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Product not found or has no stock record.';
    END IF;
    
    IF (NEW.quantity > available_stock) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Insufficient stock.';
    END IF;
END//
DELIMITER ;