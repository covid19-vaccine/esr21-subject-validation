from edc_form_validators import FormValidator
from django.core.exceptions import ValidationError

class ScreenOutFormValidator(FormValidator):
    
    def clean(self):
        cleaned_data = self.cleaned_data
        
        self.validate_other_specify(field='screen_out_reason',
                                    other_specify_field='screen_out_other')
        
        self.validate_screen_out_reason(cleaned_data)
        
        self.validate_other_specify(field='screen_out_other')
        
        
    def validate_screen_out_reason(self, cleaned_data=None):
        screen_out_reason = cleaned_data.get('screen_out_reason')

        if not screen_out_reason:
            message = {'screen_out_reason':
                       'Please select a reason for screen out'}
            self._errors.update(message)
            raise ValidationError(message)
