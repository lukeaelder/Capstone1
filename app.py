from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from models import User, Movie, List, ListMovie, Watchlist, Review, db, connect_db, Favorite
from secrets import secret_key, api_key, api_base
from sqlalchemy.exc import IntegrityError
from forms import UserEditForm, LoginForm, ReviewForm, SignupForm, CreateList
import os, json, requests

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = (os.environ.get("DATABASE_URL", "postgres:///capstone1"))
app.config["SECRET_KEY"] = (os.environ.get("SECRET_KEY", secret_key))
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

connect_db(app)

########################### Template filters and general functions ###########################

@app.template_filter()
def numberFormat(value):
    """Add commas to budget and revenue numbers."""

    return format(int(value), ',d')

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%B'):
    """Format date time from utc to month day year."""

    return value.strftime(format)

@app.before_request
def add_user_to_g():
    """When a user signes in add them to a global variable or remove them."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def get_results_list(a):
    """Change a list of movies to an easily usable format."""

    res = json.loads(a.text)
    return res["results"]

def get_results(a):
    """Change one movie to a easily useable format."""

    res = json.loads(a.text)
    return res

def login_user(user):
    """Set session value to the logged in user's id."""

    session[CURR_USER_KEY] = user.id

def in_movies(movie):
    """Check if a movie is already in movies table, if not add it."""

    movie2 = Movie.query.filter(Movie.movie_id == movie["id"]).first()
    if movie2 == None:
        movie3 = Movie(
            movie_id=movie["id"],
            poster_image=movie["poster_path"],
            backdrop_image=movie["backdrop_path"],
            overview=movie["overview"],
            title=movie["title"],
            year=movie["release_date"]
        )
        db.session.add(movie3)
        db.session.commit()

def in_favorites(movie):
    """Check if a movie is in a users favorites."""

    is_favorite = db.session.query(Favorite).filter(Favorite.movie_id == movie["id"]).filter(Favorite.user_id == session[CURR_USER_KEY]).first()
    if is_favorite:
        return True
    return False

def in_watchlist(movie):
    """Check if a movie is in a users watchlist."""

    is_watchlist = db.session.query(Watchlist).filter(Watchlist.movie_id == movie["id"]).filter(Watchlist.user_id == session[CURR_USER_KEY]).first()
    if is_watchlist:
        return True
    return False

def is_movie(movie):
    """Check if a requested movie is actually a movie."""

    if movie["success"] == False:
        return False
    return True



######################################## Movie routes ##########################################



@app.route("/")
def homepage():
    """Show home page with a couple categories of movies."""

    upcoming = get_results_list(requests.get(f"{api_base}movie/upcoming{api_key}"))
    playing = get_results_list(requests.get(f"{api_base}movie/now_playing{api_key}"))
    toprated = get_results_list(requests.get(f"{api_base}movie/top_rated{api_key}"))

    return render_template("home.html", upcoming = upcoming, playing = playing, toprated = toprated)

@app.route("/movie/<movie_id>")
def view_movie(movie_id):
    """View one movie including pictures, cast, recommendation, and more information if able to retrieve data."""

    movie = get_results(requests.get(f"{api_base}movie/{movie_id}{api_key}"))
    if is_movie(movie) == False:
        flash("We couldn't fint that movie.")
        return redirect("/")
    trailer = get_results(requests.get(f"{api_base}movie/{movie_id}/videos{api_key}"))
    try:
        certifications = get_results_list(requests.get(f"{api_base}movie/{movie_id}/release_dates{api_key}"))
        us_certification = [entry for entry in certifications if entry["iso_3166_1"] in ("US")]
        if us_certification:
            certification = [entry for entry in us_certification[0]["release_dates"] if entry["certification"]][0]["certification"]
        else:
            certification = None
    except:
        certification = None
    movie_credits = get_results(requests.get(f"{api_base}movie/{movie_id}/credits{api_key}"))
    recommendations = get_results(requests.get(f"{api_base}movie/{movie_id}/recommendations{api_key}"))
    reviews = db.session.query(Review).filter(Review.movie_id == movie_id).all()

    if g.user:
        is_favorite = in_favorites(movie)
        is_watchlist = in_watchlist(movie)
    else:
        is_favorite = False
        is_watchlist = False

    return render_template("movies/movie.html", movie = movie, trailer = trailer, 
    certification = certification, credits = movie_credits, 
    recommendations = recommendations, favorite = is_favorite, watchlist = is_watchlist,
    reviews = reviews)

@app.route("/movie/<movie_id>/cast")
def show_movie_cast(movie_id):
    """Show all cast and crew for a movie."""

    movie = get_results(requests.get(f"{api_base}movie/{movie_id}{api_key}"))
    if is_movie(movie) == False:
        flash("We couldn't fint that movie.")
        return redirect("/")
    movie_credits = get_results(requests.get(f"{api_base}movie/{movie_id}/credits{api_key}"))

    return render_template("movies/cast.html", movie = movie, credits = movie_credits)

@app.route("/movies/<section>")
def show_upcoming_movies(section):
    """Show all movies for a certain category. Upcoming, now playing, popular, and top rated."""

    movies = get_results_list(requests.get(f"{api_base}movie/{section}{api_key}"))
    if is_movie(movie) == False:
        flash("We couldn't find that cetegory.")
        return redirect("/")

    return render_template("movies/section.html", movies = movies, section = section)

@app.route("/search", methods=["GET", "POST"])
def search_movie():
    """Show results for a users search for movies by the title."""

    query = request.form.get("search")
    if query == "":
        flash("Please enter something to search for.")
        return redirect("/")

    movies = get_results_list(requests.get(f"{api_base}search/movie{api_key}&query={query}"))

    return render_template("movies/section.html", movies = movies, section = query)

@app.route("/movie/<movie_id>/review", methods=["GET", "POST"])
def create_movie_review(movie_id):
    """Show a form for a user to create a review for a movie, and add the review to reviews table."""

    if not g.user:
            flash("You must be signed in to leave a review")
            return redirect("/")

    movie = get_results(requests.get(f"{api_base}movie/{movie_id}{api_key}"))
    if is_movie(movie) == False:
        flash("We couldn't find that movie.")
        return redirect("/")
    in_movies(movie)
    form = ReviewForm()


    if form.validate_on_submit():
        review = Review(
            title=form.title.data,
            body=form.body.data,
            rating=form.rating.data,
            username = g.user.username,
            movie_id=movie_id
        )
        db.session.add(review)
        db.session.commit()
        return redirect(f"/movie/{movie_id}")
    return render_template("movies/review.html", movie = movie, form = form)



################################ Movie favorite/watchlist routes ################################



@app.route("/movie/<movie_id>/favorite")
def add_favorite(movie_id):
    """Add a movie to a users favorites."""

    if not g.user:
        flash("Access unauthorized.")
        return redirect("/")
    movie = get_results(requests.get(f"{api_base}movie/{movie_id}{api_key}"))
    if is_movie(movie) == False:
        flash("We couldn't find that movie.")
        return redirect("/")
    in_movies(movie)
    favorite = Favorite(
        user_id=session[CURR_USER_KEY],
        movie_id=movie["id"]
    )
    db.session.add(favorite)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash("Movie already added to your favorites")
    return redirect(f"/movie/{movie_id}")

@app.route("/movie/<movie_id>/favorite/remove")
def remove_favorite(movie_id):
    """Remove a movie from a users favorites."""

    if not g.user:
        flash("Access unauthorized.")
        return redirect("/")
    favorite = db.session.query(Favorite).filter(Favorite.user_id == session[CURR_USER_KEY]).filter(Favorite.movie_id == movie_id).first()
    if not favorite:
        flash("Unable to delete from your favorites")
        return redirect(request.referrer)
    db.session.delete(favorite)
    db.session.commit()

    return redirect(f"/movie/{movie_id}")

@app.route("/movie/<movie_id>/watchlist")
def add_watchlist(movie_id):
    """Add a movie to a users watchlist."""

    if not g.user:
        flash("Access unauthorized.")
        return redirect("/")
    movie = get_results(requests.get(f"{api_base}movie/{movie_id}{api_key}"))
    if is_movie(movie) == False:
        flash("We couldn't find that movie.")
        return redirect("/")
    in_movies(movie)
    watchlist = Watchlist(
        user_id=session[CURR_USER_KEY],
        movie_id=movie["id"]
    )
    db.session.add(watchlist)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash("Movie already added to your watchlist")
    return redirect(f"/movie/{movie_id}")

@app.route("/movie/<movie_id>/watchlist/remove")
def remove_watchlist(movie_id):
    """Remove a movie from a users watchlist."""

    if not g.user:
        flash("Access unauthorized.")
        return redirect("/")
    watchlist = db.session.query(Watchlist).filter(Watchlist.user_id == session[CURR_USER_KEY]).filter(Watchlist.movie_id == movie_id).first()
    if not watchlist:
        flash("Unable to delete from your watchlist")
        return redirect(request.referrer)
    
    db.session.delete(watchlist)
    db.session.commit()

    return redirect(f"/movie/{movie_id}")




####################################### User view routes ########################################



@app.route("/user/<username>")
def show_user(username):
    """Show information on a user."""

    user_name = username

    user = User.query.filter(User.username == user_name).first()

    if user == None:
        flash(f"User {username} not found")
        return redirect("/")

    lists = db.session.query(List).filter(List.user_id == user.id).all()
    reviews = db.session.query(Review).filter(Review.username == username).count()
    favorites = db.session.query(Movie).join(Favorite).filter(Movie.movie_id == Favorite.movie_id).filter(Favorite.user_id == user.id).all()

    return render_template("user/user.html", user = user, lists = lists, favorites = favorites, reviews = reviews)

@app.route("/signup", methods=["GET", "POST"])
def register():
    """Show form to signup a user and add them to the users table."""

    if g.user:
        flash("You're already logged in")
        return redirect("/")
    form = SignupForm()
    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data
            )
            db.session.commit()
        except IntegrityError as e:
            flash("Username already taken")
            return render_template('user/signup.html', form=form)
        login_user(user)
        return redirect("/")
    else:
        return render_template('user/signup.html', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login a user and add them to the session and a global variable."""

    if g.user:
        flash("You're already logged in")
        return redirect("/")
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            login_user(user)
            return redirect("/")
        flash("Invalid credentials.")
    return render_template('user/login.html', form=form)

@app.route('/logout')
def logout():
    """Logout a logged in user."""

    if not g.user:
        flash("Access unauthorized.")
        return redirect("/")
    session.pop(CURR_USER_KEY)
    return redirect("/")

@app.route("/user/<username>/edit", methods=["GET", "POST"])
def edit_user(username):
    """Show form to edit a users email, bio, profile image and perform update."""

    if not g.user or g.user.username != username:
        flash("Access unauthorized.")
        return redirect("/")

    user = User.query.filter(User.username == username).first()

    form = UserEditForm()

    if form.validate_on_submit():
        user.email = form.email.data if form.email.data else user.email
        user.bio = form.bio.data if form.bio.data else user.bio
        user.image_url = form.image_url.data if form.image_url.data else user.image_url
        try:
            db.session.commit()
        except:
            flash("Email already in use")
        return redirect(f"/user/{username}")

    form.email.data = user.email
    form.bio.data = user.bio
    form.image_url.data = user.image_url

    return render_template("user/edituser.html", form = form)

@app.route("/watchlist")
def show_watchlist():
    """Show a users watchlist."""

    if not g.user:
        flash("You must be signed in.")
        return redirect("/")
    watchlist = db.session.query(Movie).join(Watchlist).filter(Movie.movie_id == Watchlist.movie_id).filter(Watchlist.user_id == session[CURR_USER_KEY]).all()
    
    return render_template("user/watchlist.html", watchlist = watchlist)

@app.route("/reviews")
def show_reviews():
    """Show a users reviews."""

    if not g.user:
        flash("You must be signed in.")
        return redirect("/")
    reviews = db.session.query(Review).filter(Review.username == g.user.username).all()
    
    return render_template("user/reviews.html", reviews = reviews)

@app.route("/reviews/<review_id>/delete")
def delete_review(review_id):
    """Delete a review that a user made."""

    review = db.session.query(Review).filter(Review.id == review_id).first()
    if review.username != g.user.username or not g.user or review == None:
        flash("Access unauthorized.")
        return redirect("/")
    db.session.delete(review)
    db.session.commit()
    return redirect("/")
    

@app.route("/list/new", methods=["GET", "POST"])
def create_list_form():
    """Show form for a user to create a new list."""

    if not g.user:
        flash("You must be signed in.")
        return redirect("/")

    form = CreateList()

    return render_template("lists/createlist.html", form = form)

@app.route("/lists")
def show_all_list():
    """Show all created list."""

    lists = db.session.query(List).all()

    if lists == None:
        flash("Currently there are no lists.")
        return redirect("/")

    return render_template("lists/lists.html", lists = lists)


@app.route("/list/<list_id>")
def show_list(list_id):
    """Show one list."""

    lists = db.session.query(List).filter(List.id == list_id).first()
    if lists == None:
        flash("Unable to find that list.")
        return redirect("/")
    movies = db.session.query(Movie).join(ListMovie).filter(ListMovie.list_id == list_id).filter(Movie.movie_id == ListMovie.movie_id).order_by(ListMovie.position).all()
    user = db.session.query(User.username).join(List).filter(User.id == List.user_id).first()

    return render_template("lists/list.html", movies = movies, list = lists, user = user)



##################################### Axios request routes #######################################



@app.route("/list/movies", methods=["POST"])
def movie_list_search():

    query = request.json.get("query")

    movies = get_results_list(requests.get(f"{api_base}search/movie{api_key}&query={query}"))

    return jsonify(movies)

@app.route("/movie/section/more", methods=["POST"])
def more_section_results():
    """Load more movies for a certain section. Now playing, popular, upcoming, and top rated."""

    section = request.json.get("section")
    page = request.json.get("page")

    movies = get_results_list(requests.get(f"{api_base}movie/{section}{api_key}&page={page}"))
    
    return jsonify(movies)

@app.route("/checkmovie", methods=["POST"])
def check_movie():
    """Check if a movie is in the movies table as they get added to list."""

    movie_id = request.json.get("movie_id")

    movie = get_results(requests.get(f"{api_base}movie/{movie_id}{api_key}"))
    in_movies(movie)

    return jsonify(movie)

@app.route("/createlist", methods=["POST"])
def create_list():
    """Perform creation of a list by a user."""

    movies = request.json.get("list")
    title = request.json.get("title")
    description = request.json.get("description")
    top_movie = db.session.query(Movie).filter(Movie.movie_id == movies[0]["movie_id"]).first()
    image = top_movie.backdrop_image
    newlist = List(
            user_id=session[CURR_USER_KEY],
            title=title,
            description=description,
            total_movies=len(movies),
            image=image
            )
    db.session.add(newlist)
    db.session.commit()
    for movie in movies:
        list_movie = ListMovie(
            list_id=newlist.id,
            movie_id=movie["movie_id"],
            position=movie["movie_position"]
        )
        db.session.add(list_movie)
    db.session.commit()
    return("created")

@app.route("/goto/myself")
def redirect_to_self():
    """Redirect user to their own user page."""

    if not g.user:
        flash("You must be signed in.")
        return redirect("/")
    return redirect(f"/user/{g.user.username}")



################################### Error handling routes #################################



@app.errorhandler(404)
def page_not_found(e):
    """Show 404 error page."""
    
    return render_template("404.html")