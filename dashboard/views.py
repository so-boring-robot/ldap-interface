from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings 
from ldap.modlist import addModlist
from dashboard.forms import PosixGroupForm, MemberForm
from .utils import get_groups, get_users_in_group, hash_password_md5, compare_strings
import ldap 
import hashlib


@login_required
def add_posix_group(request):
   try:
      ldap_conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
      ldap_conn.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
      
      groups_id = [int(group['id']) for group in get_groups(ldap_conn)]
      groups_id.sort()
      new_default_id = groups_id[-1:][0]+1
      
      form = PosixGroupForm(default_gidNumber=new_default_id)
      
      if request.method=="POST":
         form = PosixGroupForm(request.POST, default_gidNumber=new_default_id)
         if form.is_valid():
            cn = form.cleaned_data['cn']
            gidNumber = form.cleaned_data['gidNumber']
            # Construire le DN du nouveau groupe
            base_dn = settings.AUTH_LDAP_BASE_DN
            group_dn = f"cn={cn},{base_dn}"

            # Définir les attributs du groupe
            attrs = {
               'objectClass': [b'top', b'posixGroup'],
               'cn': [cn.encode('utf-8')],
               'gidNumber': [str(gidNumber).encode('utf-8')],
            }

            # Convertir les attributs en format LDAP
            ldif = addModlist(attrs)

            # Ajouter le groupe
            ldap_conn.add_s(group_dn, ldif)
            print(f"Groupe {cn} ajouté avec succès.")
            return redirect('dashboard', groups_id[:1][0])
      
   except ldap.LDAPError as e:
      print(f"Erreur lors de l'ajout du groupe : {e}")
      return redirect('dahsboard', groups_id[:1][0])
      
   return render(request,'dashboard/add_posix_group.html', context={'form':form})

def add_member(request, group_active):
   try:
      ldap_conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
      ldap_conn.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
      members = get_users_in_group(ldap_conn, group_active)
      users_uidNumber = [int(user['uidNumber']) for user in get_users_in_group(ldap_conn, group_active)]
      users_uidNumber.sort()
      new_default_uidNumber = users_uidNumber[-1:][0]+1
      form = MemberForm(default_uidNumber=new_default_uidNumber, default_gidNumber=group_active)
      if request.method=='POST':
         form = MemberForm(request.POST, default_uidNumber=new_default_uidNumber, default_gidNumber=group_active)
         if form.is_valid():
            uidNumber = form.cleaned_data['uidNumber']
            uid = ''
            gidNumber = request.POST['gidNumber']
            sn = form.cleaned_data['sn']
            cn = f"{form.cleaned_data['givenName']} {form.cleaned_data['sn']}"
            givenName = form.cleaned_data['givenName']
            password_1 = hash_password_md5(form.cleaned_data['password_1'])
            
            uid_sample = givenName[:2].lower()+sn.lower()
            rest_uids = []
            current_uids = [member['uid'] for member in members]
            for i in range(len(current_uids)):
               if uid_sample in current_uids[i]:
                  rest_uids.append(compare_strings(uid_sample, current_uids[i]))
            rest_uids.sort()
            print(rest_uids)
            if rest_uids:
               if rest_uids[-1:]=='':
                  uid = uid_sample+'2'
               else:
                  print(rest_uids[-1:][0])
                  uid = uid_sample+str(int(rest_uids[-1:][0])+1)
            else:
               uid = uid_sample
                                 
            homeDirectory = f'/home/users/{uid}'
            loginShell = '/bin/bash'
            
            base_dn = settings.AUTH_LDAP_BASE_DN
            user_dn = f'uid={uid},{base_dn}'

            # Définir les attributs de l'utilisateur
            attrs = {
                  'objectClass': [b'inetOrgPerson', b'posixAccount', b'top'],
                  'uid': [uid.encode('utf-8')],
                  'cn': [cn.encode('utf-8')],
                  'sn': [sn.encode('utf-8')],
                  'givenName': [givenName.encode('utf-8')],
                  'userPassword': [password_1.encode('utf-8')],
                  'gidNumber': [str(gidNumber).encode('utf-8')],
                  'uidNumber': [str(uidNumber).encode('utf-8')],
                  'homeDirectory': [homeDirectory.encode('utf-8')],
                  'loginShell': [loginShell.encode('utf-8')],
            }

            # Convertir les attributs en format LDAP
            ldif = addModlist(attrs)

            # Ajouter l'utilisateur
            ldap_conn.add_s(user_dn, ldif)
            
            return redirect('dashboard', group_active)
            
   except ldap.LDAPError as e:
      print(f"Erreur lors de l'ajout du groupe : {e}")
      return redirect('dashboard', group_active)
      
   return render(request,'dashboard/add_member.html', context={'form':form, 'active':group_active})
   

@login_required
def dashboard(request, group_active=500):
   ldap_conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
   ldap_conn.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)

   groups = get_groups(ldap_conn)
   members = get_users_in_group(ldap_conn, group_active)
   #add_posix_group(ldap_conn, 'infirmier', 507)
   ldap_conn.unbind_s()
   
   return render(request,'dashboard/dashboard.html', context={'groups':groups, 'members':members, 'active':group_active})