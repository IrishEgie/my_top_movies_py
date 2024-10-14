from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
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
    year = StringField('Year', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    rating = StringField('Rating', validators=[DataRequired()])
    ranking = StringField('Ranking', validators=[DataRequired()])
    review = StringField('Review', validators=[DataRequired()])
    img_url = StringField('Image URL', validators=[DataRequired()])
    submit = SubmitField('Update Movie')

# Create the database and the movies table
def create_db():
    with app.app_context():
        db.create_all()

def movie_entry(action, id=None, title=None, year=None, description=None, rating=None, ranking=None, review=None, img_url=None):
    with app.app_context():
        if action == "create":
            new_movie = Movie(
                title=title,
                year=year,
                description=description,
                rating=rating,
                ranking=ranking,
                review=review,
                img_url=img_url
            )
            db.session.add(new_movie)
            db.session.commit()
            return new_movie
        elif action == "read":
            return Movie.query.get(id)
        elif action == "update":
            movie = Movie.query.get(id)
            if movie:
                movie.title = title
                movie.year = year
                movie.description = description
                movie.rating = rating
                movie.ranking = ranking
                movie.review = review
                movie.img_url = img_url
                db.session.commit()
            return movie
        elif action == "delete":
            movie = Movie.query.get(id)
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
    movie = movie_entry("read", id)
    form = MovieForm(obj=movie)

    if form.validate_on_submit():
        movie_entry("update", id,
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
        new_id = get_new_movie_id()  # Get the new ID
        movie_entry("create", 
                    title=form.title.data,
                    year=int(form.year.data),
                    description=form.description.data,
                    rating=float(form.rating.data),
                    ranking=float(form.ranking.data),
                    review=form.review.data,
                    img_url=form.img_url.data)

        return redirect(url_for('home'))
    
    return render_template("add.html", form=form)

if __name__ == '__main__':
    create_db()  # Ensure the database and tables are created
    app.run(debug=True)
