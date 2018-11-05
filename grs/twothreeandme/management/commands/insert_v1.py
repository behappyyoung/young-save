from django.core.management import BaseCommand
import os
from twothreeandme.models import Patients, GenotypesV1, GenomeSnpMap


class Command(BaseCommand):
    # snp_maps = {}

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str)

    # def create_snp_map(self):
    #     snps = GenomeSnpMap.objects.all()
    #     for snp in snps:
    #         self.snp_maps[snp.ttm_index] = snp.id

    def read_file(self, filename, p_id):
        with open(filename, "rU") as fp:
            content = fp.read()
        c_index = 0
        print(filename, type(content), len(content))
        for i in range(0, len(content), 2):
            f_allele = content[i]
            s_allele = content[i+1]
            # print(f_allele, s_allele)
            if f_allele != '_' or s_allele != '_':
                try:
                    # try:
                    #     map_id = self.snp_maps[str(c_index)]
                    # except KeyError:
                    #     print 'Error - cannot find index : %s - %s, %s' % (c_index, f_allele, s_allele)
                    #     map_id = None

                    try:
                        c_gene = GenotypesV1.objects.get(patient_id=p_id, position_map_id=c_index, allele1=f_allele,
                                                         allele2=s_allele, current_index=c_index)
                        # print 'Index already exist : %s, %s  - skipped' % (c_snp.id, c_index)

                    except GenotypesV1.DoesNotExist:
                        c_gene = GenotypesV1(patient_id=p_id, position_map_id=map_id, allele1=f_allele,
                                                         allele2=s_allele, current_index=c_index)
                        c_gene.save()

                except Exception as e:
                    e_message = e.message if e.message else ','.join(map(str, e.args))
                    print 'Error - updating Genotype [ %s - %s, %s ] : %s' % (c_index, f_allele, s_allele, e_message)

            c_index += 1

        fp.close()
        print('done %s : with %s' % (filename, c_index))

    def handle_file(self, filename, dirname=''):

        (firstname, lastname) = filename.split('.')[0].split('-')
        c_file = os.path.join(dirname, filename)
        # print(filename, firstname, lastname, c_file)
        try:
            c_patient = Patients.objects.get(last_name=lastname, first_name=firstname)

        except Patients.DoesNotExist:
            c_patient = Patients(last_name=lastname, first_name=firstname, email='--', profile_id='',
                                 account_id='')
            c_patient.save()
        self.read_file(c_file, c_patient.id)

    def handle(self, *args, **options):
        directory = options['directory']
        # count = 0
        # self.create_snp_map()
        if os.path.isdir(directory):
            for dirname, dirnames, filenames in os.walk(directory):
                # print path to all subdirectories first.
                # for subdirname in dirnames:
                #     print(os.path.join(dirname, subdirname))
                # print path to all filenames.

                # if count < 20:
                    for filename in filenames:
                        self.handle_file(filename, dirname)
                    # count += 1
        else:
            filename = directory.split('/')[-1]
            self.handle_file(filename, directory.replace('/'+filename, ''))