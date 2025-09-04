from django.test import TestCase
from ..models import Reservation
from datetime import date, time as dtime
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import IntegrityError
# Create your tests here.

class ReservationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user( username='test', password='test')
        self.reservation = Reservation.objects.create(
            user= self.user,
            name="Name",
            email="email@email.com" ,
            date = date(2025,12,12) ,
            time = dtime(12, 0) ,
            party_size= 5 ,
            is_shared = True,
        )
        
    def test_fields(self):
        self.assertIsInstance(self.reservation.name, str)
        self.assertIsInstance(self.reservation.email, str)
        self.assertIsInstance(self.reservation.date, date)
        self.assertIsInstance(self.reservation.time, dtime)
        self.assertIsInstance(self.reservation.party_size, int)
        self.assertIsInstance(self.reservation.is_shared, bool)

    def test_user_cant_reserve_twice_same_day_validation(self):
        reservation2 = Reservation(
            user=self.user,
            name="Name2",
            email="Email2@email.com",
            date = date(2025,12,12) ,
            time = dtime(13, 0) ,
            party_size= 2,
            is_shared = False,
            )
        with self.assertRaises(ValidationError):
            reservation2.clean()

    # Database constraints test

    def test_negative_party_size_constraint(self):
        reservation = Reservation(
            user=self.user,
            name="Negative party size",
            email="email@email.com" ,
            date = date(2025,12,20) ,
            time = dtime(12, 0) ,
            party_size=0,
            is_shared = True, )
        
        with self.assertRaises(IntegrityError):
            reservation.save()



