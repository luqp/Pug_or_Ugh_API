from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

import json

from .models import Dog, UserDog, UserPref
from . import serializers


class createModelTest(TestCase):
    def setUp(self):
        self.dog = Dog.objects.create(
            name="Pez",
            image_filename="6.jpg",
            breed="Unknown Mix",
            age=3,
            gender="m",
            size="m"
        )
        self.dog2 = Dog.objects.create(
            name="Cocoa",
            image_filename="7.jpg",
            breed="Chocolate Labrador Mix",
            age=60,
            gender="f",
            size="l"
        )
        self.user = User.objects.create_user(
            username="User1",
            password="1234"
        )

    def test_dog_model_create(self):
        pk_dog = self.dog.pk
        self.assertEqual(Dog.objects.filter(pk=pk_dog).exists(), True)
        self.assertTrue(self.dog.age_status == 'b')

    def test_userdog_model_create(self):
        user = self.user
        dog = self.dog2
        dog_search = Dog.objects.filter(
            userdog__user__id=user.id,
            userdog__dog__id=dog.id
        )
        user_dog = UserDog.objects.filter(
            user__id=user.id,
            dog__id=dog.id
        ).first()
        self.assertEqual(dog_search.exists(), True)
        self.assertTrue(user_dog.status == 'u')

    def test_userpref_model_create(self):
        user = self.user
        user_pref = UserPref.objects.filter(user__id=user.id)
        self.assertEqual(user_pref.exists(), True)
        self.assertTrue(user_pref[0].age == "b,y,a,s")
        self.assertTrue(user_pref[0].gender == "f,m")
        self.assertTrue(user_pref[0].size == "s,m,l,xl")


class SetUpTestCase(APITestCase):
    def setUp(self):
        self.dog = Dog.objects.create(
            name="Pez",
            image_filename="6.jpg",
            breed="Unknown Mix",
            age=3,
            gender="m",
            size="m"
        )
        self.dog2 = Dog.objects.create(
            name="Cocoa",
            image_filename="7.jpg",
            breed="Chocolate Labrador Mix",
            age=60,
            gender="f",
            size="l"
        )
        self.user = User.objects.create_user(
            username="User",
            password="1234"
        )
        token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)


class UserPrefViewTest(SetUpTestCase):

    def test_preferences_view_get_request(self):
        response = self.client.get('/api/user/preferences/')
        assert response.status_code == 200
        self.assertEqual(
            json.loads(response.content),
            {"age": "b,y,a,s", "gender": "f,m", "size": "s,m,l,xl"})

    def test_preferences_view_put_request(self):
        response = self.client.put(
            path='/api/user/preferences/',
            data={"age": "a,s", "gender": "f", "size": "m,l,xl"},
            format='json'
        )
        assert response.status_code == 200
        self.assertEqual(
            json.loads(response.content),
            {"age": "a,s", "gender": "f", "size": "m,l,xl"})


class StateDogViewTest(SetUpTestCase):
    def test_next_dog_view_get_undecided(self):
        '''
            Test the first request of API of undecided group,
            it should contain data
        '''
        serializer = serializers.DogSerializer(self.dog)
        response = self.client.get(
            reverse(
                'dog-next-dog',
                kwargs={'pk': -1, 'dog_status': 'undecided'}
            ))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), serializer.data)

    def test_next_dog_liked_first_time(self):
        '''
            Test the first request of API of liked group,
            it should return 404
        '''
        response = self.client.get(
            reverse(
                'dog-next-dog',
                kwargs={'pk': -1, 'dog_status': 'liked'}
            ))
        self.assertEqual(response.status_code, 404)

    def test_next_dog_disliked_first_time(self):
        '''
            Test the first request of API of disliked group,
            it should return 404
        '''
        response = self.client.get(
            reverse(
                'dog-next-dog',
                kwargs={'pk': -1, 'dog_status': 'disliked'}
            ))
        self.assertEqual(response.status_code, 404)

    def test_status_update_view_liked(self):
        pk = 1
        response = self.client.put(
            reverse('dog-status-update',
                    kwargs={'pk': pk, 'dog_status': 'liked'}))
        user_dog = UserDog.objects.filter(dog__id=pk).first()
        self.assertEqual(response.status_code, 204)
        self.assertEqual(user_dog.status, 'l')

    def test_status_update_view_disliked(self):
        pk = 1
        response = self.client.put(
            reverse('dog-status-update',
                    kwargs={'pk': pk, 'dog_status': 'disliked'}))
        user_dog = UserDog.objects.filter(dog__id=pk).first()
        self.assertEqual(response.status_code, 204)
        self.assertEqual(user_dog.status, 'd')

    def test_status_update_view_undecided(self):
        pk = 1
        response = self.client.put(
            reverse('dog-status-update',
                    kwargs={'pk': pk, 'dog_status': 'disliked'}))
        response = self.client.put(
            reverse('dog-status-update',
                    kwargs={'pk': pk, 'dog_status': 'undecided'}))
        user_dog = UserDog.objects.filter(dog__id=pk).first()
        self.assertEqual(response.status_code, 204)
        self.assertEqual(user_dog.status, 'u')

    def test_next_dog_liked(self):
        pk = 2
        self.client.put(
            reverse('dog-status-update',
                    kwargs={'pk': pk, 'dog_status': 'liked'}))
        response = self.client.get(
            reverse('dog-next-dog',
                    kwargs={'pk': -1, 'dog_status': 'liked'}))
        user_dog = UserDog.objects.select_related(
            'dog').filter(dog__id=pk).first()
        serializer = serializers.DogSerializer(user_dog.dog)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), serializer.data)

    def test_next_dog_disliked(self):
        pk = 2
        self.client.put(
            reverse('dog-status-update',
                    kwargs={'pk': pk, 'dog_status': 'disliked'}))
        response = self.client.get(
            reverse('dog-next-dog',
                    kwargs={'pk': -1, 'dog_status': 'disliked'}))
        user_dog = UserDog.objects.select_related(
            'dog').filter(dog__id=pk).first()
        serializer = serializers.DogSerializer(user_dog.dog)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), serializer.data)

    def test_next_dog_undecided_empty(self):
        for pk in range(1, Dog.objects.count() + 1):
            self.client.put(
                reverse('dog-status-update',
                        kwargs={'pk': pk, 'dog_status': 'liked'}))
        response = self.client.get(
            reverse('dog-next-dog',
                    kwargs={'pk': -1, 'dog_status': 'undecided'}))
        self.assertEqual(response.status_code, 404)
