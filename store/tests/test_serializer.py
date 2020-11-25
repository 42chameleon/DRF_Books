from django.test import TestCase
from store.models import Book
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        book1 = Book.objects.create(name='Test book 1', price='100.00', author_name='Mark 1')
        book2 = Book.objects.create(name='Test book 2', price='200.00', author_name='Mark 2')
        data = BooksSerializer([book1, book2], many=True).data
        expected_data = [
            {
                'id': book1 .id,
                'name': book1.name,
                'price': book1.price,
                'author_name' : book1.author_name
            },

            {
                'id': book2.id,
                'name': book2.name,
                'price': book2.price,
                'author_name': book2.author_name
            }
        ]
        self.assertEqual(expected_data, data)
