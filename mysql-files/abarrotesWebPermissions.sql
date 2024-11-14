SELECT host, user FROM mysql.user WHERE user = 'root';
SHOW GRANTS FOR 'root'@'%';

CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY 'apolo9494';
GRANT ALL PRIVILEGES ON abarrotesWeb.* TO 'root'@'%';
FLUSH PRIVILEGES;
                        