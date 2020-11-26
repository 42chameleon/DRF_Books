import json

from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test username')
        self.book1 = Book.objects.create(name='Test book 1', price=100, author_name='author1', owner=self.user)
        self.book2 = Book.objects.create(name='Test book 2', price=200, author_name='author2', owner=self.user)
        self.book3 = Book.objects.create(name='Test book 3 author1', price=200, author_name='author3', owner=self.user)

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BooksSerializer([self.book1, self.book2, self.book3], many=True).data
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 200})
        serializer_data = BooksSerializer([self.book2, self.book3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data, serializer_data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'author 1'})
        serializer_data = BooksSerializer([self.book1, self.book3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'name'})
        serializer_data = BooksSerializer([self.book1, self.book2, self.book3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-list')
        data = {
            "name": "Shpak",
            "price": "1000.00",
            "author_name": "Mark Shpak"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        url = reverse('book-detail', args=(self.book1.id,))
        data = {
            "name": self.book1.name,
            "price": "4000.00",
            "author_name": self.book1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book1.refresh_from_db()
        self.assertEqual(4000.00, self.book1.price)

    def test_delete(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-detail', args={self.book2.id})
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, Book.objects.all().count())

    def test_update_not_owner(self):
        self.user2 = User.objects.create(username='test username2')
        url = reverse('book-detail', args=(self.book1.id,))
        data = {
            "name": self.book1.name,
            "price": "4000.00",
            "author_name": self.book1.author_name,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)
        self.book1.refresh_from_db()
        self.assertEqual(100, self.book1.price)

    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='test username2', is_staff=True)
        url = reverse('book-detail', args=(self.book1.id,))
        data = {
            'id': self.book1.id,
            'name': self.book1.name,
            'price': '4000.00',
            'author_name': self.book1.author_name,
            'owner': self.book1.owner.id
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book1.refresh_from_db()
        self.assertEqual(data, response.data)
        self.assertEqual(4000.00, self.book1.price)
