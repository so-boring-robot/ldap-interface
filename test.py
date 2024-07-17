import ldap 

AUTH_LDAP_SERVER_URI = "ldap://192.168.3.233"
SECRET_KEY = 'django-insecure-qsg74f%9uf#(az2sp&v5b-=4em)06%9n4pzal9%8^5c#ia3&04'
AUTH_LDAP_BASE_DN = 'dc=example,dc=com'
AUTH_LDAP_BIND_DN = "cn=admin,dc=example,dc=com"
AUTH_LDAP_BIND_PASSWORD = "aroot"
#AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,dc=example,dc=com", ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

def get_groups(connection):
   # Construire le DN de base pour la recherche des utilisateurs
   base_dn = AUTH_LDAP_BASE_DN
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

try:
    ldap_conn = ldap.initialize(AUTH_LDAP_SERVER_URI)
    ldap_conn.simple_bind_s(AUTH_LDAP_BIND_DN, AUTH_LDAP_BIND_PASSWORD)
    print("Connexion établie.")
    print(get_groups(ldap_conn))
except: 
    print("Connexion échouée.")