from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg, F
from django.test import TestCase
from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        user1 = User.objects.create(username='username1', first_name='Ivan', last_name='Petrov')
        user2 = User.objects.create(username='username2', first_name='Shpak', last_name='Shpakov')
        user3 = User.objects.create(username='username3', first_name='Bisk', last_name='Biskanov')
        book1 = Book.objects.create(name='Test book 1', price='100.00', author_name='Mark 1', discount='15.00',
                                    owner=user1)
        book2 = Book.objects.create(name='Test book 2', price='200.00', author_name='Mark 2', discount='15.00',
                                    owner=user2)
        UserBookRelation.objects.create(user=user1, book=book1, like=True, rate=5)
        UserBookRelation.objects.create(user=user2, book=book1, like=True, rate=5)
        UserBookRelation.objects.create(user=user3, book=book1, like=True, rate=4)
        UserBookRelation.objects.create(user=user1, book=book2, like=True, rate=3)
        UserBookRelation.objects.create(user=user1, book=book2, like=True, rate=5)
        UserBookRelation.objects.create(user=user1, book=book2, like=False)
        books = Book.objects.all().annotate(
            owner_name=F('owner__username'),
            price_with_discount=F('price') - F('discount'),
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            rating=Avg('userbookrelation__rate')
        ).order_by('id')
        data = BooksSerializer(books, many=True).data
        expected_data = [
            {
                'id': book1.id,
                'name': book1.name,
                'price': book1.price,
                'author_name': book1.author_name,
                'annotated_likes': 3,
                'rating': '4.67',
                'discount': '15.00',
                'price_with_discount': '85.00',
                'owner_name': book1.owner.username,
                'readers': [
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Petrov'
                    },
                    {
                        'first_name': 'Shpak',
                        'last_name': 'Shpakov'
                    },
                    {
                        'first_name': 'Bisk',
                        'last_name': 'Biskanov'
                    },
                ],
            },

            {
                'id': book2.id,
                'name': book2.name,
                'price': book2.price,
                'author_name': book2.author_name,
                'annotated_likes': 2,
                'rating': '4.00',
                'discount': '15.00',
                'price_with_discount': '185.00',
                'owner_name': book2.owner.username,
                'readers': [
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Petrov'
                    },
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Petrov'
                    },
                    {
                        'first_name': 'Ivan',
                        'last_name': 'Petrov'
                    }
                ],

            }
        ]
        self.assertEqual(expected_data, data)
