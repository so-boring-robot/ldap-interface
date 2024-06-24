import ldap
from django.conf import settings
import hashlib
import base64
import difflib

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
         users.append({'givenName': entry['givenName'][0].decode(), 'sn':entry['sn'][0].decode(), 'uid':entry['uid'][0].decode(), 'uidNumber':entry['uidNumber'][0].decode()})
   return users

def get_users(connection):
   base_dn = settings.AUTH_LDAP_BASE_DN
   search_filter = '(objectClass=*)'
   users = []
   search_attributes = []
      
   # Effectuer la recherche
   result = connection.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter, search_attributes)
   # Traiter les résultats
   for dn, entry in result:
      if entry['objectClass'][1].decode()=='posixAccount':
         users.append({'givenName': entry['givenName'][0].decode(), 'sn':entry['sn'][0].decode(), 'uid':entry['uid'][0].decode(), 'uidNumber':entry['uidNumber'][0].decode()})
   return users


def hash_password_md5(plain_password):
   # Créer un objet md5
   md5_hash = hashlib.md5()
   
   # Mettre à jour l'objet md5 avec le mot de passe en clair encodé en UTF-8
   md5_hash.update(plain_password.encode('utf-8'))
   
   # Récupérer le hash MD5 en bytes
   hash_bytes = md5_hash.digest()
   
   # Encoder le hash en base64 pour le rendre lisible
   hash_base64 = base64.b64encode(hash_bytes)
   
   # Retourner le hash formaté comme requis par LDAP
   return f'{{MD5}}{hash_base64.decode("utf-8")}'
 
def compare_strings(s1, s2):
   seq = difflib.SequenceMatcher(None, s1, s2)
   match = seq.find_longest_match(0, len(s1), 0, len(s2))
   s2_rest = s2[:match.b] + s2[match.b + match.size:]

   return s2_rest