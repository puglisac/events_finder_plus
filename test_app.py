

from unittest import TestCase
from flask_login import login_user
from models import db, connect_db, User, Event, UsersEvents
from flask import jsonify


from app import app
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///events_plus_test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = "some_secret_key"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class RoutesTest(TestCase):

    def setUp(self):
        """Create test client, add sample data."""
        UsersEvents.query.delete()
        Event.query.delete()
        User.query.delete()

        self.testuser = User.register(
            email="test@test.com",
            pwd="testuser",
            first="test",
            last="user",
            loc="anywhere")
        db.session.add(self.testuser)
        db.session.commit()
        self.user_id = self.testuser.id

    def test_home_page(self):
        with app.test_client() as client:

            resp = client.get('/')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("To get started finding", html)

    def test_quick_search(self):
        with app.test_client() as client:

            resp = client.get('/search_results?keyword=Nashville')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Nashville", html)

    def test_login(self):
        with app.test_client() as client:

            resp = client.post(
                '/users/login', data={'email': 'test@test.com', 'password': 'testuser'}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("test@test.com", html)
            self.assertIn("user", html)

    def test_invalid_email(self):
        with app.test_client() as client:

            resp = client.post(
                '/users/login', data={'email': 'tester@test.com', 'password': 'testuser'}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                "There is no account associated with tester@test.com", html)

    def test_invalid_password(self):
        with app.test_client() as client:

            resp = client.post(
                '/users/login', data={'email': 'test@test.com', 'password': 'nottestuser'}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Incorrect email or password", html)

    def test_signup(self):
        with app.test_client() as client:

            resp = client.post(
                '/users/signup', data={'email': 'tester@test.com', 'password': 'newpassword', 'first_name': 'new', 'last_name': 'user', 'location': 'another_loc'}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("tester@test.com", html)

    def test_duplicate_email(self):
        with app.test_client() as client:

            resp = client.post(
                '/users/signup', data={'email': 'test@test.com', 'password': 'newpassword', 'first_name': 'new', 'last_name': 'user', 'location': 'another_loc'}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                "There is already an account associated with test@test.com", html)

    def test_user_edit(self):
        with app.test_client() as client:
            client.post('/users/login', data={'email': 'test@test.com',
                                              'password': 'testuser'}, follow_redirects=True)
            resp = client.post(
                '/users/edit_profile', data={'email': 'testing@test.com', 'password': 'testuser', 'first_name': 'new', 'last_name': 'name', 'location': 'another_loc'}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("testing@test.com", html)
            self.assertIn("new name", html)

    def test_user_edit_invalid_password(self):
        with app.test_client() as client:
            client.post('/users/login', data={'email': 'test@test.com',
                                              'password': 'testuser'}, follow_redirects=True)
            resp = client.post(
                '/users/edit_profile', data={'email': 'testing@test.com', 'password': 'password', 'first_name': 'new', 'last_name': 'name', 'location': 'another_loc'}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("test@test.com", html)
            self.assertIn("Invalid Password", html)

    def test_delete_user(self):
        with app.test_client() as client:
            client.post('/users/login', data={'email': 'test@test.com',
                                              'password': 'testuser'}, follow_redirects=True)
            resp = client.post(
                '/users/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            user = User.query.get(self.testuser.id)
            self.assertEqual(user, None)

    def test_add_favorite(self):
        with app.test_client() as client:
            client.post('/users/login', data={'email': 'test@test.com',
                                              'password': 'testuser'}, follow_redirects=True)
            resp = client.post('/users/add_event',
                               json={'id': 'event_id'}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            user = User.query.get(self.testuser.id)
            self.assertEqual(user.events[0].id, 'event_id')

    def test_remove_favorite(self):
        with app.test_client() as client:
            client.post('/users/login', data={'email': 'test@test.com',
                                              'password': 'testuser'}, follow_redirects=True)
            client.post('/users/add_event',
                        json={'id': 'event_id'}, follow_redirects=True)
            resp = client.post('/users/remove_event',
                               json={'id': 'event_id'}, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            user = User.query.get(self.testuser.id)
            self.assertNotIn('event_id', user.events)
