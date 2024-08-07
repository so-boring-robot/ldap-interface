from django.forms import ModelForm
from .models import Schema

class SchemaForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SchemaForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control w-25'
            field.widget.attrs['required'] = 'required'
            
    class Meta:
        model = Schema
        fields = ["nom"]
    
            