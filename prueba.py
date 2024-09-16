import pandas as pd
from pymongo import MongoClient

# Configura la conexión a MongoDB Atlas
client = MongoClient("mongodb+srv://fabricioquispe:Nm8AxHP2aoa3ykd6@movies.3ealn.mongodb.net/?retryWrites=true&w=majority&appName=movies")

# Selecciona la base de datos y las colecciones
db = client['movies']  # Nombre de la base de datos
collection_movies = db['movies']  # Nombre de la colección para películas
collection_occupations = db['occupations']  # Nombre de la colección para ocupaciones

# Leer los archivos CSV generados (users.csv y ratings.csv) y u.item (movies)
users = pd.read_csv('ml-100k/users.csv')
ratings = pd.read_csv('ml-100k/ratings.csv')

# Leer el archivo u.item para obtener los títulos de las películas
columnas_peliculas = ['movie_id', 'movie_title', 'release_date', 'video_release_date', 'IMDb_URL']
movies = pd.read_csv('ml-100k/u.item', sep='|', encoding='latin-1', usecols=range(5), names=columnas_peliculas)

# Paso 1: Calcular la cantidad de votaciones por película
votaciones_por_pelicula = ratings.groupby('movie_id').size().reset_index(name='num_votaciones')

# Ordenar por la cantidad de votaciones, en orden descendente (películas más votadas primero)
peliculas_mas_votadas = votaciones_por_pelicula.sort_values(by='num_votaciones', ascending=False)

# Paso 2: Obtener las ocupaciones de los usuarios que votaron por las películas más votadas
# Unimos el dataframe de calificaciones con el de usuarios
ratings_usuarios = pd.merge(ratings, users, on='user_id')

# Unimos el dataframe de películas con el resultado anterior
result = pd.merge(ratings_usuarios, movies[['movie_id', 'movie_title']], on='movie_id')

# Agrupamos por título de película y ocupación para contar las votaciones por ocupación
ocupaciones_por_pelicula = result.groupby(['movie_title', 'occupation']).size().reset_index(name='num_votaciones_por_ocupacion')

# Convertir los datos a tipos estándar de Python
def convert_to_standard_types(df):
    df = df.copy()
    for col in df.select_dtypes(include=['int64', 'float64']).columns:
        df[col] = df[col].astype(int)  # O puedes usar float si es necesario
    return df

# Convertir los DataFrames antes de la inserción
votaciones_por_pelicula = convert_to_standard_types(votaciones_por_pelicula)
ocupaciones_por_pelicula = convert_to_standard_types(ocupaciones_por_pelicula)

# Paso 3: Mostrar las 5 películas con más votaciones y las ocupaciones relacionadas
peliculas_top_5 = peliculas_mas_votadas.head(5)

print("Ranking de las 5 películas más votadas junto con las ocupaciones de los usuarios que votaron:")

# Preparar las películas y ocupaciones para insertar en MongoDB
movies_to_insert = []
occupations_to_insert = []

for _, row in peliculas_top_5.iterrows():
    movie_id = row['movie_id']
    movie_title = movies[movies['movie_id'] == movie_id]['movie_title'].values[0]
    
    print(f"\nPelícula: {movie_title} - Total de votaciones: {row['num_votaciones']}")
    
    # Insertar la película en MongoDB
    movies_to_insert.append({
        'movie_id': int(movie_id),
        'movie_title': movie_title,
        'num_votaciones': int(row['num_votaciones'])
    })
    
    # Filtrar ocupaciones relacionadas con esta película
    ocupaciones_pelicula = ocupaciones_por_pelicula[ocupaciones_por_pelicula['movie_title'] == movie_title]
    
    # Insertar ocupaciones en MongoDB
    for _, ocupacion_row in ocupaciones_pelicula.iterrows():
        occupations_to_insert.append({
            'movie_title': movie_title,
            'occupation': ocupacion_row['occupation'],
            'num_votaciones_por_ocupacion': int(ocupacion_row['num_votaciones_por_ocupacion'])
        })

# Insertar los datos en MongoDB Atlas
if movies_to_insert:
    collection_movies.insert_many(movies_to_insert)
if occupations_to_insert:
    collection_occupations.insert_many(occupations_to_insert)

print("Datos insertados en MongoDB Atlas.")
