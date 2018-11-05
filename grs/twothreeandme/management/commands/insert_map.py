from django.core.management import BaseCommand
from twothreeandme import ttm_functions


class Command(BaseCommand):

    def handle(self, *args, **options):
        f_re = ttm_functions.insert_map()
        print(f_re)