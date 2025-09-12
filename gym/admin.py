from django.contrib import admin
from .models import User,MembershipPass,GymVisit
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username','email','first_name','last_name','role','is_active','created_at')
    list_filter = ('role','is_active','created_at')
    search_fields=('username','email','first_name','last_name')
    ordering=('-created_at',)
    readonly_fields = ('created_at','updated_at')
    
@admin.register(MembershipPass)
class MembershipPassAdmin(admin.ModelAdmin):
    list_display = ('client','membership_type','start_date','end_date','is_active')
    list_filter=('membership_type','is_active','start_date','end_date')
    search_fields=('client__username','client__email','client__first_name','client__last_name')
    ordering =('-created_at',)
    readonly_fields = ('created_at',)
    
@admin.register(GymVisit)
class GymVisitAdmin(admin.ModelAdmin):
    list_display = ('client','visit_date')
    list_filter= ('visit_date','membership_pass__membership_type','membership_pass__is_active')
    search_fields = ('client__username','client__first_name','client__last_name')
    ordering = ('-visit_date',)
    readonly_fields = ('client','visit_date','membership_pass')
    
admin.site.site_header="Gym Management System"
admin.site.site_title ="Gym Admin"