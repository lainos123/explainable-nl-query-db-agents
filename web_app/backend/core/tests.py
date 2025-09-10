from django.test import TestCase, Client

# Files access tests
class FileAccessTests(TestCase):
	def setUp(self):
		self.client = Client()

	def test_sqlfiles_upload_requires_auth(self): 
		with open('test.sql', 'w') as f:
			f.write('SELECT 1;')
		with open('test.sql', 'rb') as f:
			response = self.client.post('/api/file/', {'file': f})
		self.assertIn(response.status_code, [401, 403, 400])

# Chat access tests
class ChatAccessTests(TestCase):
	def setUp(self):
		self.client = Client()

	def test_chat_unauthorized(self):
		response = self.client.get('/api/chat/')
		self.assertIn(response.status_code, [401, 403, 404])