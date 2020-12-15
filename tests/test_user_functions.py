import os
from unittest import TestCase
from sqlalchemy import exc
from models import User, Movie, List, ListMovie, Watchlist, Review, db, connect_db, Favorite
os.environ['DATABASE_URL'] = "postgresql:///capstone1-test"
from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserFunctionTestCase(TestCase):
    """Test model for user."""

    def setUp(self):
        db.drop_all()
        db.create_all()
        self.client = app.test_client()
        self.testuser1 = User.signup("testuser1", "testuser1@email.com", "password")
        self.testuser1id = 1
        self.testuser1.id = self.testuser1id
        db.session.commit()
        self.testuser1 = User.query.get(self.testuser1id)


    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_user_favorite(self):
        with self.client as c:
            movie = Movie(title="testmovietitle")
            db.session.add(movie)
            db.session.commit()
            favorite = Favorite(user_id=self.testuser1.id,movie_id=1)
            db.session.add(favorite)
            db.session.commit()
            resp = c.get("/user/testuser1")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("testmovietitle", str(resp.data))

    def test_user_watchlist(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1id
            movie = Movie(title="testmovietitle")
            db.session.add(movie)
            db.session.commit()
            watchlist = Watchlist(user_id=self.testuser1.id,movie_id=1)
            db.session.add(watchlist)
            db.session.commit()
            resp = c.get("/watchlist")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("testmovietitle", str(resp.data))

    def test_user_list(self):
         with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1id
            movie = Movie(title="testmovietitle")
            db.session.add(movie)
            db.session.commit()
            user_list = List(user_id=self.testuser1.id,title="testlist",description="testdescription",
                created="2020-12-14 04:26:35.664867",last_updated="2020-12-14 04:26:35.664867",total_movies=1)
            db.session.add(user_list)
            db.session.commit()
            list_movie = ListMovie(list_id=1, movie_id=1, position=1)
            resp = c.get("/list/1")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("testlist", str(resp.data))
            self.assertIn("testdescription", str(resp.data))
            self.assertIn("testuser1", str(resp.data))
            self.assertIn("Created Dec 14, 2020", str(resp.data))