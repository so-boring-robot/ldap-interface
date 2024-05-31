from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ldap3 import Server, Connection, ALL, NTLM

@login_required
def dashboard(request):
   
   server = Server('ldap://192.168.3.228:389', get_info=ALL)
   conn = Connection(server, user="cn=admin,dc=nodomain", password="root", auto_bind=True)
   #print(conn)
   #print(server.info)
   print(conn.extend.standard.who_am_i())
   return render(request,'dashboard/dashboard.html')