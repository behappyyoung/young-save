from django.core.management import BaseCommand
import os, json, yaml
from twothreeandme.models import Patients, GenotypesV1, GenomeSnpMap
from crsapi import settings


class Command(BaseCommand):
    snp_maps = {}

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str)

    def create_snp_map(self):
        snps = GenomeSnpMap.objects.all()
        for snp in snps:
            self.snp_maps[snp.id] = (snp.chromosome, snp.position, snp.ref)

    def read_file(self, filepath, filename, p_id):
        with open(filepath, "rU") as fp:
            content = fp.read()
        fp.close()
        c_index = 1
        print(filepath, type(content), len(content))
        allele_list = []
        # result_list = []
        data_text = ''
        # for i in range(0, len(content), 2):
        while content != '' and c_index <= 1490984:
            f_allele = content[0]
            s_allele = content[1]
            content = content[2:]
            alleles = str(f_allele) + str(s_allele)
            c_line = ''
            if f_allele != '_' or s_allele != '_':
                refs = str(self.snp_maps[c_index][2]).split(',')
                for r in refs:
                    c_ref = r.strip()
                    if 'rs' in r:
                        break
                c_contig = str(self.snp_maps[c_index][0]).strip()
                c_position = str(self.snp_maps[c_index][1]).strip()
                f_allele = str(f_allele).strip()
                s_allele = str(s_allele).strip()
                # result_dict = {"index": c_index, "contig": c_contig, "position": c_position, "ref": c_ref,
                #                "allele1": f_allele, "allele2": s_allele}
                # result_list.append(result_dict)
                c_line = c_ref + '\t' + c_contig + '\t' + c_position + '\t' + f_allele + s_allele + '\n'
                data_text += c_line

            if settings.LOCAL:
                print(c_index, alleles, c_line)
            c_index += 1
            allele_list.append(alleles)

        # result_json = yaml.safe_dump(result_list)
        # allele_json = yaml.safe_dump(allele_list)
        # result_json = json.dumps(result_list)
        allele_json = json.dumps(allele_list)

        # file_dir = settings.BASE_DIR + '/output/' + filename + '.json'
        # f = open(file_dir, 'w+')
        # f.write(result_json)
        # f.close()

        file_dir = settings.BASE_DIR + '/output/' + filename + '.txt'
        f = open(file_dir, 'w+')
        f.write(data_text)
        f.close()

        try:
            c_v1 = GenotypesV1.objects.get(patient_id=p_id)
            c_v1.filename = filename
            c_v1.alleles = allele_json
            c_v1.data_text = data_text

        except GenotypesV1.DoesNotExist:
            c_v1 = GenotypesV1(patient_id=p_id, file_name=filename, alleles=allele_json, data_text=data_text)

        c_v1.save()

        print('done %s : with %s' % (filename, c_index))

    def handle_file(self, filename, dirname=''):
        print(filename, dirname)
        (firstname, lastname) = filename.split('.')[0].split('-')
        filepath = os.path.join(dirname, filename)
        try:
            c_patient = Patients.objects.get(last_name=lastname, first_name=firstname)

        except Patients.DoesNotExist:
            c_patient = Patients(last_name=lastname, first_name=firstname, email='--', profile_id='',
                                 account_id='')
            c_patient.save()
        try:
            self.read_file(filepath, firstname+lastname, c_patient.id)
        except Exception as e:
            e_message = e.message if e.message else ','.join(map(str, e.args))
            message = 'Processing File [%s] Error -   %s' % (filename, e_message)
            print(message)

    def handle(self, *args, **options):
        directory = options['directory']
        # count = 0
        self.create_snp_map()
        print('map loaded')
        if os.path.isdir(directory):
            for dirname, dirnames, filenames in os.walk(directory):
                # print path to all subdirectories first.
                # for subdirname in dirnames:
                #     print(os.path.join(dirname, subdirname))
                # print path to all filenames.

                for filename in filenames:
                    if '.txt' in filename:
                        self.handle_file(filename, dirname)
        else:
            filename = directory.split('/')[-1]
            self.handle_file(filename, directory.replace('/'+filename, ''))