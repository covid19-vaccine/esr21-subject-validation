from edc_constants.constants import YES, OTHER
from edc_form_validators import FormValidator
from .crf_form_validator import CRFFormValidator


class MedicalHistoryFormValidator(CRFFormValidator, FormValidator):

    def clean(self):

        self.m2m_required_if(YES,
                             field='prior_covid_infection',
                             m2m_field='covid_symptoms')

        self.m2m_other_specify(OTHER,
                               m2m_field='covid_symptoms',
                               field_other='symptoms_other')

        self.m2m_other_specify(OTHER,
                               m2m_field='comorbidities',
                               field_other='comorbidities_other')

        super().clean()
