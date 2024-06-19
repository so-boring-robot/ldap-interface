from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings 
from ldap.modlist import addModlist

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
      if entry['objectClass'][0].decode()=='posixGroup':
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

@login_required
def dashboard(request, group_active=500):
   ldap_conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
   ldap_conn.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)

   groups = get_groups(ldap_conn)
   members = get_users_in_group(ldap_conn, group_active)
   
   ldap_conn.unbind_s()
   return render(request,'dashboard/dashboard.html', context={'groups':groups, 'members':members, 'active':group_active})