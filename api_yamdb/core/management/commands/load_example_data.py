import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from titles.models import Category, Genre, GenreTitle, Title
from reviews.models import Comment, Review
from users.models import User


ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the example data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables."""


class Command(BaseCommand):
    """Provides loading example data form /static/data to DB."""

    help = "Loads example data from /static/data"
    requires_migrations_checks = True
    output_transaction = True

    def handle(self, *args, **options):
        if Title.objects.exists():
            self.stdout.write(self.style.ERROR(ALREDY_LOADED_ERROR_MESSAGE))
            return

        self.stdout.write(self.style.NOTICE('Start loading...'))

        try:
            self._load_data()
        except Exception as err:
            raise CommandError(
                f'Failed load {err.args}, reason: {err}')

        self.stdout.write(self.style.SUCCESS('Loading done.'))

    def _load_data(self):
        def get_file_path(filename):
            return os.path.join(settings.BASE_DIR, 'static', 'data', filename)

        categories = {}
        genres = {}
        titles = {}
        reviews = {}
        users = {}

        path = get_file_path('users.csv')
        with open(path, encoding='utf-8', newline='') as csvfile:
            for row in csv.DictReader(csvfile):
                obj = User(**row)
                obj.save()
                users[obj.id] = obj
        self.stdout.write(self.style.NOTICE(f'{path} done...'))

        path = get_file_path('category.csv')
        with open(path, encoding='utf-8', newline='') as csvfile:
            for row in csv.DictReader(csvfile):
                obj = Category(**row)
                categories[obj.id] = obj
            Category.objects.bulk_create(objs=categories.values())
        self.stdout.write(self.style.NOTICE(f'{path} done...'))

        path = get_file_path('genre.csv')
        with open(path, encoding='utf-8', newline='') as csvfile:
            for row in csv.DictReader(csvfile):
                obj = Genre(**row)
                genres[obj.id] = obj
            Genre.objects.bulk_create(objs=genres.values())
        self.stdout.write(self.style.NOTICE(f'{path} done...'))

        path = get_file_path('titles.csv')
        with open(path, encoding='utf-8', newline='') as csvfile:
            for row in csv.DictReader(csvfile):
                row['category'] = categories[row['category']]
                obj = Title(**row)
                titles[obj.id] = obj
            Title.objects.bulk_create(objs=titles.values())
        self.stdout.write(self.style.NOTICE(f'{path} done...'))

        path = get_file_path('genre_title.csv')
        with open(path, encoding='utf-8', newline='') as csvfile:
            objs = [
                GenreTitle(
                    id=row['id'],
                    genre=genres[row['genre_id']],
                    title=titles[row['title_id']]
                )
                for row in csv.DictReader(csvfile)
            ]
            GenreTitle.objects.bulk_create(objs=objs)
        self.stdout.write(self.style.NOTICE(f'{path} done...'))

        path = get_file_path('review.csv')
        with open(path, encoding='utf-8', newline='') as csvfile:
            for row in csv.DictReader(csvfile):
                row['title'] = titles[row['title_id']]
                row['author'] = users[row['author']]
                obj = Review(**row)
                reviews[obj.id] = obj
            Review.objects.bulk_create(objs=reviews.values())
        self.stdout.write(self.style.NOTICE(f'{path} done...'))

        path = get_file_path('comments.csv')
        with open(path, encoding='utf-8', newline='') as csvfile:
            objs = []
            for row in csv.DictReader(csvfile):
                row['review'] = reviews[row['review_id']]
                row['author'] = users[row['author']]
                objs.append(Comment(**row))
            Comment.objects.bulk_create(objs=objs)
        self.stdout.write(self.style.NOTICE(f'{path} done...'))
