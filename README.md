# Proyecto_MedioCiclo_FNAFBET
Tarea de proyecto Python con Flask


IMPORTANTE:
Crear base de datos y usuario:

```bash
-- Crear Base de datos
CREATE DATABASE fnafbet;

-- Crear usuario 
CREATE USER 'fnafbeta'@'localhost' IDENTIFIED BY 'Fnaf123!';

-- Darle todos los privilegios sobre la base de datos fnafbet
GRANT ALL PRIVILEGES ON fnafbet.* TO 'fnafbeta'@'localhost';

-- Aplicar los cambios
FLUSH PRIVILEGES;
```