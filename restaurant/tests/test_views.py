from django.test import TestCase
from restaurant.models import MenuFood, MenuCategory, User, Reservation
from django.urls import reverse


class TestHomePage(TestCase):

    def test_home_page_template_used(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'restaurant/home.html')

    def test_home_page_contains_title(self):
        response = self.client.get('/')
        self.assertContains(response, "The Little Lemon", status_code=200)
    
class TestMenuPage(TestCase):
    def setUp(self):
        cat1 = MenuCategory.objects.create(menu_category_name="Category 1")
        cat2 = MenuCategory.objects.create(menu_category_name="Category 2")
        MenuFood.objects.create(food_name="Test Dish", price=10.99, description="A test dish for menu page", category_id=cat1)
        MenuFood.objects.create(food_name="Another Dish", price=12.99, description="Another test dish", category_id=cat2)

    def test_menu_page_template_used(self):
        response = self.client.get('/menu/')
        self.assertTemplateUsed(response, 'restaurant/menu.html')
    
    def test_menu_page_contains_dishes(self):
        response = self.client.get('/menu/')
        self.assertContains(response, "Test Dish")
        self.assertContains(response, "Another Dish")
        self.assertContains(response, "Category 1")
        self.assertContains(response, "Category 2")
        self.assertNotContains(response, "No items in this category at this moment.")
    
    def test_menu_page_has_no_items(self):
        MenuFood.objects.all().delete()
        response = self.client.get('/menu/')
        self.assertContains(response, "No items in this category at this moment.", status_code=200)

class TestReservationPage(TestCase):

    def test_reservation_view_accessible_by_logged_in_user(self):
        #Create a user for testing
        User.objects.create_user(username='testuser', password='testpass')

        #Log the user in
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('reservation'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'restaurant/reservation.html')
    
    def test_reservation_view_redirects_anonymous_user(self):
        response = self.client.get(reverse('reservation'))
        self.assertRedirects(response, '/login/?next=/reservations/')

    





    

    
