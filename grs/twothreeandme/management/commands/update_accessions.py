from django.core.management import BaseCommand
from twothreeandme import ttm_functions


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('cid', type=int)
        parser.add_argument('--offset', type=str, default='0')
        parser.add_argument('--startid', type=str, default='0')

    def handle(self, *args, **options):
        cid = options['cid']
        offset = options['offset']
        startid = options['startid']

        f_re = ttm_functions.update_accessions(startid, cid, offset)
        print(f_re)