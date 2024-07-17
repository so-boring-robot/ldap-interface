# ldap-interface
LDAP adaptive interface for administration programmed in Django

----------------------------------

### Install prerequisites
---
*terminal*
``` bash
apt install libsasl2-dev libldap2-dev libssl-dev
```

### Setup required variables
---
1.  Create and use a virtual environment
*terminal*
``` bash
python3 -m venv .venv
source .venv/bin/activate
pip instal -r requirements.txt
```
2.  Create a .env file inside the project folder and setup necessary variables
*terminal*
``` bash
nano .env
```
*.env*
``` bash
AUTH_LDAP_SERVER_URI = "ldap://127.0.0.1"
AUTH_LDAP_BASE_DN = 'dc=example,dc=com'
AUTH_LDAP_BIND_DN = "cn=admin,dc=example,dc=com"
AUTH_LDAP_BIND_PASSWORD = "aroot"
```
3.  Create an admin account
*terminal*
``` bash
python3 manage.py createsuperuser
```
4.  Check if everything's alright by running the test server
*terminal*
``` bash
python3 manage.py runserver
```
4. Then go to [127.0.0.1:8000/](127.0.1:8000/) and enjoy !