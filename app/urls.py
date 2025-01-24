# reservations/urls.py
from django.urls import path
from .views import *
# from .swagger import schema_view


urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register_user'),
    path('login/', LoginView.as_view(), name='login_view'),
    path('logout/', LogoutView.as_view(), name='logout_view'),
    path('tables/avaliable/', AvailableTablesView.as_view(), name='list_tables'),
    path('tables/all/', AllTablesView.as_view(), name='all_tables'),


    path('reservation/<int:table_id>/', CreateReservationView.as_view(), name='create_reservation'),
    path('reservations/cancel/<int:reservation_id>/', CancelReservationView.as_view(), name='cancel-reservation'),

    path('waitlist/join/<int:table_id>/', WaitlistView.as_view(), name='add_to_waitlist'),
    path('reservations/', ListReservationsView.as_view(), name='list_reservations'),
    path('insights/', ReservationInsightsView.as_view(), name='reservation_insights'),



]
