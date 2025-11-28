# Keep Bouncing Back 


## 🚀 Inicio 

### 1. Clona el repositorio
```bash
git clone <url-del-repositorio>
cd keep-bouncing-back
```

### 2. Instala las dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecuta la aplicación
```bash
uvicorn main:app --reload
```

### 4. Accede a la aplicación
- **API**: http://127.0.0.1:8000
- **Documentación interactiva**: http://127.0.0.1:8000/docs

## 📋 Requisitos
- Python 3.8+
- pip

## 🗄️ Base de Datos

Por defecto usa SQLite. Para usar una base de datos externa:

### 1. Crear la base de datos
Crea una base de datos llamada **KeepBouncing** en tu servidor de base de datos.

### 2. Ejecutar scripts de control de cambios
Corre los scripts desde: https://drive.google.com/drive/u/2/folders/1q7OIxUloZwMZGKEbj3peEtLmeT19RtdN

### 3. Configurar la conexión
Modifica `database.py` según el tipo de base de datos:

### SQLite (por defecto)
```python
DATABASE_URL = "sqlite:///./keep_bouncing_back.db"
```

### PostgreSQL
```python
DATABASE_URL = "postgresql://usuario:password@localhost:5432/nombre_db"
```

### MySQL
```python
DATABASE_URL = "mysql+pymysql://usuario:password@localhost:3306/nombre_db"
```

Después de cambiar, instala el driver correspondiente:
```bash
# Para PostgreSQL
pip install psycopg2-binary

# Para MySQL
pip install pymysql
```


## 🧪 Ejecutar tests

Para ejecutar la suite de pruebas (desde la raíz del proyecto y con el entorno virtual activado):

```bash
python -m pytest tests/
```

Opcionales útiles:
- `-q` — salida más compacta
- `-v` — salida detallada
