from django.core.management import BaseCommand
import os, json


class Command(BaseCommand):
    snp_maps = {}

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str)

    def read_file(self, filepath, filename):
        with open(filepath, "rU") as fp:
            content = fp.read()
        fp.close()
        cf_json = json.loads(content)
        c_index = 0
        c_text = ''
        for c in cf_json:
            refs = str(c.get('ref')).split(',')
            for r in refs:
                c_ref = r.strip()
                if 'rs' in r:
                    break

            c_line = str(c_ref) + '\t' + str(c.get('contig')) + '\t' + str(c.get('position')) + '\t' + str(
                c.get('allele1')) + str(c.get('allele2')) + '\n'
            c_text += c_line
            c_index += 1
            print(c_index, c_line)

        tf = open(filepath.replace('.json', '_rs.txt'), 'w')
        tf.write(c_text)
        tf.close()

        print('done %s : with %s' % (filename, c_index))

    def handle_file(self, filename, dirname=''):
        filepath = os.path.join(dirname, filename)
        try:
            self.read_file(filepath, filename)
        except Exception as e:
            e_message = e.message if e.message else ','.join(map(str, e.args))
            message = 'Processing File [%s] Error -   %s' % (filename, e_message)
            print(message)

    def handle(self, *args, **options):
        directory = options['directory']
        if os.path.isdir(directory):
            for dirname, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    if '.json' in filename:
                        self.handle_file(filename, dirname)
        else:
            filename = directory.split('/')[-1]
            self.handle_file(filename, directory.replace('/'+filename, ''))