import ldap
from ldap.modlist import addModlist, modifyModlist
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

def get_user(connection, uid):
   base_dn = settings.AUTH_LDAP_BASE_DN
   user_dn = f"uid={uid},{base_dn}"
   # Récupérer les attributs actuels de l'utilisateur
   result = connection.search_s(user_dn, ldap.SCOPE_BASE)
   cn = result[0][1]['cn'][0].decode()
   sn = result[0][1]['sn'][0].decode()
   givenName = result[0][1]['givenName'][0].decode()
   mail = result[0][1]['mail'][0].decode()
   gidNumber = result[0][1]['gidNumber'][0].decode()
   uidNumber = result[0][1]['uidNumber'][0].decode()
   homeDirectory = result[0][1]['homeDirectory'][0].decode()
   loginShell = result[0][1]['loginShell'][0].decode()      
   return {'uid':uid,'cn':cn, 'sn':sn,'givenName':givenName,'mail':mail,'gidNumber':gidNumber,'uidNumber':uidNumber,'homeDirectory':homeDirectory,'loginShell':loginShell,}

def add_user(connection,group_active, sn, givenName, mail, password_1, gidNumber, uidNumber):
   cn = f"{givenName} {sn}"
   uid = ''
   uid_sample = givenName[:2].lower()+sn.lower()
   members = get_users_in_group(connection, group_active)
   rest_uids = []
   current_uids = [member['uid'] for member in members]
   for i in range(len(current_uids)):
      if uid_sample in current_uids[i]:
         rest_uids.append(compare_strings(uid_sample, current_uids[i]))
   rest_uids.sort()
   if rest_uids:
      if rest_uids[-1:][0]=='':
         uid = uid_sample+'2'
      else:
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
         'mail': [mail.encode('utf-8')],
         'userPassword': [password_1.encode('utf-8')],
         'gidNumber': [str(gidNumber).encode('utf-8')],
         'uidNumber': [str(uidNumber).encode('utf-8')],
         'homeDirectory': [homeDirectory.encode('utf-8')],
         'loginShell': [loginShell.encode('utf-8')],
   }

   # Convertir les attributs en format LDAP
   ldif = addModlist(attrs)

   # Ajouter l'utilisateur
   connection.add_s(user_dn, ldif)
   
   
   
   
def edit_user(connection, uid, new_uid, changes):
   base_dn = settings.AUTH_LDAP_BASE_DN
   user_dn = f"uid={uid},{base_dn}"
   # Récupérer les attributs actuels de l'utilisateur
   result = connection.search_s(user_dn, ldap.SCOPE_BASE)
   current_attrs = result[0][1]
   changes['objectClass'] = current_attrs['objectClass']
   # Préparer les modifications
   modlist = modifyModlist(current_attrs, changes)
   # Appliquer les modifications
   connection.modify_s(user_dn, modlist)
   
   # Check if UID have to change
   if new_uid != uid:
      new_user_dn = f"uid={new_uid},{base_dn}"
      connection.rename_s(user_dn, f"uid={new_uid}")


   
   connection.unbind_s()

    

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