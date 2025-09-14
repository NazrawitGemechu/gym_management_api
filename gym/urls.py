from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users',views.UserViewSet)
router.register(r'membership-passes',views.MembershipPassViewSet)
router.register(r'gym-visits',views.GymVisitViewSet)
router.register(r'dashboard',views.DashboardViewSet,basename='dashboard')



urlpatterns = [
    path('',include(router.urls)),
    path('auth/login/',views.login,name='login'),
]