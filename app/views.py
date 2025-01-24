
from .serializers import *
from django.utils import timezone
from django.db.models import Count
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Reservation, Table, Waitlist, CustomUser
# from drf_yasg.utils import swagger_auto_schema
# from drf_yasg import openapi


class RegisterUserView(generics.CreateAPIView):
    """
    Handle user registration by accepting email, full name, and password.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    # @swagger_auto_schema(
    #     request_body=UserRegistrationSerializer,
    #     responses={
    #         201: openapi.Response('User registered successfully.'),
    #         400: openapi.Response('Validation error occurred.'),
    #     }
    # )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutView(generics.GenericAPIView):
    """
    Logout view to blacklist a refresh token.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer  # Use the LogoutSerializer here

    # @swagger_auto_schema(
    #     request_body=LogoutSerializer,
    #     responses={
    #         200: openapi.Response('Logout successful'),
    #         400: openapi.Response('Error'),
    #     }
    # )
    def post(self, request, *args, **kwargs):
        # Use the serializer to validate the incoming data
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Get the validated refresh token
            refresh_token = serializer.validated_data['refresh']
            
            try:
                # Blacklist the refresh token
                token = RefreshToken(refresh_token)
                token.blacklist()
                
                return Response({'detail': 'Logout successful'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # If the serializer is not valid, return errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(generics.GenericAPIView):
    """
    Login view to generate JWT tokens for users.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    # @swagger_auto_schema(
    #     request_body=LoginSerializer,
    #     responses={200: openapi.Response('Login successful.'), 401: openapi.Response('Invalid credentials.')}
    # )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AvailableTablesView(generics.ListAPIView):
    """
    Retrieve a list of all available tables.
    """
    permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]
    queryset = Table.objects.filter(availability_status=True)
    serializer_class = TableSerializer

    # @swagger_auto_schema(
    #     operation_description='Retrieve a list of available tables.',
    #     tags=['Tables'],
    #     responses={200: TableSerializer(many=True)},
    # )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class AllTablesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TableSerializer
    queryset = Table.objects.all()


class CreateReservationView(generics.CreateAPIView):
    """
    Create a reservation for the authenticated user, given a table ID.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ReservationSerializer

    # @swagger_auto_schema(
    #     request_body=ReservationSerializer,
    #     responses={201: ReservationSerializer, 400: openapi.Response('Error')}
    # )
    def post(self, request, table_id, *args, **kwargs):
        table = Table.objects.get(id=table_id, availability_status=True)
        date = request.data.get('date')
        time = request.data.get('time')
        tb = request.data.get('table')

        if tb:
            raise ValueError("Table is not required in the request body.")
        

        # Check if user already has a reservation for this table at the specified time
        existing_reservation = Reservation.objects.filter(
            user=request.user, 
            table=table, 
            date=date, 
            time=time, 
            status="booked"
        ).exists()

        if existing_reservation:
            return Response({"error": "You already have a reservation for this table at the specified time."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Proceed to create the reservation
        reservation = Reservation.objects.create(
            user=request.user,
            table=table,
            date=date,
            time=time,
            status="booked"
        )

        # Mark the table as unavailable
        table.availability_status = False
        table.save()

        return Response(
            {
                "message": "Reservation created successfully.",
                "reservation": {
                    "id": reservation.id,
                    "table": reservation.table.table_number,
                    "date": reservation.date,
                    "time": reservation.time,
                },
            },
            status=status.HTTP_201_CREATED
        )


class CancelReservationView(generics.DestroyAPIView):
    """
    Cancel a reservation for the logged in user.
    """
    permission_classes = [IsAuthenticated]
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    # @swagger_auto_schema(
    #     manual_parameters=[
    #         openapi.Parameter('reservation_id', openapi.IN_PATH, description="ID of the reservation to cancel.", type=openapi.TYPE_INTEGER),
    #     ],
    #     responses={200: openapi.Response('Reservation cancelled successfully.'), 404: openapi.Response('Error')}
    # )
    def delete(self, request, reservation_id, *args, **kwargs):
        try:
            reservation = self.get_object()

            if reservation.status == "cancelled":
                return Response({"error": "This reservation is already cancelled."}, status=status.HTTP_400_BAD_REQUEST)

            reservation.status = "cancelled"
            reservation.save()

            # Mark the table as available
            table = reservation.table
            table.availability_status = True
            table.save()

            return Response({"message": "Reservation cancelled successfully."}, status=status.HTTP_200_OK)
        except Reservation.DoesNotExist:
            return Response({"error": "Reservation not found or you do not have permission to cancel it."},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WaitlistView(generics.CreateAPIView):
    """
    Add the authenticated user to the waitlist for a specific table.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = WaitlistSerializer

    # @swagger_auto_schema(
    #     request_body=WaitlistSerializer,
    #     responses={
    #         201: openapi.Response(
    #             description="Added to waitlist successfully.",
    #             examples={
    #                 "application/json": {
    #                     "message": "You have been added to the waitlist.",
    #                     "waitlist_entry": {
    #                         "id": 1,
    #                         "table": 101,
    #                         "date": "2025-01-22",
    #                         "status": "waiting"
    #                     }
    #                 }
    #             }
    #         ),
    #         400: "Bad Request: Validation error.",
    #         404: "Table not found.",
    #     },
    # )
    def post(self, request, table_id, *args, **kwargs):
        table = Table.objects.get(id=table_id)
        date = request.data.get('date')

        if not date:
            return Response({"error": "Date is required."}, status=status.HTTP_400_BAD_REQUEST)

        existing_waitlist = Waitlist.objects.filter(
            user=request.user,
            table=table,
            date=date,
            status__in=["waiting", "notified"]
        ).exists()

        if existing_waitlist:
            return Response({"error": "You are already on the waitlist for this table and date."},
                            status=status.HTTP_400_BAD_REQUEST)

        waitlist_entry = Waitlist.objects.create(
            user=request.user,
            table=table,
            date=date,
            status="waiting"
        )

        return Response(
            {
                "message": "You have been added to the waitlist.",
                "waitlist_entry": {
                    "id": waitlist_entry.id,
                    "table": table.table_number,
                    "date": waitlist_entry.date,
                    "status": waitlist_entry.status,
                },
            },
            status=status.HTTP_201_CREATED
        )


class ReservationInsightsView(generics.GenericAPIView):
    """
    Get insights like peak booking times, guest trends, and upcoming reservations for managers.
    """
    permission_classes = [IsAuthenticated]

    # @swagger_auto_schema(
    #     responses={
    #         200: openapi.Response(
    #             description="Insights for reservations.",
    #             examples={
    #                 "application/json": {
    #                     "peak_times_by_hour": [{"time": "18:00", "count": 10}],
    #                     "peak_times_by_day": [{"date": "2025-01-22", "count": 15}],
    #                     "guest_trends": [{"user": 1, "reservation_count": 5}],
    #                     "upcoming_reservations": [
    #                         {
    #                             "id": 1,
    #                             "user": 2,
    #                             "table__table_number": 101,
    #                             "date": "2025-01-22",
    #                             "time": "19:00"
    #                         }
    #                     ]
    #                 }
    #             }
    #         ),
    #         403: "Forbidden: Requires authentication and staff privileges."
    #     },
    # )
    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({'detail': 'Authentication and staff privileges required.'}, status=status.HTTP_403_FORBIDDEN)

        current_time = timezone.now()

        # Get insights for reservations
        peak_times_by_hour = Reservation.objects.filter(date__gte=current_time).values('time').annotate(
            count=Count('id')).order_by('-count')
        peak_times_by_day = Reservation.objects.filter(date__gte=current_time).values('date').annotate(
            count=Count('id')).order_by('-count')

        guest_trends = Reservation.objects.values('user').annotate(
            reservation_count=Count('id')).order_by('-reservation_count')

        upcoming_reservations = Reservation.objects.filter(date__gte=current_time.date(), time__gte=current_time.time()) \
            .order_by('date', 'time')

        insights = {
            'peak_times_by_hour': peak_times_by_hour,
            'peak_times_by_day': peak_times_by_day,
            'guest_trends': guest_trends,
            'upcoming_reservations': upcoming_reservations.values('id', 'user', 'table__table_number', 'date', 'time')
        }

        return Response(insights)




class ListReservationsView(generics.ListAPIView):
    """
    List all reservations for the logged-in user.
    """
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This method returns the reservations related to the authenticated user.
        """
        return Reservation.objects.filter(user=self.request.user)

    # @swagger_auto_schema(
    #     responses={
    #         200: ReservationSerializer(many=True),
    #         401: "Unauthorized: Authentication required."
    #     }
    # )
    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to list the reservations for the authenticated user.
        """
        # Ensures that only authenticated users can access this view.
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)

        return super().get(request, *args, **kwargs)