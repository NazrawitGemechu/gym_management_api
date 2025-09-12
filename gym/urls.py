from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users',views.UserViewSet,basename='user')
router.register(r'membership-passes',views.MembershipPassViewSet,basename='membershippass')
router.register(r'gym-visits',views.GymVisitViewSet,basename='gymvisit')



urlpatterns = [
    path('',include(router.urls)),
    path('auth/login/',views.login,name='login'),
]