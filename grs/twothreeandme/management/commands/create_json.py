from django.core.management import BaseCommand
from twothreeandme import ttm_functions
from crsapi import functions, settings
from twothreeandme.models import Chromosome, Patients, GenotypesV1, GenomeSnpMap
from django.core.files import File
import json

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--patient', type=str, default='all')
        # parser.add_argument('--offset', type=str, default='0')
        # parser.add_argument('--limit', type=str, default='100')

    def handle(self, *args, **options):
        patients = options['patient']
        patient_id_list = []
        if patients == 'all':
            patients = Patients.objects.all().order_by('id')
            for p in patients:
                patient_id_list.append(p.id)
        else:
            patient_id_list.append(patients)
        message = 'Done'
        return_json = []
        try:
            for patient_id in patient_id_list:
                try:
                    patient = Patients.objects.get(id=patient_id)
                    file_name = str(patient.first_name) + str(patient.last_name)
                except Patients.DoesNotExist:
                    raise functions.CustomError('no patient Exist')

                genoData = GenotypesV1.objects.filter(patient_id=patient_id).select_related('position_map')

                # with open(settings.BASE_DIR + '/output/' + file_name + '.json', 'w+') as f:
                for gd in genoData:
                    if gd.position_map:
                        # print(gd.current_index, gd.position_map.chromosome, gd.position_map.ref,  gd.allele1, gd.allele2)
                        current_dict = {"index": gd.current_index,"contig": str(gd.position_map.chromosome), "position": str(gd.position_map.position),  "ref": str(gd.position_map.ref), "allele1": str(gd.allele1), "allele2": str(gd.allele2)}
                        return_json.append(current_dict)

                    # skip ones without position_map


                status_code = 200

                file_dir = settings.BASE_DIR + '/output/' + file_name + '.json'

                f = open(file_dir, 'w+')
                f.write(json.dumps(return_json))
                f.close()
                print(file_dir)

        except IOError as e:
            e_message = e.message if e.message else ','.join(map(str, e.args))
            message = 'Update Accession Error -   %s' % e_message
            status_code = 500

        # print {'status_code': status_code, 'message': message, 'return_json': return_json}