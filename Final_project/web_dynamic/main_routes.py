#!/usr/bin/python3
"""
Flask App that integrates with AirBnB static HTML Template
"""
from flask import render_template, url_for, flash, redirect, request, Flask, jsonify
from models import storage
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import requests
from .forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm, ReviewForm
from models.user import User
from models.place import Place
from models.city import City
from models.state import State
from models.review import Review
from flask_login import login_user, current_user, logout_user, login_required, LoginManager
import uuid
import json
from hashlib import md5
from flask_mail import Message, Mail



# flask setup
app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jacktkc1@gmail.com'
#app.config['MAIL_PASSWORD'] = that is your password
app.url_map.strict_slashes = False
mail = Mail(app)
port = 5000
host = '0.0.0.0'


@login_manager.user_loader
def load_user(user_id):
    all_users = storage.all('User').values()
    for user in all_users:
        if user.id == user_id:
            return user


# begin flask page rendering
@app.teardown_appcontext
def teardown_db(exception):
    """
    after each request, this method calls .close() (i.e. .remove()) on
    the current SQLAlchemy Session
    """
    storage.close()


@app.route('/')
@app.route('/home')
def home(the_id=None):
    """
    handles request to custom template with states, cities & amentities
    """
    if current_user.is_authenticated:
        flash('you are loged in')
    state_objs = storage.all('State').values()
    states = dict([state.name, state] for state in state_objs)
    amens = storage.all('Amenity').values()
    places = storage.all('Place').values()
    users = dict([user.id, "{} {}".format(user.first_name, user.last_name)]
                 for user in storage.all('User').values())
    return render_template('home.html',
                           title='home',
                           states=states,
                           amens=amens,
                           places=places,
                           users=users,
                           cache_id=str(uuid.uuid4()))

@app.route("/about")
def about():
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """return login page
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        all_users = storage.all('User').values()
        for user in all_users:
            if user.email == form.email.data:
                pw = md5()
                pw.update(form.password.data.encode("utf-8"))
                if pw.hexdigest() == user.password:
                    user.authenticated = True
                    login_user(user, remember=form.remember.data)
                    next_page = request.args.get('next')
                    flash('Hello {} {}!'.format(user.first_name, user.last_name))
                    return redirect(next_page) if next_page else redirect(url_for('home'))
        flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html',
                            title='Login',
                            form=form,
                            cache_id=str(uuid.uuid4()))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """return login page
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(first_name=form.first_name.data,
                        last_name=form.last_name.data,
                        email=form.email.data,
                        password=form.password.data)
        storage.new(new_user)
        storage.save()
        flash('Account created for {}!'.format(form.first_name.data), 'home')
        return redirect(url_for('login'))
    return render_template('register.html',
                            title='Register',
                            form=form,
                            cache_id=str(uuid.uuid4()))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
def account():
    return render_template('account.html',
                            title='Account',
                            user_id=current_user.id,
                            user_name=current_user.first_name + ' ' + current_user.last_name,
                            cache_id=str(uuid.uuid4()))


@app.route("/update_profile", methods=['GET', 'POST'])
def update_profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        storage.save()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
    return render_template('update_profile.html',
                        title='Account',
                        form=form,
                        user_id=current_user.id,
                        user_name=form.first_name.data + form.last_name.data,
                        cache_id=str(uuid.uuid4()))

@app.route("/location", methods=['GET', 'POST'])
@login_required
def location():
    city_name = ""
    state_name = ""
    city_id = ""
    if request.method == 'POST':
        location = request.form['text']
        if location:
            city_name = location.split(',')[0]
            state_name = location.split(',')[1]
        else:
            flash('Please add location!')
            return redirect(url_for('location'))
        cities = storage.all('City').values()
        states = storage.all('State').values()
        for state in states:
            if state.name == state_name:
                for city in state.cities:
                    if city.name == city_name:
                        city_id = city.id
                if city_id == "":
                    new_city = City(name=city_name, state_id=state.id)
                    city_id = new_city.id
                    storage.new(new_city)
                    storage.save()
        if city_id == "":
            new_state = State(name=state_name)
            new_city = City(name=city_name, state_id=new_state.id)
            city_id = new_city.id
            storage.new(new_city)
            storage.new(new_state)
            storage.save()
        if city_id != "":
            return redirect(url_for('new_post', city_id=city_id))
    return render_template('location.html', cache_id=str(uuid.uuid4()))


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if request.method == 'POST' and form.validate_on_submit():
        place = Place(city_id=request.args['city_id'],
                      user_id=current_user.id,
                      name=form.name.data,
                      description=form.description.data,
                      number_rooms=int(form.number_rooms.data),
                      number_bathrooms=int(form.number_bathrooms.data),
                      max_guest=int(form.max_guest.data),
                      price_by_night=int(form.price_by_night.data),
        )
        for ame_id in form.amenities.data:
            ame_obj = storage.get('Amenity', ame_id)
            place.amenities.append(ame_obj)
        storage.new(place)
        storage.save()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html',
                           form=form, legend='New Post',
                           method='POST',
                           cache_id=str(uuid.uuid4()))

@app.route("/delete_post/<place_id>", methods=['GET', 'POST', 'DELETE'])
@login_required
def delete_post(place_id):
    r = requests.delete("http://0.0.0.0:5001/api/v1/places/" + place_id)
    if r:
        flash('Your post has been deleted!', 'success')
    else:
        flash('You can not deleted this post!', 'fail')
    return redirect(url_for('account'))

@app.route("/review_post/<place_id>", methods=['GET', 'POST'])
@login_required
def review_post(place_id):
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(text=form.text.data,
                      place_id=place_id,
                      user_id=current_user.id,
        )
        storage.new(review)
        storage.save()
        place_obj = storage.get('Place', place_id)
        place_obj.reviews.append(review)
        place_obj.save()
        # obj = storage.get('Place', place_id)
        # flash(review.id)
        flash('Your review has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('review_post.html',
                           form=form, legend='Review Post',
                           method='POST',
                           cache_id=str(uuid.uuid4()))

@app.route("/update_post/<place_id>", methods=['GET', 'PUT', 'POST'])
@login_required
def update_post(place_id):
    form = PostForm()
    if form.validate_on_submit():
        dic = {
            'name': form.name.data,
            'description': form.description.data,
            'number_rooms': form.number_rooms.data,
            'number_bathrooms': form.number_bathrooms.data,
            'max_guest': form.max_guest.data,
            'price_by_night': form.price_by_night.data,
        }
        requests.put("http://0.0.0.0:5001/api/v1/places/" + place_id, json = dic)
        for ame_id in form.amenities.data:
            requests.post("http://0.0.0.0:5001/api/v1/places/" + place_id + "/amenities/" + ame_id)
        flash('Your post has been updated!', 'success')
        return redirect(url_for('account'))
    return render_template('create_post.html',
                            form=form,
                            title='Create',
                            place_id=place_id,
                            cache_id=str(uuid.uuid4()))

def send_reset_email(user):
    s = Serializer(app.config['SECRET_KEY'], 1800)
    token = s.dumps({'user_id': user.id}).decode('utf-8')
    msg = Message('Password Reset Request',
                    sender='jacktkc1@gmail.com',
                    recipients=[user.email])
    msg.body = """To reset your password, visit the following link:
{}

If you did not make this request then simply ignore this email and no changes will be made.
""".format(url_for('reset_token', token=token, _external=True))
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        for user in storage.all('User').values():
            if user.email == form.email.data:
                send_reset_email(user)
                flash('An email has been sent with instructions to reset your password.', 'info')
                return redirect(url_for('login'))
    return render_template('reset_request.html',
                            title='Reset Password',
                            form=form,
                            cache_id=str(uuid.uuid4()))


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    s = Serializer(app.config['SECRET_KEY'])
    try:
        user_id = s.loads(token)['user_id']
    except:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    user = storage.get('User', user_id)
    form = ResetPasswordForm()
    if form.validate_on_submit():
        pw = md5()
        pw.update(form.password.data.encode("utf-8"))
        user.password = pw.hexdigest()
        user.save()
        flash('Your password has been updated {}! You are now able to log in'.format(user.password), 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html',
                            title='Reset Password',
                            form=form,
                            cache_id=str(uuid.uuid4()))

if __name__ == "__main__":
    """
    MAIN Flask App"""
    app.run(host=host, port=port)
