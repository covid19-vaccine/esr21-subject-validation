from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_base import get_utcnow

from .models import Appointment, SubjectVisit, VaccinationDetails
from ..constants import FIRST_DOSE, SECOND_DOSE
from ..form_validators import VaccinationHistoryFormValidator


@tag('history')
class TestVaccinationHistoryFormValidator(TestCase):

    def setUp(self):
        vaccination_details_cls = 'esr21_subject_validation.vaccinationdetails'
        VaccinationHistoryFormValidator.vaccination_details_cls = vaccination_details_cls

        self.subject_identifier = '111111'

        appointment = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='1000',
            schedule_name='esr21_enrol_schedule')

        self.visit_1000 = SubjectVisit.objects.create(
            appointment=appointment,
            schedule_name='esr21_enrol_schedule')

        self.appt_1070 = Appointment.objects.create(
            subject_identifier=self.subject_identifier,
            visit_code='1070',
            schedule_name='esr21_fu_schedule',
            appt_datetime=get_utcnow())

        self.visit_1070 = SubjectVisit.objects.create(
            appointment=self.appt_1070,
            schedule_name='esr21_fu_schedule')

    def test_number_of_doses(self):
        VaccinationDetails.objects.create(
            subject_visit=self.visit_1000,
            report_datetime=get_utcnow(),
            received_dose_before=FIRST_DOSE,
            vaccination_date=get_utcnow(),
            next_vaccination_date=(get_utcnow() + relativedelta(days=56)).date())

        VaccinationDetails.objects.create(
            subject_visit=self.visit_1070,
            report_datetime=(get_utcnow() + relativedelta(days=56)).date(),
            received_dose_before=SECOND_DOSE,
            vaccination_date=get_utcnow(),
            next_vaccination_date=(get_utcnow() + relativedelta(days=56)).date())

        clean_data = {
            'subject_identifier': self.subject_identifier,
            'dose_quantity': '1',
        }

        form_validator = VaccinationHistoryFormValidator(
            cleaned_data=clean_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('dose_quantity', form_validator._errors)

    def test_first_dose(self):
        VaccinationDetails.objects.create(
            subject_visit=self.visit_1000,
            report_datetime=get_utcnow(),
            received_dose_before=FIRST_DOSE,
            vaccination_date=get_utcnow(),
            next_vaccination_date=(get_utcnow() + relativedelta(days=56)).date())

        clean_data = {
            'subject_identifier': self.subject_identifier,
            'dose_quantity': '1',
            'dose1_product_name': 'vin'
        }

        form_validator = VaccinationHistoryFormValidator(
            cleaned_data=clean_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('dose1_product_name', form_validator._errors)

    def test_first_dose_date(self):
        VaccinationDetails.objects.create(
            subject_visit=self.visit_1000,
            report_datetime=get_utcnow(),
            received_dose_before=FIRST_DOSE,
            vaccination_date=get_utcnow(),
            next_vaccination_date=(get_utcnow() + relativedelta(days=56)).date())

        clean_data = {
            'subject_identifier': self.subject_identifier,
            'dose_quantity': '1',
            'dose1_product_name': 'azd_1222',
            'dose1_date': get_utcnow()
        }

        form_validator = VaccinationHistoryFormValidator(
            cleaned_data=clean_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('dose1_date', form_validator._errors)

    def test_second_dose(self):
        VaccinationDetails.objects.create(
            subject_visit=self.visit_1000,
            report_datetime=get_utcnow(),
            received_dose_before=FIRST_DOSE,
            vaccination_date=get_utcnow(),
            next_vaccination_date=(get_utcnow() + relativedelta(days=56)).date())

        VaccinationDetails.objects.create(
            subject_visit=self.visit_1070,
            report_datetime=(get_utcnow() + relativedelta(days=56)).date(),
            received_dose_before=SECOND_DOSE,
            vaccination_date=get_utcnow(),
            next_vaccination_date=(get_utcnow() + relativedelta(days=56)).date())

        clean_data = {
            'subject_identifier': self.subject_identifier,
            'dose_quantity': '2',
            'dose1_product_name': 'azd_1222',
            'dose1_date': get_utcnow().date(),
            'dose2_product_name': 'vin',
            'dose2_date': (get_utcnow() + relativedelta(days=56)).date()
        }

        form_validator = VaccinationHistoryFormValidator(
            cleaned_data=clean_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('dose2_product_name', form_validator._errors)

    def test_second_dose(self):
        VaccinationDetails.objects.create(
            subject_visit=self.visit_1000,
            report_datetime=get_utcnow(),
            received_dose_before=FIRST_DOSE,
            vaccination_date=get_utcnow(),
            next_vaccination_date=(get_utcnow() + relativedelta(days=56)).date())

        VaccinationDetails.objects.create(
            subject_visit=self.visit_1070,
            report_datetime=(get_utcnow() + relativedelta(days=56)).date(),
            received_dose_before=SECOND_DOSE,
            vaccination_date=get_utcnow(),
            next_vaccination_date=(get_utcnow() + relativedelta(days=56)).date())

        clean_data = {
            'subject_identifier': self.subject_identifier,
            'dose_quantity': '2',
            'dose1_product_name': 'azd_1222',
            'dose1_date': get_utcnow().date(),
            'dose2_product_name': 'azd_1222',
            'dose2_date': (get_utcnow() + relativedelta(days=56)).date()
        }

        form_validator = VaccinationHistoryFormValidator(
            cleaned_data=clean_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')
