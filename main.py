
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from typing import Callable

API_KEY = "9e4896490bba24e27cb03f45ebb97e69"
SEARCH_URL = "https://api.themoviedb.org/3/search/movie"


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

##CREATE DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class MySQLAlchemy(SQLAlchemy):
    Column: Callable
    String: Callable
    Integer: Callable
    Float: Callable


db = MySQLAlchemy(app)


##CREATE TABLE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)
db.create_all()



class EditForm(FlaskForm):
    rating = StringField(label='Your Rating Out of 10 e.g. 7.6',validators=[DataRequired()])
    review = StringField(label='Your Review', validators=[DataRequired()])
    submit = SubmitField(label='Done')


class AddForm(FlaskForm):
    movie = StringField(label='Movie Title',validators=[DataRequired()])
    button = SubmitField(label="Add Movie")

## After adding the new_movie the code needs to be commented out/deleted.
## So you are not trying to add the same movie twice.
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# db.session.add(new_movie)
# db.session.commit()


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating.asc())
    movies = Movie.query.all()
    total = len(movies)
    for movie in all_movies:
        movie_to_select = Movie.query.get(movie.id)
        movie_to_select.ranking = total
        db.session.commit()
        total -=1

    return render_template("index.html", movies=all_movies)

@app.route("/edit",methods=["GET","POST"])
def edit():
    my_form = EditForm()
    id = request.args.get('id')
    movie = Movie.query.get(id)

    if my_form.validate_on_submit():
        movie.rating = float(my_form.rating.data)
        movie.review = my_form.review.data
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit.html',form=my_form,movie=movie)


@app.route('/delete')
def delete():
    id = request.args.get('id')
    movie = Movie.query.get(id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/app',methods=["Get","POST"])
def add():
    form = AddForm()
    if form.validate_on_submit():
        query = form.movie.data
        params = {
            'api_key': API_KEY,
            'query': query
        }
        connection = requests.get(SEARCH_URL,params=params)
        connection.raise_for_status()
        data = connection.json()['results']
        return render_template('select.html',data=data)

    return render_template('add.html',form=form)


@app.route('/fetch',methods=["GET","POST"])
def fetch():
   movie_id = request.args.get('id')
   if movie_id:

       ID_URL = f"https://api.themoviedb.org/3/movie/{movie_id}"
       param = {
           'api_key': API_KEY,
       }

       connection = requests.get(ID_URL, params=param)
       connection.raise_for_status()
       data = connection.json()
       title = str(data['original_title'])
       overview = str(data['overview'])
       movie_release = int(request.args.get('release'))
       img_url = "https://www.themoviedb.org/t/p/original" + data['backdrop_path']

       new_movie = Movie(
           title=title,
           year=movie_release,
           description=overview,
           img_url=img_url
       )
       db.session.add(new_movie)
       db.session.commit()

       movie_to_edit = Movie.query.filter_by(title=title).first()

       return redirect(url_for('edit', id=movie_to_edit.id))

   else:

       return redirect(url_for('home'))



if __name__ == '__main__':
    app.run(debug=True)


