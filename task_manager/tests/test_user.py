"""Test user."""

import pytest
from rest_framework.test import APIClient
from django.core.management import call_command
from django.urls import reverse_lazy
from task_manager.apps.user.models import User
from django.core import mail

client = APIClient()


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('loaddata', 'task_manager/tests/fixtures/users.yaml')


@pytest.mark.django_db
def test_create_user():
    register_url = "/api/v1/auth/users/"
    activate_url = "/api/v1/auth/users/activation/"
    login_url = "/api/v1/auth/token/login/"

    username = 'test_user'
    email = 'test@example.com'
    password = 'test_password'

    # User registration
    response = client.post(register_url, data={'username': username,
                                               'email': email,
                                               'password': password})
    assert response.status_code == 201
    assert len(mail.outbox) == 1

    # Activation check
    user = User.objects.filter(email=email).first()
    assert user.is_active is False

    response = client.get(reverse_lazy('user:list'))
    assert response.status_code == 401

    # Activation message
    text_message = mail.outbox[0].body
    link_activation = text_message.split("\n")[3]
    link_activation_list = link_activation.split('/')

    uid = link_activation_list[6]
    token = link_activation_list[7]

    # Activation
    client.post(activate_url, data={'uid': uid, 'token': token})

    # Activation check
    user = User.objects.filter(email=email).first()
    assert user.is_active is True

    # Get token
    response = client.post(login_url, data={'email': email,
                                            'password': password})

    token_login = response.data['auth_token']
    header_authorization = 'Token ' + token_login

    response = client.get(reverse_lazy('user:sample', kwargs={'pk': user.pk}))
    assert response.status_code == 401

    response = client.get(reverse_lazy('user:sample', kwargs={'pk': user.pk}),
                          HTTP_AUTHORIZATION=header_authorization)
    assert response.status_code == 200
