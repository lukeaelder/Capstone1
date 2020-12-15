import os
from unittest import TestCase
from models import User, Movie, List, ListMovie, Watchlist, Review, db, connect_db, Favorite
os.environ['DATABASE_URL'] = "postgresql:///capstone1-test"
from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class MoviesViewTestCase(TestCase):
    """Test views for movies."""

    def setUp(self):
        db.drop_all()
        db.create_all()
        self.client = app.test_client()
        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_home(self):
        with self.client as c:
            resp = c.get("/")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Upcoming Movies", str(resp.data))
            self.assertIn("Movies Playing Now", str(resp.data))
            self.assertIn("Top Rated Movies", str(resp.data))

    def test_upcoming(self):
        with self.client as c:
            resp = c.get(f"/movies/upcoming")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Upcoming Movies", str(resp.data))

    def test_popular(self):
        with self.client as c:
            resp = c.get(f"/movies/popular")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Popular Movies", str(resp.data))

    def test_now_play(self):
        with self.client as c:
            resp = c.get(f"/movies/now_playing")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Movies Playing Now", str(resp.data))

    def test_top_rated(self):
        with self.client as c:
            resp = c.get(f"/movies/top_rated")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Top Rated Movies", str(resp.data))

    def test_movie_page(self):
        with self.client as c:
            resp = c.get(f"/movie/299534")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Avengers: Endgame", str(resp.data))
            self.assertIn("Cast", str(resp.data))
            self.assertIn("Recommendations", str(resp.data))
            self.assertIn("Budget", str(resp.data))
            self.assertIn("Revenue", str(resp.data))

    def test_movie_cast_page(self):
        with self.client as c:
            resp = c.get(f"/movie/299534/cast")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Cast (101)", str(resp.data))
            self.assertIn("Crew (518)", str(resp.data))