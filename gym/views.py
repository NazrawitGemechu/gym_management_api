from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action,api_view,permission_classes
from rest_framework.response import Response
from .models import User, MembershipPass, GymVisit
from .serializers import ChangePasswordSerializer,AssignCoachSerializer,UserSerializer, UserListSerializer,MembershipPassSerializer,GymVisitSerializer,GymVisitHistorySerializer,ClientCoachSerializer,CoachWithClientsSerializer
from .permissions import IsAdministrator,IsOwnerOrAdmin,IsClient,IsCoach
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404 

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email=request.data.get('email')
    password= request.data.get('password')
    user = authenticate(username=email,password=password)
    if user:
        access = str(AccessToken.for_user(user))
        return Response({
            'access':access
        },status=status.HTTP_200_OK)
    return Response({
        'error':'Invalid Credentials'
    },status=status.HTTP_401_UNAUTHORIZED)
    
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAdministrator]
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        if self.action == 'assign_coach':
            return AssignCoachSerializer
        if self.action == 'change_password':
            return ChangePasswordSerializer
        return UserSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsOwnerOrAdmin])
    def change_password(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
           
            if not user.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.data.get("new_password"))
            user.save()
            return Response({"status": "password set"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True,methods=['post'],permission_classes=[IsAdministrator])
    def assign_coach(self,request,pk=None):
        client = self.get_object()
        if not client.is_client():
            return Response(
                {'error':'Coach can only be assigned to clients'},
                status = status.HTTP_400_BAD_REQUEST
            )
        serializer = AssignCoachSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  
        coach = serializer.validated_data['coach']
        client.coach = coach
        client.save()
        return Response(
            {'message':f"Coach {coach.email} assigned to client' {client.email}"},
            status=status.HTTP_200_OK
        )
        
    @action(detail= False,methods=['get'],permission_classes=[IsAdministrator])
    def clients_with_coaches(self,request):
        clients = User.objects.filter(role='client').select_related('coach')
        serializer = ClientCoachSerializer(clients,many=True)
        return Response(serializer.data)
    
    @action(detail=True,methods=['get'],permission_classes=[IsAdministrator | IsCoach])
    def coach_with_clients(self,request,pk=None):
        try:
            coach = User.objects.prefetch_related('clients').get(id=pk, role='coach')
        except User.DoesNotExist:
            return Response(
                {'error':'Coach not found'},
                 status= status.HTTP_404_NOT_FOUND
                )
        if request.user.is_coach() and request.user != coach:
            return Response(
                {'error':'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = CoachWithClientsSerializer(coach)
        return Response(serializer.data)
class MembershipPassViewSet(viewsets.ModelViewSet):
    queryset = MembershipPass.objects.all()
    serializer_class = MembershipPassSerializer
    permission_classes= [IsAdministrator]
    
    @action(detail=False, methods=['post'], permission_classes=[IsAdministrator])
    def assign_membership(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        membership = serializer.save() 
        return Response({
            'message': f'Membership assigned to {membership.client.email}',
            'membership': serializer.data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True,methods=['post'],permission_classes=[IsAdministrator])
    def revoke(self,request,pk=None):
        membership_pass = self.get_object()
        if not membership_pass.is_active:
            return Response(
                {'error': 'Membership is already inactive'},
                status = status.HTTP_400_BAD_REQUEST
            )
        membership_pass.is_active = False
        membership_pass.save()
        return Response(
            {'message': 'Membership pass revoked successfully'},
            status = status.HTTP_200_OK
        )
    @action(detail=False,methods =['get'],permission_classes=[IsClient])
    def my_memberships(self,request):
        memberships = self.get_queryset().select_related('client').filter(client=request.user)
        serializer = self.get_serializer(memberships,many=True)
        return Response(serializer.data)

class GymVisitViewSet(viewsets.ModelViewSet):
    queryset = GymVisit.objects.all()
    serializer_class = GymVisitSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = GymVisit.objects.select_related(
            'client','membership_pass'
        ).order_by('-visit_date')
        
        if self.request.user.is_client():
            queryset = queryset.filter(client = self.request.user)
            
        elif self.request.user.is_coach():
            queryset = queryset.filter(client__coach=self.request.user)
        return queryset
    
    @action(detail = False,methods=['post'],permission_classes=[IsClient])
    def checkin(self,request):
        try:
            active_membership = MembershipPass.objects.get(
                client= request.user,
                is_active = True
            )
        except MembershipPass.DoesNotExist:
            return Response(
                {'error':'No active membership pass found'},
                status = status.HTTP_400_BAD_REQUEST
            )
            
        if not active_membership.is_valid():
            return Response(
                {'error':'Membership pass has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        visit = GymVisit.objects.create(
            client = request.user,
            membership_pass = active_membership
        )
        serializer = GymVisitSerializer(visit)
        return Response(
            {'message': 'Check-in successful',
             'visit': serializer.data
            },
            status = status.HTTP_201_CREATED
        )
    @action(detail=False,methods=['get'],permission_classes=[IsClient])
    def my_history(self,request):
        visits = self.get_queryset().filter(client=request.user)
        serializer = GymVisitHistorySerializer(visits,many= True)
        return Response(serializer.data)

        