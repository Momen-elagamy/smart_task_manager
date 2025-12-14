from django.test import TestCase, Client
from django.urls import reverse

class SmokeTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(email='tester@example.com', password='Aa!23456')
        self.client = Client()
        self.client.login(username='tester@example.com', password='Aa!23456')

    def test_pages_load(self):
        pages = [
            reverse('dashboard'), reverse('chat'), reverse('team'),
            reverse('settings'), reverse('profile'), reverse('api-explorer')
        ]
        for url in pages:
            resp = self.client.get(url)
            self.assertIn(resp.status_code, (200,302), f"Page {url} did not load properly")

    def test_api_endpoints(self):
        endpoints = [
            '/api/users/profile/', '/api/team/members/', '/projects/api/projects/',
            '/tasks/api/tasks/', '/dashboard/stats/', '/notifications/count/',
            '/api/search/?q=test', '/api/activity/recent/'
        ]
        for url in endpoints:
            resp = self.client.get(url)
            # Some endpoints may require auth; ensure 200 or 403 acceptable
            self.assertIn(resp.status_code, (200, 403), f"Endpoint {url} unexpected status {resp.status_code}")

    def test_create_project(self):
        payload = { 'name': 'Smoke Project', 'description': 'Created in smoke test' }
        resp = self.client.post('/projects/api/projects/', payload, content_type='application/json')
        self.assertEqual(resp.status_code, 201)

    def test_create_task(self):
        # Need a project first
        proj_resp = self.client.post('/projects/api/projects/', { 'name': 'TaskProj', 'description': '' }, content_type='application/json')
        self.assertEqual(proj_resp.status_code, 201)
        project_id = proj_resp.json()['id']
        task_payload = { 'title': 'Smoke Task', 'status': 'todo', 'project': project_id }
        resp = self.client.post('/tasks/api/tasks/', task_payload, content_type='application/json')
        self.assertEqual(resp.status_code, 201)
