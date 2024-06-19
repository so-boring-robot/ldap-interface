from django import forms

class PosixGroupForm(forms.Form):
    cn = forms.CharField(label="Nom du groupe", required=True)
    gidNumber = forms.IntegerField(label="ID du groupe", required=True)
    
    def __init__(self, *args, **kwargs):
        default_gidNumber = kwargs.pop('default_gidNumber', None)
        super(PosixGroupForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.field.label=='ID du groupe':
                visible.field.initial =default_gidNumber
            visible.field.widget.attrs['class'] = 'form-control w-25'