from django.db import models


class Hotel(models.Model):
    name = models.CharField(
        max_length=255
    )

    code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True
    )

    def __str__(self):
        return self.code


class Room(models.Model):
    name = models.CharField(
        max_length=255
    )

    code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True
    )

    hotel = models.ForeignKey('api.Hotel', on_delete=models.CASCADE)

    def __str__(self):
        return self.code


class Rate(models.Model):

    name = models.CharField(
        max_length=255
    )

    code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True
    )

    room = models.ForeignKey('api.Room', on_delete=models.CASCADE)

    def __str__(self):
        return self.code


class Inventory(models.Model):

    class Meta:
        unique_together = ('date', 'rate')

    price = models.FloatField()

    cupo = models.PositiveIntegerField()

    date = models.DateField(db_index=True)

    rate = models.ForeignKey('api.Rate', on_delete=models.CASCADE)
