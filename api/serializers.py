from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from .models import Hotel, Rate, Room, Inventory


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = "__all__"


class RoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Room
        fields = "__all__"

    def to_representation(self, instance):
        rep = super(RoomSerializer, self).to_representation(instance)
        rep['hotel'] = instance.hotel.code
        return rep


class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = "__all__"

    def to_representation(self, instance):
        rep = super(RateSerializer, self).to_representation(instance)
        rep['room'] = instance.room.code
        return rep


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = "__all__"

    def to_representation(self, instance):
        rep = super(InventorySerializer, self).to_representation(instance)
        rep['rate'] = instance.rate.code
        return rep
