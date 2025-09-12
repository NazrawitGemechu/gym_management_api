from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, MembershipPass, GymVisit

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id','email','first_name','last_name',
            'role','phone_no','address','created_at','updated_at','is_active'
        ]
        read_only_fields = ['id','created_at','updated_at']
         
    def create(self,validated_data):
        email = validated_data.get('email')
        validated_data['username'] = email
        password = validated_data.pop('password',None)
        if not password:
            last_name = validated_data.get('last_name')
            if last_name:
                password = last_name.replace(" ","").lower()
            else:
                password = User.objects.make_random_password(length=8)
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
        
    def update(self, instance,validated_data):
        password = validated_data.pop('password',None)
        
        instance = super().update(instance, validated_data)

        if password:
            instance.set_password(password)
            instance.save()

        return instance
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required = True) 
    new_password = serializers.CharField(required = True,validators=[validate_password])
    new_password_confirm = serializers.CharField(required = True) 
    
    def validate(self,data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("New passwords must match.")
        return data
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email','first_name','last_name','role']
        
class MembershipPassSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source = 'client.email',read_only= True)
    days_remaining = serializers.SerializerMethodField()
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = MembershipPass
        fields = [
            'id','client', 'client_name','membership_type','start_date',
            'end_date','is_active','created_at','days_remaining','is_valid'
        ]
        read_only_fields = ['id','created_at','end_date']
        
    def get_days_remaining(self,obj):
        return obj.days_remaining()
    def get_is_valid(self,obj):
        return obj.is_valid()
    
    def validate_client(self,value):
        if not value.is_client():
            raise serializers.ValidationError("Only clients can have membership passes.")
        return value
class GymVisitSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source = 'client.email',read_only=True)
    membership_type = serializers.CharField(source='membership_pass.membership_type',read_only = True)
    
    class Meta:
        model = GymVisit
        fields = [
            'id','client','client_name','visit_date',
            'membership_pass','membership_type'
        ]
        read_only_fields = ['id','visit_date','client']
        
class MembershipInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipPass
        fields = ['id', 'membership_type', 'start_date', 'end_date']

class GymVisitHistorySerializer(serializers.ModelSerializer):
    membership_info = MembershipInfoSerializer(source='membership_pass', read_only=True)
    class Meta:
        model = GymVisit
        fields = ['id', 'client', 'membership_pass', 'visit_date', 'membership_info']
    

class AssignCoachSerializer(serializers.Serializer):
    coach = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='coach'))
    
class ClientCoachSerializer(serializers.ModelSerializer):
    coach = serializers.CharField(source = 'coach.email',allow_null = True)
    
    class Meta:
        model = User
        fields = ['username','coach']

class CoachWithClientsSerializer(serializers.ModelSerializer):
    clients = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['username','clients']
        
    def get_clients(self,obj):
        return [c.email for c in obj.clients.all()]