# UTN FRRO Soporte TPI
# Sistema de Recomendación de Películas

Este proyecto es una aplicación web de recomendaciones de películas desarrollada en Python usando Flask, Scikit-Learn y SQLite. Permite a los usuarios registrarse, iniciar sesión y recibir recomendaciones de películas personalizadas en función de calificaciones de otros usuarios y el género, título y año de lanzamiento de cada película. Además, utiliza la API de OMDb (versión abierta de IMDb) para obtener detalles adicionales de las películas.

[Para una documentación más ampliada del proyecto consultar aquí](Documentación%20TPI%20-%20Grupo%207%20-%20Soporte%202024.pdf)


## Estructura del Proyecto

```
UTN_SOPORTE_PRUEBA_TPI/
│
├── app.py               # Archivo principal de la aplicación Flask
├── app.db          # Base de datos SQLite que almacena usuarios y recomendaciones
├── movies.csv           # Archivo CSV con la estructura de las películas en la base de datos
├── ratings.csv          # Archivo CSV con las calificaciones de usuarios a las películas
└── templates/           # Carpeta para los archivos HTML de las diferentes secciones de la app
```

## Descripción de Archivos

- **app.py**: Archivo principal de la aplicación Flask. Define las rutas y la lógica de la aplicación, que incluye el registro/inicio de sesión de usuarios, generación de recomendaciones, y visualización de películas. Implementa un modelo de recomendación de películas basado en el algoritmo de Vecinos Más Cercanos (k-Nearest Neighbors) de Scikit-Learn.

- **app.db**: Base de datos SQLite que contiene dos tablas principales:
  - `Users`: Almacena los datos de los usuarios (username y password).
  - `Recomendations`: Guarda las recomendaciones generadas para cada usuario.

- **movies.csv**: Archivo que contiene la estructura de las películas disponibles en la base de datos. Cada entrada tiene `movieId`, `imdbId`, `tmdbId`, `title`, `genre`, y `year`.

- **ratings.csv**: Archivo que almacena las calificaciones de distintos usuarios sobre las películas disponibles.

- **templates/**: Carpeta que contiene los archivos HTML de las diferentes secciones de la aplicación, como las páginas de inicio, recomendaciones y login de usuario.

## Funcionalidades

### 1. Recomendación de Películas
- La aplicación proporciona cinco películas aleatorias (de `movies.csv`) para que el usuario las califique. En base a estas calificaciones, el modelo de machine learning que hace uso del algoritmo k-Nearest Neighbors de Scikit-Learn recomienda 3 películas que probablemente sean del agrado del usuario, teniendo en cuenta las opiniones de otros usuarios, el título, género y año de lanzamiento de las películas.

### 2. Mis Recomendaciones
- Aquí se pueden visualizar todas las películas (con su título, año de lanzamiento y imagen de portada) que se le han recomendado al usuario anteriormente, para que pueda tener un rápido acceso a las sugerencias que ha realizado el modelo de machine learning y no le sea tan fácil olvidarlas.

## Tecnologías Utilizadas

- **Flask**: Para el desarrollo del servidor web.
- **SQLite**: Base de datos para almacenar información de usuarios y recomendaciones.
- **Pandas**: Para manipulación y carga de datos de los archivos CSV.
- **Scikit-Learn**: Biblioteca de aprendizaje automático utilizada para implementar el modelo de Vecinos Más Cercanos.
- **OMDb API**: Para obtener detalles adicionales de las películas.

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/federicoclementealvarez/UTN-FRRO-Soporte-TPI.git
   ```
2. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Setear una API KEY de OMDb en el env local:

   Se deberá crear un archivo .env que contenga la siguiente línea: (reemplazando "my_apy_key_here" por su API KEY de OMDb personal)
   ```
   OMDB_API_KEY=my_api_key_here
   ```
 4. Iniciar la aplicación:
   ```bash
   python app.py
   ```

## Uso

1. **Registro**: Crear una cuenta de usuario en la aplicación.
2. **Inicio de sesión**: Iniciar sesión para acceder a las recomendaciones personalizadas.
3. **Recomendar**: Calificar películas aleatorias para obtener recomendaciones.
4. **Mis recomendaciones**: Acceder a la sección "Mis Recomendaciones" para ver películas recomendadas anteriormente.

## Notas Adicionales
- La aplicación está diseñada para ejecutarse en un entorno de desarrollo. No se recomienda su uso en producción sin ajustes adicionales en seguridad y escalabilidad.

---

**Autor**: Grupo 07 - Soporte - UTN Facultad Regional Rosario  
**Año**: 2024
