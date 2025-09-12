from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
class User(AbstractUser):
    ROLE_CHOICES = [
        ('client','Client'),
        ('coach',"Coach"),
        ('administrator','Administrator',)
    ]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=15,choices=ROLE_CHOICES)
    phone_no = models.CharField(max_length = 15,blank = True)
    address = models.CharField(max_length = 50,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now = True)
    
    coach = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null = True,
        blank = True,
        limit_choices_to={'role':'coach'},
        related_name='clients'  
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    class Meta:
        indexes=[
            models.Index(fields=['role']),
            models.Index(fields=['created_at']),
        ]
    def __str__(self):
        return f"{self.username} : {self.role}"
    
    def is_client(self):
        return self.role == 'client'
    def is_coach(self):
        return self.role == 'coach'
    def is_administrator(self):
        return self.role == 'administrator'
    
class MembershipPass(models.Model):
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='membership_passes',
        limit_choices_to={'role': 'client'}
        )
    TYPE_CHOICES = [
        ('month','Monthly'),
        ('annual','Annual'),
    ]
    membership_type = models.CharField(max_length=10,choices=TYPE_CHOICES)
    start_date = models.DateField()
    end_date=models.DateField(blank = True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes =[
            models.Index(fields = ['client','is_active']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
            models.Index(fields=['membership_type'])
        ]
    def __str__(self):
        return f"{self.client.username} - {self.membership_type} ({self.start_date} to {self.end_date})"
    def save(self, *args, **kwargs):
        if self.start_date and not self.end_date:
            if self.membership_type == 'month':
                self.end_date = self.start_date + timedelta(days=30)
            elif self.membership_type == 'annual':
                self.end_date = self.start_date + timedelta(days=365)
        if self.is_active:
            MembershipPass.objects.filter(
                client = self.client,
                is_active = True
            ).exclude(pk=self.pk).update(is_active=False)
            
        super().save(*args,**kwargs)
    def is_valid(self):
        return self.is_active and self.end_date >= timezone.now().date()
    def days_remaining(self):
        if self.end_date >= timezone.now().date():
            return (self.end_date - timezone.now().date()).days
        return 0

class GymVisit(models.Model):
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name = 'gym_visits',
        limit_choices_to={'role':'client'},
        )
    visit_date = models.DateTimeField(auto_now_add=True)
    membership_pass = models.ForeignKey(
        MembershipPass,
        on_delete=models.CASCADE
    )    
    class Meta:
        indexes=[
            models.Index(fields=['client','visit_date'])
        ]
        
    def __str__(self):
        return f"{self.client.username} visited on {self.visit_date.strftime('%Y-%m-%d %H:%M')}"
    def clean(self):
        if self.membership_pass.client != self.client:
            raise ValidationError("Membership pass must belong to the visiting client")
        if not self.membership_pass.is_valid():
            raise ValidationError("Membership has expired.")
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args,**kwargs)