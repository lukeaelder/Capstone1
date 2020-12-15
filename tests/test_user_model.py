import os
from unittest import TestCase
from sqlalchemy import exc
from models import User, Movie, List, ListMovie, Watchlist, Review, db, connect_db, Favorite
os.environ['DATABASE_URL'] = "postgresql:///capstone1-test"
from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserModelTestCase(TestCase):
    """Test model for user."""

    def setUp(self):
        db.drop_all()
        db.create_all()
        self.client = app.test_client()
        self.testuser1 = User.signup("testuser1", "testuser1@email.com", "password")
        self.testuser1id = 1
        self.testuser1.id = self.testuser1id
        self.testuser1 = User.signup("testuser2", "testuser2@email.com", "password")
        self.testuser1id = 2
        self.testuser1.id = self.testuser1id
        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_user_model(self):
        with self.client as c:
            testuser3 = User.signup("testuser3", "testuser3@email.com", "password")
            testuser3.id = 3
            db.session.add(testuser3)
            db.session.commit()
            self.assertEqual(testuser3.total_reviews, 0)
            self.assertEqual(testuser3.id, 3)
            self.assertNotEqual(testuser3.password, "password")

    def test_invalid_signup(self):
        with self.client as c:
            invalid = User.signup(None, "test@email.com", "password")
            with self.assertRaises(exc.IntegrityError) as context:
                db.session.commit()

    def test_short_password_error(self):
        with self.client as c:
            invalid = User.signup("testuser3", "test@email.com", "short")
            with self.assertRaises(exc.IntegrityError) as context:
                db.session.commit()

    def test_authentication(self):
        user = User.authenticate(self.testuser1.username, "password")
        self.assertEqual(user.id, self.testuser1id)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("notacorrectusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.testuser1.username, "notacorrectpassword"))