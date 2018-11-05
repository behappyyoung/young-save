from django.core.management import BaseCommand
from twothreeandme import ttm_functions
from twothreeandme.models import Chromosome


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('chromosome_id', type=str)
        parser.add_argument('--offset', type=str, default='0')
        parser.add_argument('--limit', type=str, default='100')

    def handle(self, *args, **options):
        chromosome_id = options['chromosome_id']

        offset = options['offset']
        limit = options['limit']
        if offset.lower() == 'last':
            chromosome = Chromosome.objects.filter().last()
            offset = chromosome.offset
        print('offset', offset)
        f_re = ttm_functions.update_chromosome(chromosome_id, offset, limit)

        print(f_re)