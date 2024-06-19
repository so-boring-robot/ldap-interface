from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings 
from ldap.modlist import addModlist
from dashboard.forms import PosixGroupForm

import ldap 

def get_groups(connection):
   # Construire le DN de base pour la recherche des utilisateurs
   base_dn = settings.AUTH_LDAP_BASE_DN
   search_filter = '(objectClass=*)'
   groups = []
   search_attributes = ['objectClass', 'cn', 'gidNumber']
   result = connection.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter, search_attributes)
   # Traiter les résultats
   for dn, entry in result:
      for ent in entry['objectClass']: 
         if ent.decode()=='posixGroup':
            groups.append({'name':entry['cn'][0].decode(),'id':int(entry['gidNumber'][0].decode())})
   return groups

def get_users_in_group(connection, group_code):
   base_dn = settings.AUTH_LDAP_BASE_DN
   search_filter = '(objectClass=*)'
   users = []
   search_attributes = []
      
   # Effectuer la recherche
   result = connection.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter, search_attributes)
   # Traiter les résultats
   for dn, entry in result:
      if entry['objectClass'][1].decode()=='posixAccount' and int(entry['gidNumber'][0].decode())==group_code:
         users.append({'name': entry['givenName'][0].decode(), 'surname':entry['sn'][0].decode(), 'username':entry['uid'][0].decode()})
   return users

def add_posix_group(request):
   try:
      ldap_conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
      ldap_conn.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
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


@login_required
def dashboard(request, group_active=500):
   ldap_conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
   ldap_conn.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)

   groups = get_groups(ldap_conn)
   members = get_users_in_group(ldap_conn, group_active)
   #add_posix_group(ldap_conn, 'infirmier', 507)
   ldap_conn.unbind_s()
   return render(request,'dashboard/dashboard.html', context={'groups':groups, 'members':members, 'active':group_active})