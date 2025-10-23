import unittest
from app import create_app, db
from app.models import User, Record

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False
        })
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        # Create a test user
        self.user = User(username='testuser', full_name='Test User')
        self.user.set_password('password')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login_page(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn('تسجيل الدخول'.encode('utf-8'), response.data)

    def test_login_logout(self):
        # Login
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='password'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('تسجيل الخروج'.encode('utf-8'), response.data)
        # Logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('تسجيل الدخول'.encode('utf-8'), response.data)

if __name__ == '__main__':
    unittest.main()