from django.test import TestCase
from django.urls import reverse
from restaurant.models import ContactMessage

class TestContactView(TestCase):

    def test_create_contact_message_when_valid(self):
        form_data = {
            'name': 'Test User',
            'subject': 'Test Subject',
            'email': 'test@email.com',
            'message': 'Valid message.' }
        response = self.client.post(reverse('contact'), data=form_data)

        # Check that the message was created and we got redirected 
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ContactMessage.objects.filter(name='Test User').exists())
    
    def test_dont_create_contact_message_when_invalid(self):
        form_data = {
            'name': '',
            'subject': '',
            'email': 'invalid-email',
            'message': '' }
        response = self.client.post(reverse('contact'), data=form_data)

        # Check that we got a 200 response and the form is invalid
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)

        form = response.context['form']
        self.assertFormError(form, 'name', 'This field is required.')
        self.assertFormError(form, 'email', 'Enter a valid email address.')
        self.assertFormError(form, 'message', 'This field is required.')

        self.assertFalse(ContactMessage.objects.filter(email= 'invalid-email').exists())

