from django.test import TestCase, Client

from django.contrib.auth import get_user_model
from .models import File, Session, Chat, APIKey
from django.core.files.uploadedfile import SimpleUploadedFile

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


# Model tests
import os
from django.conf import settings

class ModelTests(TestCase):
	def setUp(self):
		self.User = get_user_model()
		self.user = self.User.objects.create_user(username='testuser', password='testpass')
		self._created_files = []

	def tearDown(self):
		# Clean up any files created during tests
		for file_path in self._created_files:
			if os.path.exists(file_path):
				os.remove(file_path)
				# Remove parent folder if empty (e.g., user_1/)
				parent_dir = os.path.dirname(file_path)
				try:
					if os.path.isdir(parent_dir) and not os.listdir(parent_dir):
						os.rmdir(parent_dir)
				except Exception:
					pass
		super().tearDown()

	def test_file_model(self):
		test_file = SimpleUploadedFile('test.txt', b'file_content')
		file_obj = File.objects.create(user=self.user, file=test_file)
		self.assertEqual(file_obj.user, self.user)
		self.assertTrue(file_obj.file.name.endswith('test.txt'))
		# Track file for cleanup
		abs_path = os.path.join(settings.MEDIA_ROOT, file_obj.file.name)
		self._created_files.append(abs_path)

	def test_session_model(self):
		session = Session.objects.create(user=self.user, title='Test Session')
		self.assertEqual(session.user, self.user)
		self.assertEqual(session.title, 'Test Session')

	def test_chat_model(self):
		session = Session.objects.create(user=self.user, title='Test Session')
		chat = Chat.objects.create(
			session=session,
			user=self.user,
			agent='a',
			type='sql',
			prompt='SELECT 1;',
			response='1',
		)
		self.assertEqual(chat.session, session)
		self.assertEqual(chat.user, self.user)
		self.assertEqual(chat.agent, 'a')
		self.assertEqual(chat.type, 'sql')
		self.assertEqual(chat.prompt, 'SELECT 1;')
		self.assertEqual(chat.response, '1')

	def test_apikey_model(self):
		apikey = APIKey.objects.create(user=self.user, api_key='key123')
		self.assertEqual(apikey.user, self.user)
		self.assertEqual(apikey.api_key, 'key123')

# python manage.py test core