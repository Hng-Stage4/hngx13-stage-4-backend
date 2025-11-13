# ============================================
# init-db.sql
# ============================================
-- Create databases for each service
CREATE DATABASE IF NOT EXISTS user_service;
CREATE DATABASE IF NOT EXISTS template_service;

-- Create users
CREATE USER IF NOT EXISTS 'user_service'@'%' IDENTIFIED BY 'user_password';
CREATE USER IF NOT EXISTS 'template_service'@'%' IDENTIFIED BY 'template_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON user_service.* TO 'user_service'@'%';
GRANT ALL PRIVILEGES ON template_service.* TO 'template_service'@'%';

FLUSH PRIVILEGES;