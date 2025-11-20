from django.test import TestCase
from django.urls import reverse

# Create your tests here.
class CoreAPITests(TestCase):
    def test_api_view(self):
        """
        اختبار الواجهة البرمجية التجريبية.
        """
        # نفترض أن لديك مسار URL باسم 'test_api'
        # ستحتاج إلى إضافة هذا المسار في ملف urls.py الخاص بك
        # مثال: path('api/test/', test_api, name='test_api')
        response = self.client.get(reverse('test_api'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "message": "API is working!"})
