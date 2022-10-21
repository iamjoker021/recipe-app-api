"""
URL mapping for user API
"""
from django.urls import path

import user.views


app_name = 'user'

urlpatterns = [
    path('create/', user.views.CreateUserView.as_view(), name="create"),
]
