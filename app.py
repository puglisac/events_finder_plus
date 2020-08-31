import os
from flask import Flask, request, render_template, redirect, flash, session, url_for, session
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Event
from secrets import event_key, event_url, google_key
import math
import requests
from werkzeug.exceptions import BadRequestKeyError
from forms import AdvancedSearchForm, LogInForm, SignUpForm, EditUserForm, NewPasswordForm, FilterCategoryForm
from methods import get_search_params, get_date_time, image_error, get_saved, sort_events_by_date, get_saved_events, start_indx

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgres:///events_plus')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'shh')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)


connect_db(app)

login = LoginManager(app)
login.login_view = "home_page"


@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def home_page():
    """shows the homepage"""

    return render_template("home.html")

################search routes####################


@app.route("/search_results")
def keyword_search_results():
    """shows quick search results"""
    try:
        """save keyword to session"""
        session['keyword'] = request.args['keyword']
        keyword = session['keyword']
    except BadRequestKeyError:
        keyword = session['keyword']

    try:
        """saves current page to session"""
        session['curr_page'] = int(request.args['page'])

    except BadRequestKeyError:
        session['curr_page'] = 1
    page = session['curr_page']
    data = {"app_key": event_key, "keywords": keyword,
            "page_number": page, "page_size": 12}
# make request to api
    r = requests.post(f"{event_url}events/search", data=data)
    size = int(r.json()['page_count'])
    if page > size:
        page = size
    if page < 1:
        page = 1
    pages = range(page-5, page+5)
    try:
        """get events from response"""
        events = r.json()['events']['event']
        results = r.json()['total_items']
    except TypeError:
        """handles no results"""
        flash("Your search did not return any results", "danger")
        return redirect(url_for('advanced_search'))
    if current_user.is_active:
        saved = get_saved(current_user.id)
    else:
        saved = None
    return render_template("search_results.html", key=keyword, pages=pages, events=events, size=size, results=results, saved=saved, time=get_date_time)


@app.route("/advanced_search", methods={"GET", "POST"})
def advanced_search():
    """advanced search form"""
    form = AdvancedSearchForm()
    if form.validate_on_submit():
        keyword = form.keyword.data
        loc = form.location.data
        cat = form.category.data
        start = form.start_date.data
        end = form.end_date.data
        session['keyword'] = keyword
        data = {"keywords": keyword, "location": loc,
                "category": cat, "page_size": 12, "date": f"{start}-{end}"}
        # save search parameters to session
        session['data'] = data
        return redirect(url_for('advanced_search_results'))
    else:
        return render_template("advanced_search.html", form=form)


@app.route("/advanced_search_results")
def advanced_search_results():
    """gets search parameters from session"""
    data = session['data']
    data['app_key'] = event_key

    try:
        """sets current page in session"""
        session['curr_page'] = int(request.args['page'])

    except BadRequestKeyError:
        session['curr_page'] = 1
    page = session['curr_page']
    data['page_number'] = page
# make call to api
    r = requests.post(f"{event_url}events/search", data=data)
    size = int(r.json()['page_count'])
    if page > size:
        page = size
    if page < 1:
        page = 1
    pages = range(page-5, page+5)
    try:
        """get events from response"""
        events = r.json()['events']['event']
        results = r.json()['total_items']
    except TypeError:
        """handles no search results"""
        flash("Your search did not return any results", "danger")
        return redirect(url_for("advanced_search"))
        """get a list of search parameters to put back into html"""
    search_params = get_search_params(data)
    if current_user.is_active:
        saved = get_saved(current_user.id)
    else:
        saved = None
    return render_template("advanced_results.html", pages=pages, events=events, size=size, saved=saved, data=search_params, results=results, time=get_date_time)


@app.route("/events/<evt_id>")
def event_details(evt_id):
    """show event details"""
    e = requests.post(f"{event_url}events/get",
                      data={"app_key": event_key, "id": evt_id})
    v = requests.post(f"{event_url}venues/get",
                      data={"app_key": event_key, "id": e.json()["venue_id"]})
    date_time = get_date_time(e.json()["start_time"])
    if current_user.is_active:
        saved = get_saved(current_user.id)
    else:
        saved = None
    return render_template("event_details.html", event=e.json(), date_time=date_time, venue=v.json(), func=image_error, saved=saved, key=google_key)
####################user routes#########################


@app.route('/users/login', methods={"POST"})
def login():
    """handles user login"""
    form = LogInForm(obj=request.json, csrf_enabled=False)
    if form.validate():
        if not User.query.filter_by(email=request.form['email']).first():
            flash(
                f"There is no account associated with {request.form['email']}", "danger")
            return redirect(url_for("signup"))
        u = User.authenticate(request.form['email'], request.form['password'])
        if u:
            """login a user and redirect to dashboard"""
            login_user(u)
            return redirect(f"/users/{u.id}")
        else:
            """handles incorrect credentials"""
            flash("Incorrect email or password", "danger")
            return redirect(url_for('home_page'))
    else:
        """handles form errors"""
        flash(form.errors, "danger")
        return redirect(url_for('home_page'))


@app.route('/users/signup', methods={"GET", "POST"})
def signup():
    """handles user sign-up"""
    form = SignUpForm()
    if form.validate_on_submit():
        """creates a new user"""
        email = form.email.data
        password = form.password.data
        first = form.first_name.data
        last = form.last_name.data
        location = form.location.data
        u = User.register(email, password, first, last, location)
        db.session.add(u)
        try:
            db.session.commit()
            login_user(u)
            return redirect(f"/users/{u.id}")
        except IntegrityError:
            """handles create new user errors"""
            flash(
                f"There is already an account associated with {form.email.data}", 'danger')
            return redirect(url_for('signup'))
    else:
        """shows user sign-up page"""
        return render_template('signup.html', form=form)


@app.route("/users/logout", methods={"POST"})
def logout():
    """logs out user"""
    logout_user()
    return redirect(url_for("home_page"))


@app.route('/users/edit_profile', methods=["GET", "POST"])
@login_required
def edit():
    """Update profile for current user."""
    user = User.query.get_or_404(current_user.id)
    form = EditUserForm(obj=user)

    if form.validate_on_submit():
        """handles password submission"""
        password = User.authenticate(user.email,
                                     form.password.data)
        if password:
            """updates the user profile"""
            user.email = form.email.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.location = form.location.data
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash(
                    f"There is already an account associated with {form.email.data}", 'danger')
                return redirect(url_for("edit"))
            flash("Updated Profile", "success")
            return redirect(f"/users/{user.id}")
        else:
            """shows for invalid password"""
            flash("Invalid Password", "danger")
            return redirect(url_for("edit"))
    else:
        return render_template("edit_user.html", user=user, form=form)


@app.route('/users/change_password', methods=["GET", "POST"])
@login_required
def change_password():
    """Update password for current user."""

    user = User.query.get_or_404(current_user.id)
    form = NewPasswordForm()

    if form.validate_on_submit():
        """handles password submission"""
        password = User.authenticate(user.email,
                                     form.cur_password.data)
        if password:
            if form.new_password.data != form.conf_password.data:
                flash("Passwords do not match", "danger")
                return render_template("change_password.html", form=form)
            if form.new_password.data == form.cur_password.data:
                flash(
                    "New password cannot be the same as your current password", "danger")
                return render_template("change_password.html", form=form)
            """changes the password"""
            User.change_password(user.email, form.new_password.data)
            db.session.commit()
            flash("Password Changed", "success")
            return redirect(f"/users/{user.id}")
        else:
            """shows for invalid password"""
            flash("Invalid Password", "danger")
            return redirect("/change_password")
    else:
        return render_template("change_password.html", user=user, form=form)


@app.route("/users/delete", methods=["POST"])
@login_required
def delete_user():
    """delete a user account"""
    u = User.query.get(current_user.id)
    db.session.delete(u)
    db.session.commit()
    logout_user()
    return redirect(url_for("home_page"))


@app.route("/users/add_event", methods=["POST"])
@login_required
def add_event():
    """add an event to a user's saved events"""
    u = User.query.get_or_404(current_user.id)
    id = request.json['id']
    new_event = Event(id=id)
    db.session.add(new_event)
    try:
        db.session.commit()
        u.events.append(new_event)
        db.session.commit()
        return "Event added"
    except:
        db.session.rollback()
        event = Event.query.get(id)
        u.events.append(event)
        db.session.commit()
        return "Event added"


@app.route("/users/remove_event", methods=["POST"])
@login_required
def remove_event():
    """remove an event from a user's saved events"""
    u = User.query.get_or_404(current_user.id)
    id = request.json['id']
    event = Event.query.get(id)
    u.events.remove(event)
    db.session.commit()
    if not event.users:
        db.session.delete(event)
        db.session.commit()
    return "Event removed"


@app.route("/users/<int:u_id>")
@login_required
def dashboard(u_id):
    if current_user.id != u_id:
        flash("You do not have permission to see this page", "danger")
        return redirect(f"/users/{current_user.id}")
    try:
        form = FilterCategoryForm(category=request.args['category'])
    except BadRequestKeyError:
        form = FilterCategoryForm()

    u = User.query.get_or_404(u_id)
    events = get_saved_events(u.id)
    try:
        category = request.args['category']
    except BadRequestKeyError:
        category = None
    r = requests.post(f"{event_url}events/search", data={"app_key": event_key,
                                                         "location": u.location, "page_size": 6, "date": "Future", "category": category})
    try:
        """get events from response"""
        local_events = r.json()['events']['event']
    except TypeError:
        """handles no search results"""
        local_events = None
    return render_template("dashboard.html", u=u, events=events[:3], local_events=local_events, time=get_date_time, saved=get_saved(current_user.id), form=form)


@app.route("/users/<int:u_id>/saved")
@login_required
def all_saved(u_id):
    """shows all user-saved events"""
    if current_user.id != u_id:
        flash("You do not have permission to see this page", "danger")
        return redirect(f"/users/{current_user.id}")
    u = User.query.get_or_404(u_id)
    events = get_saved_events(u.id)
    size = math.ceil(len(events)/12)
    try:
        """saves current page to session"""
        session['curr_page'] = int(request.args['page'])

    except BadRequestKeyError:
        session['curr_page'] = 1
    page = session['curr_page']
    if page > size:
        page = size
    if page < 1:
        page = 1
    pages = range(session['curr_page']-5, session['curr_page']+5)
    start=start_indx(page)
    page_event=events[start:start+12]
    return render_template("saved.html", u=u, events=page_event, time=get_date_time, saved=get_saved(current_user.id), pages=pages, size=size)
