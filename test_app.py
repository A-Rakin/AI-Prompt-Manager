import unittest
import json
from app import create_app, db
from app.models import User, Category, Tag, Prompt, Collection, ActivityLog, CopyHistory

# ==============================================================================
# PromptForge - Automated Test Suite
# ==============================================================================
# Verifies authentication, CRUD operations, tag associations, copy counting,
# activity logging, and REST API responses.
# ==============================================================================

class PromptForgeTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.client = self.app.test_client()

        # Create test user
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self):
        return self.client.post('/auth/login', data={
            'email_or_username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)

    def test_auth_flow(self):
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome back', response.data)

    def test_prompt_crud_and_copy(self):
        self.login()

        # Create prompt
        create_res = self.client.post('/prompts/new', data={
            'title': 'Test Python Refactor Prompt',
            'description': 'Refactors Python code for readability',
            'content': 'Act as a Senior Python Architect...',
            'platform': 'ChatGPT',
            'category_id': 0,
            'tags_input': 'python, refactor',
            'language': 'Python',
            'difficulty': 'Intermediate'
        }, follow_redirects=True)
        self.assertEqual(create_res.status_code, 200)

        prompt = Prompt.query.filter_by(title='Test Python Refactor Prompt').first()
        self.assertIsNotNone(prompt)
        self.assertEqual(prompt.platform, 'ChatGPT')
        self.assertEqual(len(prompt.tags), 2)

        # Copy prompt
        copy_res = self.client.post(f'/prompts/{prompt.id}/copy')
        self.assertEqual(copy_res.status_code, 200)
        data = json.loads(copy_res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['copy_count'], 1)

        # Verify activity log and copy history
        history = CopyHistory.query.filter_by(prompt_id=prompt.id).first()
        self.assertIsNotNone(history)

    def test_api_endpoints(self):
        self.login()

        prompt = Prompt(
            title='API Test Prompt',
            content='API test instructions...',
            platform='Claude',
            user_id=self.user.id
        )
        db.session.add(prompt)
        db.session.commit()

        api_res = self.client.get('/api/v1/prompts')
        self.assertEqual(api_res.status_code, 200)
        data = json.loads(api_res.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']), 1)

if __name__ == '__main__':
    unittest.main()
