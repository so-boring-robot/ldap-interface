# ldap-interface
LDAP adaptive interface for administration programmed in Django

----------------------------------

### Install prerequisites
---
``` bash
apt install libsasl2-dev libldap2-dev libssl-dev
```

### Setup required variables
---
1.  Create and use a virtual environment
``` bash
python3 -m venv .venv
source .venv/bin/activate
pip instal -r requirements.txt
```
2.  Create a .env file inside the project folder and setup necessary variables
``` bash
nano .env
```
``` bash
AUTH_LDAP_SERVER_URI = "ldap://127.0.0.1"
AUTH_LDAP_BASE_DN = 'dc=example,dc=com'
AUTH_LDAP_BIND_DN = "cn=admin,dc=example,dc=com"
AUTH_LDAP_BIND_PASSWORD = "aroot"
```
3.  Migrate elements from database
``` bash
python3 manage.py migrate
```
4.  Create an admin account
``` bash
python3 manage.py createsuperuser
```
5.  Check if everything's alright by running the test server
``` bash
python3 manage.py runserver
```
6. Then go to [127.0.0.1:8000/](127.0.1:8000/) and enjoy !