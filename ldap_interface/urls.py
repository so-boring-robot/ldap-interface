"""
URL configuration for ldap_interface project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import authentification.views
import dashboard.views
import schema.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', authentification.views.home, name="login"),
    path('logout/', authentification.views.logout_user, name='logout'),
    path('dashboard/<int:group_active>/', dashboard.views.dashboard, name="dashboard"),
    path('add_posix_group/', dashboard.views.add_posix_group, name='add_posix_group'),
    path('add_user/<int:group_active>', dashboard.views.add_user_page, name='add_user'),
    path('add_bulk_users/<int:group_active>', dashboard.views.add_bulk_users, name='add_bulk_users'),
    path('delete_user/<int:group_active>/<slug:uid>/', dashboard.views.delete_user, name='delete_user'),
    path('edit_user/<slug:uid>/', dashboard.views.edit_user_page, name='edit_user'),
    path('schema/dashboard/', schema.views.dashboard, name='schema_dashboard'),
    path('schema/add_schema/', schema.views.add_schema, name='add_schema'),
]
