# HappinessScore_Predicted

[![Python](https://img.shields.io/badge/Python-3.10-blue)](https://www.python.org/) [![Kafka](https://img.shields.io/badge/Apache_Kafka-2.8.0-red)](https://kafka.apache.org/) [![Docker](https://img.shields.io/badge/Docker-20.10-blue)](https://www.docker.com/) [![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## Descripción General

El proyecto **HappinessScore_Predicted** implementa un pipeline de datos para predecir la **Puntuación de Felicidad** de países utilizando datos del **World Happiness Report** (2015–2019). Este sistema integra extracción y transformación de datos, análisis exploratorio (EDA), un modelo de Bosques Aleatorios, streaming en tiempo real con Apache Kafka y almacenamiento en PostgreSQL. Las visualizaciones generadas ofrecen insights sobre patrones globales de felicidad y el rendimiento del modelo. Docker asegura escalabilidad y reproducibilidad.

### Objetivos Principales
- Normalizar y limpiar los datos del World Happiness Report para garantizar consistencia.
- Realizar EDA para identificar relaciones entre variables.
- Entrenar y serializar un modelo de Bosques Aleatorios para predicciones.
- Procesar datos en tiempo real mediante Kafka.
- Almacenar predicciones en PostgreSQL y evaluar el modelo con métricas y visualizaciones.

La documentación detallada está disponible en [Documentación](Documents/Documentacion_WorkShop3_Actualizada.md).

## Estructura del Repositorio

```
HappinessScore_Predicted/
├── data/                     # Archivos CSV del World Happiness Report (2015–2019)
├── model/                    # Modelo serializado (rf_model.pkl)
├── Documents/                # Documentación del proyecto
│   └── Documentacion_WorkShop3_Actualizada.md
├── env/                      # Archivo de variables de entorno (.env)
├── consumer.py               # Script consumidor de Kafka para predicción y almacenamiento
├── producer.py               # Script productor de Kafka para streaming de datos
├── docker-compose.yml        # Configuración de Docker para Kafka y ZooKeeper
└── README.md                 # Descripción general e instrucciones de configuración
```

## Herramientas y Tecnologías

El pipeline utiliza las siguientes herramientas y librerías:
- **Python 3.10**: Lenguaje principal para procesamiento y modelado.
- **Apache Kafka**: Sistema de mensajería distribuida para streaming en tiempo real.
- **Docker**: Orquestación de contenedores para Kafka y ZooKeeper.
- **PostgreSQL**: Base de datos relacional para almacenamiento de predicciones.
- **Librerías de Python**:
  - **pandas**: Manipulación y transformación de datos.
  - **scikit-learn**: Modelo de Bosques Aleatorios y métricas de evaluación.
  - **matplotlib, seaborn, plotly**: Visualizaciones estáticas e interactivas.
  - **kafka-python-ng**: Cliente de Kafka para operaciones de productor y consumidor.
  - **country-converter**: Estandarización de nombres de países y continentes.
  - **sqlalchemy, psycopg2-binary**: Conexión a PostgreSQL.
  - **python-dotenv**: Gestión de variables de entorno.
  - **joblib**: Serialización de modelos.

Consulta `requirements.txt` (generado durante la configuración) para la lista completa.

## Metodología

1. **Extracción y Transformación de Datos** (`producer.py`):
   - Carga y normaliza datos de archivos CSV (2015–2019).
   - Imputa valores nulos y asigna continentes con `country-converter`.

2. **Análisis Exploratorio de Datos (EDA)**:
   - Genera visualizaciones con Plotly para identificar patrones geográficos.

3. **Entrenamiento y Serialización del Modelo**:
   - Entrena un modelo de Bosques Aleatorios y lo serializa en `rf_model.pkl`.

4. **Streaming en Tiempo Real con Kafka**:
   - Usa Docker para ejecutar Kafka y ZooKeeper (`docker-compose.yml`).
   - `producer.py` envía datos al tópico; `consumer.py` procesa y predice.

5. **Almacenamiento y Evaluación** (`consumer.py`):
   - Almacena resultados en PostgreSQL y evalúa con métricas y visualizaciones.

## Instrucciones de Configuración

### Prerrequisitos
- **Docker**: Instala [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- **Python 3.10**: Descarga desde [python.org](https://www.python.org/downloads/).
- **PostgreSQL**: Instala localmente o usa un servicio gestionado.
- **Git**: Para clonar el repositorio.

### Instalación
1. **Clonar el Repositorio**:
   ```bash
   git clone https://github.com/<tu-usuario>/HappinessScore_Predicted.git
   cd HappinessScore_Predicted
   ```
2. **Configurar Variables de Entorno**:
   - Crea un archivo `.env` en la carpeta `env/` con el siguiente contenido:
     ```
     PG_USER=<tu-usuario-postgres>
     PG_PASSWORD=<tu-contraseña-postgres>
     PG_HOST=<tu-host-postgres>
     PG_PORT=<tu-puerto-postgres>
     PG_DATABASE=<tu-base-de-datos-postgres>
     ```
   - Asegúrate de incluir `.env` en `.gitignore` para proteger las credenciales.
3. **Instalar Dependencias de Python**:
   - Crea y activa un entorno virtual:
     ```bash
     python -m venv venv
     source venv/bin/activate  # En Windows: venv\Scripts\activate
     ```
   - Instala las dependencias (crea `requirements.txt` si no existe):
     ```bash
     pip install pandas scikit-learn matplotlib seaborn plotly kafka-python-ng country-converter sqlalchemy psycopg2-binary python-dotenv joblib
     pip freeze > requirements.txt
     ```
4. **Iniciar Kafka y ZooKeeper**:
   - Ejecuta la configuración de Docker Compose:
     ```bash
     docker compose up --build
     ```
   - Esto inicia ZooKeeper (puerto 2181) y Kafka (puerto 9092). Verifica los servicios con `docker ps`.
5. **Ejecutar el Pipeline**:
   - Asegúrate de que la carpeta `data/` contiene los archivos CSV (2015–2019).
   - Inicia el consumidor de Kafka (en una terminal):
     ```bash
     python consumer.py
     ```
   - Inicia el productor de Kafka (en otra terminal):
     ```bash
     python producer.py
     ```
   - El productor envía datos a Kafka, y el consumidor los procesa, aplica el modelo y almacena los resultados en PostgreSQL.
6. **Verificar Almacenamiento en PostgreSQL**:
   - Conéctate a tu base de datos PostgreSQL y consulta la tabla `whr_predictions` para ver las predicciones, incluyendo `happiness_score` y `predicted_happiness_score`.

### Notas
- Asegúrate de que el archivo `model/rf_model.pkl` exista o reentrena el modelo (script de entrenamiento no incluido).
- El pipeline asume que los archivos CSV están en `data/`. Ajusta las rutas en `producer.py` si es necesario.
- Detén los servicios de Docker con `docker compose down` al finalizar.

## Resultados

- **Rendimiento del Modelo**: El modelo de Bosques Aleatorios alcanzó un R² de 0.85, explicando el 85% de la varianza en las Puntuaciones de Felicidad, con MSE y MAE bajos.
- **Insights Clave**:
  - Países con alto PIB per cápita, apoyo social y esperanza de vida (por ejemplo, Finlandia, Noruega, Canadá) lideran en felicidad.
  - África Subsahariana y Asia Meridional presentan puntuaciones más bajas, reflejando desafíos socioeconómicos.
  - `economy`, `social_support` y `health` son los predictores más fuertes.
- **Visualizaciones**: Mapas interactivos y gráficos de dispersión destacan patrones geográficos y validan la precisión del modelo.
- **Escalabilidad**: Kafka y Docker garantizan un pipeline robusto en tiempo real.

## Lecciones Aprendidas

- La normalización de datos y la imputación cuidadosa fueron esenciales para evitar sesgos.
- Visualizaciones como mapas interactivos ayudaron a interpretar patrones y validar suposiciones.
- Los Bosques Aleatorios equilibraron precisión y simplicidad frente a otros modelos.
- Docker simplificó la configuración de Kafka, pero requirió gestionar dependencias entre servicios.
- La integración con PostgreSQL optimizó el almacenamiento, pero destacó la necesidad de manejar errores robustamente.

## Contribuir

¡Las contribuciones son bienvenidas! Sigue estos pasos:
1. Haz un fork del repositorio.
2. Crea una rama para tu funcionalidad (`git checkout -b feature/TuFuncionalidad`).
3. Realiza los cambios (`git commit -m "Añadir TuFuncionalidad"`).
4. Sube la rama (`git push origin feature/TuFuncionalidad`).
5. Abre un Pull Request.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

Para preguntas o comentarios, abre un issue o contacta al mantenedor del repositorio.