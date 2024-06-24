from django import forms
import ldap
from django.conf import settings
from .utils import get_users, get_groups
import hashlib



class MemberForm(forms.Form):
    givenName = forms.CharField(label="Prénom")
    sn = forms.CharField(label="Nom de famille")
    gidNumber = forms.IntegerField(label="ID du groupe", widget = forms.HiddenInput())
    password_1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput())
    password_2 = forms.CharField(label="Confirmer le mot de passe", widget=forms.PasswordInput())
    uidNumber = forms.IntegerField(label="ID du membre")
    
    def __init__(self, *args, **kwargs):
        default_uidNumber = kwargs.pop('default_uidNumber', None)
        default_gidNumber = kwargs.pop('default_gidNumber', None)
        super(MemberForm, self).__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            if field.label=='ID du membre':
                field.initial = default_uidNumber
            if field.label=='ID du groupe':
                field.initial = default_gidNumber
            field.widget.attrs['class'] = 'form-control w-25'
            field.widget.attrs['required'] = 'required'
            
    def clean(self, *args, **kwargs):    
        cleaned_data = super().clean()
        
        ldap_conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
        ldap_conn.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
        
        uidNumbers = [int(user['uidNumber']) for user in get_users(ldap_conn)]
            
        if cleaned_data.get('uidNumber') in uidNumbers:
            raise forms.ValidationError({'uidNumber': ['Cet identifiant existe déjà.',]})
        
        gidNumbers = [int(group['id']) for group in get_groups(ldap_conn)]
        
        if cleaned_data.get('gidNumber') not in gidNumbers:
            raise forms.ValidationError({'gidNumber': ['Ce groupe n\'existe pas.',]})
        
        field1 = cleaned_data.get('password_1')
        field2 = cleaned_data.get('password_2')

        if field1 and field2:
            if field1 != field2:
                raise forms.ValidationError({'password_1': ['Les mots de passe sont différents.',]})
            
        return cleaned_data
            
class PosixGroupForm(forms.Form):
    cn = forms.CharField(label='Nom du groupe')
    gidNumber = forms.IntegerField(label='ID du groupe')
    
    def __init__(self, *args, **kwargs):
        default_gidNumber = kwargs.pop('default_gidNumber', None)
        super(PosixGroupForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if visible.field.label=='ID du groupe':
                visible.field.initial =default_gidNumber
            visible.field.widget.attrs['class'] = 'form-control w-25'
            visible.field.widget.attrs['required'] = 'required'