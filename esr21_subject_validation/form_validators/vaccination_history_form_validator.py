from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_constants.constants import YES
from edc_form_validators import FormValidator


class VaccinationHistoryFormValidator(FormValidator):
    vaccination_details_cls = 'esr21_subject.vaccinationdetails'

    @property
    def vaccination_details_model_cls(self):
        return django_apps.get_model(self.vaccination_details_cls)

    def clean(self):

        self.required_if(
            YES,
            field='received_vaccine',
            field_required='dose_quantity', )

        dose1_required = ['dose1_product_name', 'dose1_date']
        dose_quantity = self.cleaned_data.get('dose_quantity')

        for dose1_field in dose1_required:
            self.required_if_true(
                dose_quantity in ['1', '2'],
                field_required=dose1_field)

        fields_other = {'dose1_product_name': 'dose1_product_other',
                        'dose2_product_name': 'dose2_product_other'}

        for field, field_other in fields_other.items():
            self.validate_other_specify(
                field=field,
                other_specify_field=field_other)

        dose2_required = ['dose2_product_name', 'dose2_date']

        for dose2_field in dose2_required:
            self.required_if(
                '2',
                field='dose_quantity',
                field_required=dose2_field)
 
        dose_1 = self.cleaned_data['dose1_product_name']
        dose_2 = self.cleaned_data['dose2_product_name']
        num_of_doses = self.cleaned_data['dose_quantity']

        if num_of_doses == '2' and 'janssen' in [dose_2, dose_1]:
            message = {
                'dose2_product_name':
                    f'Participant has received {dose_1} and '
                    f'{dose_2} therefore they are not eligible to participate'
            }
            raise ValidationError(message)

        self.validate_number_of_doses()
        self.validate_first_dose()
        self.validate_first_dose_date()
        self.validate_second_dose()
        self.validate_second_dose_date()

    def vaccination_details_objs(self, subject_identifier):
        return self.vaccination_details_model_cls.objects.filter(
            subject_visit__subject_identifier=subject_identifier)

    def validate_number_of_doses(self):
        subject_identifier = self.cleaned_data.get('subject_identifier')
        dose_received = self.cleaned_data.get('dose_quantity')
        dose2_product_name = self.cleaned_data.get('dose2_product_name')
        dose1_product_name = self.cleaned_data.get('dose1_product_name')
        vac_details_count = self.vaccination_details_objs(subject_identifier).count()
        message = {
            'dose_quantity': f'The participant has received {vac_details_count} doses'
                             f' of AstraZeneca (AZD 1222), Please correct your entry'}
        if not str(vac_details_count) == dose_received and not (
                dose1_product_name == 'azd_1222' or dose2_product_name == 'azd_1222'):
            raise ValidationError(message)

    def dose_received(self, subject_identifier, dose):
        try:
            dose_received = self.vaccination_details_model_cls.objects.get(
                subject_visit__subject_identifier=subject_identifier,
                received_dose_before=dose)
        except self.vaccination_details_model_cls.DoesNotExist:
            pass
        else:
            return dose_received

    def validate_first_dose(self):
        subject_identifier = self.cleaned_data.get('subject_identifier')
        dose1_product_name = self.cleaned_data.get('dose1_product_name')
        first_dose = self.dose_received(subject_identifier=subject_identifier,
                                        dose='first_dose')
        if not dose1_product_name == 'azd_1222' and first_dose:
            message = {'dose1_product_name':
                           f'The EDC has a record that the participate received '
                           f'AstraZeneca (AZD 1222) as a first dose, Please recheck the'
                           f' participants\'s dose records'}
            raise ValidationError(message)
        elif not first_dose and dose1_product_name == 'azd_1222':
            message = {'dose1_product_name':
                           f'The EDC has a no record that the participate received '
                           f'AstraZeneca (AZD 1222) as a first dose, Please recheck the'
                           f' participants\'s dose records'}
            raise ValidationError(message)

    def validate_first_dose_date(self):
        subject_identifier = self.cleaned_data.get('subject_identifier')
        dose1_date = self.cleaned_data.get('dose1_date')
        dose1_product_name = self.cleaned_data.get('dose1_product_name')
        first_dose = self.dose_received(subject_identifier=subject_identifier,
                                        dose='first_dose')
        if dose1_product_name == 'azd_1222' and first_dose:
            first_dose_date = first_dose.vaccination_date.date()
            if not (first_dose_date == dose1_date):
                message = {'dose1_date':
                               f'The participant received AstraZeneca (AZD 1222) as first'
                               f' dose on date {first_dose_date}'}
                raise ValidationError(message)

    def validate_second_dose(self):
        subject_identifier = self.cleaned_data.get('subject_identifier')
        dose2_product_name = self.cleaned_data.get('dose2_product_name')
        second_dose = self.dose_received(subject_identifier=subject_identifier,
                                         dose='second_dose')
        if not dose2_product_name == 'azd_1222' and second_dose:
            message = {'dose2_product_name':
                           f'The EDC has a record that the participate received '
                           f'AstraZeneca (AZD 1222) as a second dose, Please recheck the'
                           f' participants\'s dose record'}
            raise ValidationError(message)
        elif not second_dose and dose2_product_name == 'azd_1222':
            message = {'dose2_product_name':
                           f'The EDC has a no record that the participate received '
                           f'AstraZeneca (AZD 1222) as a second dose, Please recheck the'
                           f' participants\'s dose record'}
            raise ValidationError(message)

    def validate_second_dose_date(self):
        subject_identifier = self.cleaned_data.get('subject_identifier')
        dose2_date = self.cleaned_data.get('dose2_date')
        dose2_product_name = self.cleaned_data.get('dose2_product_name')
        second_dose = self.dose_received(subject_identifier=subject_identifier,
                                         dose='second_dose')
        if not dose2_product_name == 'azd_1222' and second_dose:
            second_dose_date = second_dose.vaccination_date.date()
            if not second_dose_date == dose2_date:
                message = {'dose2_date':
                               f'The participant received AstraZeneca (AZD 1222) as '
                               f'second dose on date {second_dose_date}'}
                raise ValidationError(message)
