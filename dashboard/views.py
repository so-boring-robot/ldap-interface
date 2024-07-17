from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings 
from ldap.modlist import addModlist
from dashboard.forms import PosixGroupForm, MemberForm, BulkAccountForm, EditMemberForm
from .utils import *
import ldap 
import hashlib
import csv
import io
import pandas as pd


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

def add_user_page(request, group_active):
   try:
      ldap_conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
      ldap_conn.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
      users_uidNumber = [int(user['uidNumber']) for user in get_users_in_group(ldap_conn, group_active)]
      users_uidNumber.sort()
      new_default_uidNumber = users_uidNumber[-1:][0]+1
      form = MemberForm(default_uidNumber=new_default_uidNumber, default_gidNumber=group_active)
      if request.method=='POST':
         form = MemberForm(request.POST, default_uidNumber=new_default_uidNumber, default_gidNumber=group_active)
         if form.is_valid():
            uidNumber = form.cleaned_data['uidNumber']
            gidNumber = request.POST['gidNumber']
            sn = form.cleaned_data['sn']
            givenName = form.cleaned_data['givenName']
            mail = form.cleaned_data['mail']
            password_1 = hash_password_md5(form.cleaned_data['password_1']) 
            add_user(ldap_conn, group_active, sn, givenName, mail, password_1, gidNumber, uidNumber)
            ldap_conn.unbind_s()
            return redirect('dashboard', group_active)
            
   except ldap.LDAPError as e:
      print(f"Erreur lors de l'ajout du groupe : {e}")
      return redirect('dashboard', group_active)
      
   return render(request,'dashboard/add_user.html', context={'form':form, 'active':group_active})
   
@login_required
def delete_user(request, group_active, uid):
   try:
      ldap_conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
      ldap_conn.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
      
      base_dn = settings.AUTH_LDAP_BASE_DN
      user_dn = f"uid={uid},{base_dn}"

      # Supprimer l'utilisateur
      ldap_conn.delete_s(user_dn)
      
      ldap_conn.unbind_s()

      print(f"Utilisateur {uid} supprimé avec succès.")
   except ldap.NO_SUCH_OBJECT:
      ldap_conn.unbind_s()
      print(f"L'utilisateur avec UID {uid} n'existe pas.")
   except ldap.LDAPError as e:
      ldap_conn.unbind_s()
      print(f"Erreur lors de la suppression de l'utilisateur {uid} : {e}")
   
   return redirect('dashboard', group_active)

def edit_user_page(request, uid):
   ldap_conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
   try:
      ldap_conn.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)

      user = get_user(ldap_conn, uid)
      form = EditMemberForm(uid=user['uid'],cn=user['cn'],sn=user['sn'],givenName=user['givenName'],mail=user['mail'],gidNumber=user['gidNumber'],uidNumber=user['uidNumber'],homeDirectory=user['homeDirectory'],loginShell=user['loginShell'])
      if request.method == 'POST':
         form = EditMemberForm(request.POST, uid=user['uid'],cn=user['cn'],sn=user['sn'],givenName=user['givenName'],mail=user['mail'],gidNumber=user['gidNumber'],uidNumber=user['uidNumber'],homeDirectory=user['homeDirectory'],loginShell=user['loginShell'])
         if form.is_valid():
            new_uid = request.POST['uid']
            changes = {
               'uid':[uid.encode('utf-8')],
               'cn':[request.POST['cn'].encode('utf-8')],
               'sn':[request.POST['sn'].encode('utf-8')],
               'givenName':[request.POST['givenName'].encode('utf-8')],
               'mail':[request.POST['mail'].encode('utf-8')],
               'gidNumber':[request.POST['gidNumber'].encode('utf-8')],
               'uidNumber':[request.POST['uidNumber'].encode('utf-8')],
               'homeDirectory':[request.POST['homeDirectory'].encode('utf-8')],
               'loginShell':[request.POST['loginShell'].encode('utf-8')],
            }
            edit_user(ldap_conn, uid, new_uid, changes)
            return redirect('dashboard', 500)
      return render(request, 'dashboard/edit_user.html', context={'form':form})
   except ldap.LDAPError as e:
      print(f"Erreur lors de la modification : {e}")
      return redirect('dashboard', 500) 

def add_bulk_users(request, group_active):
   form = BulkAccountForm()
   if request.method == 'POST':
      ldap_conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
      ldap_conn.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
      users_uidNumber = [int(user['uidNumber']) for user in get_users_in_group(ldap_conn, group_active)]
      users_uidNumber.sort()
      new_default_uidNumber = users_uidNumber[-1:][0]+1
      print(request.POST)
      for filename, file in request.FILES.items():
         file = request.FILES[filename] 
      users = pd.read_csv(io.StringIO(file.read().decode('utf-8')), delimiter=',')
      password_1 = hash_password_md5('root') 
      users = users.reset_index()
      for index, row in users.iterrows():
         add_user(ldap_conn, group_active, row['Prenom'], row['Nom'], row['Mail'], password_1, group_active, new_default_uidNumber)
         new_default_uidNumber += 1
         
   return render(request, 'dashboard/add_bulk_users.html', context={'form':form})

@login_required
def dashboard(request, group_active=500):
   ldap_conn = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
   ldap_conn.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
   groups = get_groups(ldap_conn)
   members = get_users_in_group(ldap_conn, group_active)
   ldap_conn.unbind_s()
   return render(request,'dashboard/dashboard.html', context={'groups':groups, 'members':members, 'active':group_active})