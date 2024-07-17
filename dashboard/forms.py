from django import forms
import ldap
from django.conf import settings
from .utils import get_users, get_groups
import hashlib



class MemberForm(forms.Form):
    givenName = forms.CharField(label="Prénom")
    sn = forms.CharField(label="Nom de famille")
    gidNumber = forms.IntegerField(label="ID du groupe", widget = forms.HiddenInput())
    mail = forms.EmailField(label="Adresse mail")
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
    

class EditMemberForm(forms.Form):
    givenName = forms.CharField(label="Prénom (gn)")
    sn = forms.CharField(label="Nom (sn)")
    cn = forms.CharField(label="Nom commun (cn)")
    uid = forms.CharField(label="Nom d'utilisateur (uid)")
    mail = forms.EmailField(label="Adresse mail (mail)")
    gidNumber = forms.IntegerField(label="ID du groupe (gidNumber)")
    uidNumber = forms.IntegerField(label="ID du membre (uidNumber)")
    homeDirectory = forms.CharField(label="Chemin vers le home (homeDirectory)")
    loginShell = forms.CharField(label="Shell (loginShell)")
    
    def __init__(self, *args, **kwargs):
        default_givenName = kwargs.pop('givenName', None)
        default_sn = kwargs.pop('sn', None)
        default_cn = kwargs.pop('cn', None)
        default_uid = kwargs.pop('uid', None)
        default_mail = kwargs.pop('mail', None)
        default_gidNumber = kwargs.pop('gidNumber', None)
        default_uidNumber = kwargs.pop('uidNumber', None)
        default_homeDirectory = kwargs.pop('homeDirectory', None)
        default_loginShell = kwargs.pop('loginShell', None)
        
        super(EditMemberForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.label=='Prénom (gn)':
                field.initial = default_givenName
            if field.label=='Nom (sn)':
                field.initial = default_sn
            if field.label=='Nom commun (cn)':
                field.initial = default_cn
            if field.label=='Nom d\'utilisateur (uid)':
                field.initial = default_uid
            if field.label=='Adresse mail (mail)':
                field.initial = default_mail
            if field.label=='ID du groupe (gidNumber)':
                field.initial = default_gidNumber
            if field.label=='ID du membre (uidNumber)':
                field.initial = default_uidNumber
            if field.label=='Chemin vers le home (homeDirectory)':
                field.initial = default_homeDirectory
            if field.label=='Shell (loginShell)':
                field.initial = default_loginShell
                
            field.widget.attrs['class'] = 'form-control w-25'
            field.widget.attrs['required'] = 'required'
            
    def clean(self, *args, **kwargs):    
        cleaned_data = super().clean()
        
        ldap_conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
        ldap_conn.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
        
        uidNumbers = [int(user['uidNumber']) for user in get_users(ldap_conn)]
            
        uidNumbers.remove(cleaned_data.get('uidNumber'))
        if cleaned_data.get('uidNumber') in uidNumbers:
            raise forms.ValidationError({'uidNumber': ['Cet identifiant existe déjà.',]})
        
        gidNumbers = [int(group['id']) for group in get_groups(ldap_conn)]
        
        if cleaned_data.get('gidNumber') not in gidNumbers:
            raise forms.ValidationError({'gidNumber': ['Ce groupe n\'existe pas.',]})
            
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
            
class BulkAccountForm(forms.Form):
    fichier = forms.FileField(widget=forms.ClearableFileInput(attrs={'class':'form-control form-control-users', 'id':'fileSelect', 'accept':'.csv', 'aria-label':'Importer votre fichier'}))
