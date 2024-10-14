from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests as rq
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', '8BYkEfBA6O6donzWlSihBXox7C0sKR6b')
Bootstrap5(app)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies-collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)

# Define the Movie model
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Float, nullable=False)
    review = db.Column(db.String(100), nullable=False)
    img_url = db.Column(db.String(100), nullable=False)

class MovieForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    year = StringField('Year')
    description = StringField('Description')
    rating = StringField('Rating')
    ranking = StringField('Ranking')
    review = StringField('Review')
    img_url = StringField('Image URL')
    submit = SubmitField('Submit')

# Create the database and the movies table
def create_db():
    with app.app_context():
        db.create_all()

def search_movie(title):
    url = f"https://api.themoviedb.org/3/search/movie?query={title}&include_adult=false&language=en-US&page=1"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.getenv('API_READ_ACCESS')}"
    }
    
    response = rq.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('results', [])
    return []  # Return an empty list on error

def movie_entry(action, **kwargs):
    with app.app_context():
        if action == "create":
            new_movie = Movie(**kwargs)
            db.session.add(new_movie)
            db.session.commit()
            return new_movie
        elif action == "read":
            return Movie.query.get(kwargs['id'])
        elif action == "update":
            movie = Movie.query.get(kwargs['id'])
            if movie:
                for key, value in kwargs.items():
                    setattr(movie, key, value)
                db.session.commit()
            return movie
        elif action == "delete":
            movie = Movie.query.get(kwargs['id'])
            if movie:
                db.session.delete(movie)
                db.session.commit()
            return movie

def get_new_movie_id():
    max_id = db.session.query(db.func.max(Movie.id)).scalar()
    return (max_id + 1) if max_id is not None else 1

@app.route("/")
def home():
    movies = Movie.query.all()
    return render_template("index.html", movies=movies)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    movie = movie_entry("read", id=id)
    form = MovieForm(obj=movie)

    if form.validate_on_submit():
        movie_entry("update", id=id,
                     title=form.title.data,
                     year=int(form.year.data),
                     description=form.description.data,
                     rating=float(form.rating.data),
                     ranking=float(form.ranking.data),
                     review=form.review.data,
                     img_url=form.img_url.data)
        return redirect(url_for('home'))

    return render_template("edit.html", form=form, movie=movie)

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    movie_entry(action='delete', id=id)
    return redirect(url_for('home'))

@app.route("/add", methods=["GET", "POST"])
def add():
    form = MovieForm()
    if form.validate_on_submit():
        title = form.title.data
        return redirect(url_for('select', title=title))
    return render_template("add.html", form=form)

@app.route("/select")
def select():
    title = request.args.get('title')
    movies = search_movie(title)  # Fetch results based on the title
    return render_template("select.html", movies=movies)

if __name__ == '__main__':
    create_db()  # Ensure the database and tables are created
    app.run(debug=True)
