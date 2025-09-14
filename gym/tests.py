import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from gym.models import User, MembershipPass


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin(db):
    return User.objects.create_user(
        username="admin@test.com",
        email="admin@test.com",
        password="adminpass",
        role="administrator",
    )


@pytest.fixture
def coach(db):
    return User.objects.create_user(
        username="coach@test.com",
        email="coach@test.com",
        password="coachpass",
        role="coach",
    )


@pytest.fixture
def client_user(db):
    return User.objects.create_user(
        username="client@test.com",
        email="client@test.com",
        password="clientpass",
        role="client",
    )


@pytest.mark.django_db
def test_admin_can_assign_coach(api_client, admin, client_user, coach):
    api_client.force_authenticate(user=admin)

    url = reverse("user-assign-coach", kwargs={"pk": client_user.pk})
    response = api_client.post(url, {"coach": coach.id})

    assert response.status_code == 200
    client_user.refresh_from_db()
    assert client_user.coach == coach


@pytest.mark.django_db
def test_assign_membership(api_client, admin, client_user):
    api_client.force_authenticate(user=admin)

    url = reverse("membershippass-assign-membership")
    response = api_client.post(url, {
        "client": client_user.id,
        "membership_type": "month",
        "start_date": timezone.now().date(),
        "is_active": True,
    })

    assert response.status_code == 201
    assert response.data["membership"]["membership_type"] == "month"
    assert response.data["membership"]["client"] == client_user.id


@pytest.mark.django_db
def test_client_checkin_with_active_membership(api_client, admin, client_user):

    api_client.force_authenticate(user=admin)
    assign_url = reverse("membershippass-assign-membership")
    api_client.post(assign_url, {
        "client": client_user.id,
        "membership_type": "month",
        "start_date": timezone.now().date(),
        "is_active": True,
    })

    api_client.force_authenticate(user=client_user)
    url = reverse("gymvisit-checkin")
    response = api_client.post(url)

    assert response.status_code == 201
    assert "Check-in successful" in response.data["message"]


@pytest.mark.django_db
def test_admin_can_revoke_membership(api_client, admin, client_user):
    api_client.force_authenticate(user=admin)
    assign_url = reverse("membershippass-assign-membership")
    response = api_client.post(assign_url, {
        "client": client_user.id,
        "membership_type": "month",
        "start_date": timezone.now().date(),
        "is_active": True,
    })
    membership_id = response.data["membership"]["id"]

    revoke_url = reverse("membershippass-revoke", kwargs={"pk": membership_id})
    revoke_response = api_client.post(revoke_url)

    assert revoke_response.status_code == 200
    membership = MembershipPass.objects.get(id=membership_id)
    assert membership.is_active is False
