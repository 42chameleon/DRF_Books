from django.contrib.auth.models import User
from store.logic import set_rating
from django.test import TestCase
from store.models import UserBookRelation, Book


class SetRatingTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            username='username1',
            first_name='Ivan',
            last_name='Petrov')
        self.user2 = User.objects.create(username='username2', first_name='Shpak', last_name='Shpakov')
        self.user3 = User.objects.create(username='username3', first_name='Bisk', last_name='Biskanov')
        self.book1 = Book.objects.create(name='Test book 1', price='100.00', author_name='Mark 1', discount='15.00',
                                         owner=self.user1)
        self.book2 = Book.objects.create(name='Test book 2', price='200.00', author_name='Mark 1', discount='15.00',
                                         owner=self.user2)
        self.book3 = Book.objects.create(name='Test book 2', price='200.00', author_name='Mark 1', discount='15.00',
                                         owner=self.user2)
        UserBookRelation.objects.create(user=self.user1, book=self.book1, like=True, rate=5)
        UserBookRelation.objects.create(user=self.user2, book=self.book1, like=True, rate=5)
        UserBookRelation.objects.create(user=self.user3, book=self.book1, like=True, rate=4)

    def test_ok(self):
        set_rating(self.book1)
        self.book1.refresh_from_db()
        self.assertEqual('4.67', str(self.book1.rating))
