from django.test import TestCase, SimpleTestCase
from gims import settings
from lib.cartagenia import BenchLabNgs, AssayRegistrationData, Patient, Check, Upload, ListAnalysis, ReportExport
import json
from base64 import decodestring


# class TestUploadVCF(TestCase):
#     def test_upload_vcf(self):
#         cwb = BenchLabNgs(settings.CARTAGENIA_IP, 443, settings.CARTAGENIA_USERNAME, log_level='debug')
#         upload_json = json.loads('{"username": "bcm", "file_type": "VCF_FILE", "medical_record_number": "10000057-9", "trio_strict_checking": "no", "sample_accession_id": "SCGV1-01", "specimen_type": "blood", "file_path": "gs://cgs-demo-thirdparty-dropin/Symphony_1213_2016_Stanford_Pilot2_85/SCGV1-01/Variants/SCGV1-01.snvindel.var.vcf", "analysis_pipeline": "Test"}')
#         response = cwb.assayRegistration('upload', upload_json)
#         print response, response.content
#         pass


# class TestListAnalysis(SimpleTestCase):
#     def test_ListAnalysis(self):
#         l = ListAnalysis(settings.CARTAGENIA_USERNAME, '10000057-9')
#         l_json =  l.getJson()
#         self.assertEquals(l_json, {'username': 'bcm', 'medical_record_number': '10000057-9'})


class TestAnalysis(TestCase):
    def test_upload_vcf(self):
        cwb = BenchLabNgs(settings.CARTAGENIA_IP, 443, settings.CARTAGENIA_USERNAME, log_level='debug')
        list_analysis = ListAnalysis(settings.CARTAGENIA_USERNAME, '10000057-9')
        list_analysis_json = list_analysis.getJson()
        a = cwb.analysis('list', list_analysis_json)
        print a, a.json()
        report_export = ReportExport(settings.CARTAGENIA_USERNAME, 'SCGV1-01_10000057-9')
        report_export_json = report_export.getJson()
        r = cwb.analysis('report', report_export_json)
        response_json = r.json()
        pdf_kount = 0
        reports = response_json.get('reports')
        # if reports:
        #     for pdf_content in reports:
        #         pdf_kount += 1
        #         pdf_file_name = '%s_report_%s.pdf' % ('SCGV1-01_10000057-9', pdf_kount)
        #         with open('/Users/s0199669/cgsdev/gims/test/'+pdf_file_name, 'wb') as pdf_file:
        #             pdf_file.write(decodestring(pdf_content['encoded_content']))
        print r.json(), reports, type(reports)
        pass


# class TestReportExport(TestCase):
#     def test_ReportExport(self):
#         r = ReportExport(settings.CARTAGENIA_USERNAME, 'PA_10000057-9')
#         r_json =  r.getJson()
#         print r, r_json
