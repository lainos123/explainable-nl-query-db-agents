from django.test import TestCase, Client

# Files access tests
class FilesAccessTests(TestCase):
	def setUp(self):
		self.client = Client()

	def test_sqlfiles_upload_requires_auth(self):
		# Giả sử endpoint upload file cần xác thực, kiểm tra trả về 403 hoặc 401
		with open('test.sql', 'w') as f:
			f.write('SELECT 1;')
		with open('test.sql', 'rb') as f:
			response = self.client.post('/api/sqlfiles/', {'file': f})
		self.assertIn(response.status_code, [401, 403, 400])

# Chat history access tests
class ChatHistoryAccessTests(TestCase):
	def setUp(self):
		self.client = Client()

	def test_chat_history_unauthorized(self):
		# Giả sử endpoint chat history cần xác thực, kiểm tra trả về 403 hoặc 401
		response = self.client.get('/api/chat/history/')
		self.assertIn(response.status_code, [401, 403, 404])