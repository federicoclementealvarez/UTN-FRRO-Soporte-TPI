from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import pandas as pd
import sqlite3
import os
import requests
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer
import os
import secrets
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('OMDB_API_KEY')

app = Flask(__name__)

secret_key = secrets.token_hex(16)
os.environ['SECRET_KEY'] = secret_key
app.secret_key = os.environ.get('SECRET_KEY')

DB_PATH = 'app.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        imdbId TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()

init_db()


def get_user_recommendations(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT imdbId FROM recommendations WHERE user_id = ?', (user_id,))
    results = c.fetchall()
    conn.close()
    return [row[0] for row in results]

@app.route('/my-recommendations')
def my_recommendations():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    imdb_ids = get_user_recommendations(user_id)

    recommended_movies = []
    for imdb_id in imdb_ids:
        response = requests.get(f'http://www.omdbapi.com/?i={imdb_id}&apikey={API_KEY}')
        movie_data = response.json()
        if movie_data.get('Response') == 'True':
            recommended_movies.append({
                'imdbId': imdb_id,
                'title': movie_data.get('Title', ''),
                'year': movie_data.get('Year', ''),
                'poster': movie_data.get('Poster', ''),
                'plot': movie_data.get('Plot', 'No plot available')
            })

    return render_template('my_recommendations.html', movies=recommended_movies)

movies_df = pd.read_csv('movies.csv')
ratings_df = pd.read_csv('ratings.csv')

def prepare_movies_features():
    global movies_features
    movies_df['year'] = movies_df['year'].fillna(0).astype(int)
    movies_df['genres'] = movies_df['genres'].fillna('').str.split('|')
    mlb = MultiLabelBinarizer()
    genres_encoded = mlb.fit_transform(movies_df['genres'])
    movies_features = pd.DataFrame(genres_encoded, columns=mlb.classes_)
    movies_features['year'] = movies_df['year']

prepare_movies_features()

def prepare_combined_features():
    global combined_features
    movie_features_expanded = movies_features.copy()
    movie_features_expanded['movieId'] = movies_df['movieId']
    user_movie_matrix = ratings_df.pivot(index='userId', columns='movieId', values='rating').fillna(0)
    combined_features = user_movie_matrix.T.join(movie_features_expanded.set_index('movieId'), how='inner').fillna(0)
    combined_features.columns = combined_features.columns.astype(str)

prepare_combined_features()

def fetch_random_movies():
    random_movies = []
    while len(random_movies) < 5:
        random_id = np.random.choice(movies_df['imdbId'])
        response = requests.get(f'http://www.omdbapi.com/?i={random_id}&apikey={API_KEY}')
        movie_data = response.json()
        if movie_data.get('Response') == 'True':
            random_movies.append({
                'imdbId': movie_data['imdbID'],
                'title': movie_data['Title'],
                'year': movie_data['Year'],
                'poster': movie_data['Poster'],
            })
    return random_movies

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            return redirect(url_for('my_recommendations'))
        flash('Datos incorrectos o cuenta inexistente')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            flash('Username already taken')
        finally:
            conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify([])
    user_ratings = request.json
    user_input = pd.DataFrame(columns=combined_features.columns)
    for imdb_id, rating in user_ratings.items():
        movie_row = movies_df[movies_df['imdbId'] == imdb_id]
        if not movie_row.empty:
            movie_id = movie_row['movieId'].values[0]
            user_input.loc[movie_id] = combined_features.loc[movie_id] * rating
    if user_input.empty:
        return jsonify([])
    user_profile = user_input.sum(axis=0).to_frame().T
    user_profile = user_profile[combined_features.columns]
    knn_model = NearestNeighbors(n_neighbors=6, metric='cosine')
    knn_model.fit(combined_features)
    distances, indices = knn_model.kneighbors(user_profile)
    recommended_movie_ids = combined_features.index[indices.flatten()]
    user_rated_movie_ids = set(movies_df[movies_df['imdbId'].isin(user_ratings.keys())]['movieId'].values)
    unique_recommendations = [movie_id for movie_id in recommended_movie_ids if movie_id not in user_rated_movie_ids][:3]
    recommended_movies = movies_df[movies_df['movieId'].isin(unique_recommendations)][['title', 'year', 'genres']].to_dict(orient='records')
    
    recommended_movies = []
    for movie_id in unique_recommendations:
        movie_row = movies_df[movies_df['movieId'] == movie_id]
        if not movie_row.empty:
            movie = movie_row.iloc[0]
            recommended_movies.append({
                'imdbId': movie['imdbId'],
                'title': movie['title'],
                'year': movie['year'],
            })

    recommended_movies_details = []
    for movie in recommended_movies:
        response = requests.get(f'http://www.omdbapi.com/?i={movie["imdbId"]}&apikey={API_KEY}')
        movie_data = response.json()
        if movie_data.get('Response') == 'True':
            recommended_movies_details.append({
                'imdbId': movie_data['imdbID'],
                'title': movie_data['Title'],
                'year': movie_data['Year'],
                'poster': movie_data.get('Poster', ''),
                'plot': movie_data.get('Plot', 'No plot available'),
            })

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for movie_id in unique_recommendations:
        movie_row = movies_df[movies_df['movieId'] == movie_id]
        imdb_id = movie_row['imdbId'].values[0]
        c.execute('INSERT INTO recommendations (user_id, imdbId) VALUES (?, ?)', (user_id, imdb_id))
    conn.commit()
    conn.close()

    return jsonify(recommended_movies_details)

@app.route('/recommend')
def recommend():
    random_movies = fetch_random_movies()
    return render_template('recommend.html', movies=random_movies)


if __name__ == '__main__':
    app.run(debug=True)