from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from . import serializers
from .filters import avaliability_rooms_by_hotel_code
from .models import Hotel, Rate, Room, Inventory


class HotelView(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Hotel.objects.all()
    serializer_class = serializers.HotelSerializer
    lookup_field = 'code'


class RateView(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Rate.objects.all()
    serializer_class = serializers.RateSerializer
    lookup_field = 'code'


class RoomView(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Room.objects.all()
    serializer_class = serializers.RoomSerializer
    lookup_field = 'code'


class InventoryView(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Inventory.objects.all()
    serializer_class = serializers.InventorySerializer


@method_decorator(name='get', decorator=swagger_auto_schema(
    operation_id='availability by hotel and check in/out dates',
    operation_description="Returns the hotel rooms since they have space between the dates provided"
))
class AvailabilityView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        hotel_code = kwargs.pop('hotel_code', None)
        checkin_date = kwargs.pop('checkin_date', None)
        checkout_date = kwargs.pop('checkout_date', None)

        try:
            checkin_date = datetime.strptime(checkin_date, '%Y%m%d')
            checkout_date = datetime.strptime(checkout_date, '%Y%m%d')
        except ValueError:
            return JsonResponse({'error': 'Invalid date'})

        if checkout_date < checkin_date:
            return JsonResponse({'error': 'check-out date < check-in date'})

        data = avaliability_rooms_by_hotel_code(hotel_code, checkin_date, checkout_date)

        return JsonResponse(data=data)


class RaulView(APIView):

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin:index')

        return JsonResponse(data={
            'name': 'Raul Torne',
            'linkedin': 'https://www.linkedin.com/in/raultornealonso/',
            'github': 'https://github.com/racu10',
        })
