import os
from unittest import TestCase
from models import User, Movie, List, ListMovie, Watchlist, Review, db, connect_db, Favorite
os.environ['DATABASE_URL'] = "postgresql:///capstone1-test"
from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        db.drop_all()
        db.create_all()
        self.client = app.test_client()
        self.testuser1 = User.signup("testuser1", "testuser1@email.com", "password")
        self.testuser1id = 1
        self.testuser1.id = self.testuser1id
        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1id
            resp = c.get("/user/testuser1")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("testuser1", str(resp.data))
            self.assertIn("Total Reviews", str(resp.data))
            self.assertIn("No bio", str(resp.data))

    def test_watchlist(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1id
            resp = c.get(f"/watchlist")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("You have no movies in your watchlist", str(resp.data))

    def test_list_form(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1id
            resp = c.get(f"/list/new")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Create List", str(resp.data))

    def test_edit_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1id
            resp = c.get(f"/user/testuser1/edit")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Edit User", str(resp.data))
            self.assertIn("testuser1@email.com", str(resp.data))

    def test_reviews_page(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1id
            resp = c.get(f"/reviews")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("You have made no reviews", str(resp.data))