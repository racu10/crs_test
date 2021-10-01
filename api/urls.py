from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'hotels', views.HotelView, basename='hotels')
router.register(r'rate', views.RateView, basename='rate')
router.register(r'room', views.RoomView, basename='room')
router.register(r'inventory', views.InventoryView, basename='inventory')

regex_date = '([12]\d{3}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01]))'

urlpatterns = [
    url(f'^availability/(?P<hotel_code>.+)/(?P<checkin_date>{regex_date})/(?P<checkout_date>{regex_date})/$', views.AvailabilityView.as_view(), name='availability'),
    path('', include(router.urls)),
]
