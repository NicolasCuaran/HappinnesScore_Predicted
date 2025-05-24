HappinessScore_Predicted

Descripción General
El proyecto HappinessScore_Predicted implementa un pipeline de datos para predecir la Puntuación de Felicidad de países utilizando los datos del World Happiness Report (2015–2019). El sistema integra extracción y transformación de datos, análisis exploratorio (EDA), un modelo de Bosques Aleatorios para predicciones, streaming en tiempo real con Apache Kafka y almacenamiento en PostgreSQL. Las visualizaciones generadas ofrecen insights sobre patrones globales de felicidad y el rendimiento del modelo. Docker asegura escalabilidad y reproducibilidad.
Los objetivos principales son:

Normalizar y limpiar los datos del World Happiness Report para garantizar consistencia.
Realizar EDA para identificar relaciones entre variables.
Entrenar y serializar un modelo de Bosques Aleatorios para predecir la Puntuación de Felicidad.
Procesar datos en tiempo real mediante Kafka.
Almacenar predicciones en PostgreSQL y evaluar el modelo con métricas y visualizaciones.

La documentación detallada está disponible en Documentación.
Estructura del Repositorio
HappinessScore_Predicted/
├── data/                     # Archivos CSV del World Happiness Report (2015–2019)
├── model/                    # Modelo serializado de Bosques Aleatorios (rf_model.pkl)
├── Documents/                # Documentación del proyecto
├── env/                      # Archivo de variables de entorno (.env)
├── consumer.py               # Script consumidor de Kafka para predicción y almacenamiento
├── producer.py               # Script productor de Kafka para streaming de datos
├── docker-compose.yml        # Configuración de Docker para Kafka y ZooKeeper
└── README.md                 # Descripción general e instrucciones de configuración

Herramientas y Tecnologías
El pipeline utiliza las siguientes herramientas y librerías:

Python 3.10: Lenguaje principal para procesamiento y modelado.
Apache Kafka: Sistema de mensajería distribuida para streaming en tiempo real.
Docker: Orquestación de contenedores para Kafka y ZooKeeper.
PostgreSQL: Base de datos relacional para almacenamiento de predicciones.
Librerías de Python:
pandas: Manipulación y transformación de datos.
scikit-learn: Modelo de Bosques Aleatorios y métricas de evaluación.
matplotlib, seaborn, plotly: Visualizaciones estáticas e interactivas.
kafka-python-ng: Cliente de Kafka para operaciones de productor y consumidor.
country-converter: Estandarización de nombres de países y continentes.
sqlalchemy, psycopg2-binary: Conexión a PostgreSQL.
python-dotenv: Gestión de variables de entorno.
joblib: Serialización de modelos.



Consulta requirements.txt (generado durante la configuración) para la lista completa.
Metodología
El pipeline se organiza en cinco etapas clave:

Extracción y Transformación de Datos (producer.py):

Carga archivos CSV (2015–2019) y normaliza nombres de columnas.
Imputa valores nulos (por ejemplo, media para corruption_perception).
Asigna continentes con country-converter y mapeos personalizados.
Concatena datos en un DataFrame unificado.


Análisis Exploratorio de Datos (EDA):

Genera mapas interactivos (Plotly) para visualizar patrones geográficos de felicidad.
Crea mapas de calor de correlaciones (Seaborn) e histogramas para identificar predictores clave (economy, social_support, health).


Entrenamiento y Serialización del Modelo:

Entrena un modelo de Bosques Aleatorios con datos preprocesados (70% entrenamiento, 30% prueba).
Logra un R² de 0.85, con MSE y MAE bajos.
Serializa el modelo en rf_model.pkl para su uso en streaming.


Streaming en Tiempo Real con Kafka:

Utiliza Docker para ejecutar Kafka y ZooKeeper (docker-compose.yml).
producer.py envía datos transformados al tópico whr_kafka_topic.
consumer.py consume mensajes, aplica el modelo y genera predicciones.


Almacenamiento y Evaluación (consumer.py):

Almacena predicciones en una tabla de PostgreSQL (whr_predictions).
Evalúa el modelo con métricas (R², MSE, MAE) y visualizaciones (gráficos de dispersión, histogramas de residuales).



Instrucciones de Configuración
Prerrequisitos

Docker: Instala Docker Desktop.
Python 3.10: Descarga desde python.org.
PostgreSQL: Instala localmente o usa un servicio gestionado.
Git: Para clonar el repositorio.

Instalación

Clonar el Repositorio:
git clone https://github.com/NicolasCuaran/HappinnesScore_Predicted.git
cd HappinessScore_Predicted


Configurar Variables de Entorno:

Crea un archivo .env en la carpeta env/ con el siguiente contenido:PG_USER=<tu-usuario-postgres>
PG_PASSWORD=<tu-contraseña-postgres>
PG_HOST=<tu-host-postgres>
PG_PORT=<tu-puerto-postgres>
PG_DATABASE=<tu-base-de-datos-postgres>


Asegúrate de incluir .env en .gitignore para proteger las credenciales.


Instalar Dependencias de Python:

Crea y activa un entorno virtual:python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate


Instala las dependencias (crea requirements.txt si no existe):pip install pandas scikit-learn matplotlib seaborn plotly kafka-python-ng country-converter sqlalchemy psycopg2-binary python-dotenv joblib
pip freeze > requirements.txt




Iniciar Kafka y ZooKeeper:

Ejecuta la configuración de Docker Compose:docker compose up --build


Esto inicia ZooKeeper (puerto 2181) y Kafka (puerto 9092). Verifica los servicios con docker ps.


Ejecutar el Pipeline:

Asegúrate de que la carpeta data/ contiene los archivos CSV (2015–2019).
Inicia el consumidor de Kafka (en una terminal):python consumer.py


Inicia el productor de Kafka (en otra terminal):python producer.py


El productor envía datos a Kafka, y el consumidor los procesa, aplica el modelo y almacena los resultados en PostgreSQL.


Verificar Almacenamiento en PostgreSQL:

Conéctate a tu base de datos PostgreSQL y consulta la tabla whr_predictions para ver las predicciones, incluyendo happiness_score y predicted_happiness_score.



Notas

Asegúrate de que el archivo model/rf_model.pkl exista o reentrena el modelo (script de entrenamiento no incluido).
El pipeline asume que los archivos CSV están en data/. Ajusta las rutas en producer.py si es necesario.
Detén los servicios de Docker con docker compose down al finalizar.

Resultados
El pipeline logró los siguientes resultados:

Rendimiento del Modelo: El modelo de Bosques Aleatorios alcanzó un R² de 0.85, explicando el 85% de la varianza en las Puntuaciones de Felicidad, con MSE y MAE bajos.
Insights Clave:
Países con alto PIB per cápita, apoyo social y esperanza de vida (por ejemplo, Finlandia, Noruega, Canadá) lideran en felicidad.
África Subsahariana y Asia Meridional presentan puntuaciones más bajas, reflejando desafíos socioeconómicos.
economy, social_support y health son los predictores más fuertes, según análisis de correlación e importancia de características.


Visualizaciones:
Mapas interactivos destacan patrones geográficos de felicidad.
Gráficos de dispersión e histogramas de residuales validan la precisión del modelo.


Escalabilidad: Kafka y Docker garantizan un pipeline robusto en tiempo real, con PostgreSQL habilitando almacenamiento estructurado para análisis posteriores.

Lecciones Aprendidas

Calidad de Datos: La normalización rigurosa y la imputación cuidadosa fueron esenciales para evitar sesgos.
Visualizaciones: Mapas interactivos y mapas de calor fueron clave para interpretar patrones y validar suposiciones.
Selección de Modelo: Los Bosques Aleatorios equilibraron precisión y simplicidad, superando alternativas como Regresión Lineal y SVR.
Beneficios de Docker: Simplificó la configuración de Kafka, pero requirió gestionar dependencias entre servicios.
Integración con Base de Datos: La inferencia dinámica de tipos SQL optimizó el almacenamiento, pero destacó la necesidad de manejar errores robustamente.

Contribuir
¡Las contribuciones son bienvenidas! Sigue estos pasos:

Haz un fork del repositorio.
Crea una rama para tu funcionalidad (git checkout -b feature/TuFuncionalidad).
Realiza los cambios (git commit -m "Añadir TuFuncionalidad").
Sube la rama (git push origin feature/TuFuncionalidad).
Abre un Pull Request.

Licencia
Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.
Contacto
Para preguntas o comentarios, abre un issue o contacta al mantenedor del repositorio.
