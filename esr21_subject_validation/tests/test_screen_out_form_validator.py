from django.test import TestCase, tag
from django.core.exceptions import ValidationError
from ..form_validators import ScreenOutFormValidator
from edc_constants.constants import OTHER


@tag('screen')
class TestScreenOutForm(TestCase):
    
    def setUp(self):
        
        self.options = {
            'screen_out_reason':'test',
            'screen_out_other':None,
            'comment':'test', 
        }

    def test_screen_out_valid(self):
        
        form_validator = ScreenOutFormValidator(cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}') 
            
    def test_screen_out_other_valid(self):
        self.options.update({'screen_out_reason': OTHER,
                             'screen_out_other':'test'})
        form_validator = ScreenOutFormValidator(cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}') 
            
    def test_screen_out_reason_invalid(self):
        
        self.options.update({'screen_out_reason': None})
        
        form_validator = ScreenOutFormValidator(cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('screen_out_reason', form_validator._errors)
        
    def test_screen_out_reason_other_invalid(self):
        
        self.options.update({'screen_out_reason': OTHER})
        
        form_validator = ScreenOutFormValidator(cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('screen_out_other', form_validator._errors)
            
            
        
        
