import base64
import json
from datetime import datetime

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import HTTP_HEADER_ENCODING, status
from rest_framework.test import APITestCase

from api.filters import avaliability_rooms_by_hotel_code
from api.models import Hotel, Room, Rate, Inventory


class AvaliabilityRoomsByHotelCodeTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """ hotels
        | name    | code |
        | hotel 1 | h1   |
        | hotel 2 | h2   |
        """
        h1 = cls._build_table_hotel('hotel 1', 'h1')
        h2 = cls._build_table_hotel('hotel 2', 'h2')
        """ rooms
        | name   | code | hotel code |
        |room 1  | ro1  | h1         |
        |room 2  | ro2  | h1         |
        |room 3  | ro3  | h1         |
        |room 4  | ro4  | h2         |
        |room 5  | ro5  | h2         |
        """
        ro1 = cls._build_table_room('room 1', 'ro1', h1)
        ro2 = cls._build_table_room('room 2', 'ro2', h1)
        ro3 = cls._build_table_room('room 3', 'ro3', h1)
        ro4 = cls._build_table_room('room 4', 'ro4', h2)
        """ rates
        | name   | code | room code |
        | rate 1 | rt1  | ro1       |
        | rate 2 | rt2  | ro1       |
        | rate 2 | rt3  | ro2       |
        | rate 2 | rt4  | ro3       |
        | rate 2 | rt5  | ro4       |
        """
        cls.rt1 = cls._build_table_rate('rate 1', 'rt1', ro1)
        cls.rt2 = cls._build_table_rate('rate 2', 'rt2', ro1)
        cls.rt3 = cls._build_table_rate('rate 2', 'rt3', ro2)
        cls.rt4 = cls._build_table_rate('rate 2', 'rt4', ro3)
        cls.rt5 = cls._build_table_rate('rate 2', 'rt5', ro4)

    @classmethod
    def _build_table_hotel(self, name, code):
        return Hotel.objects.create(name=name, code=code)

    @classmethod
    def _build_table_room(self, name, code, hotel):
        return Room.objects.create(name=name, code=code, hotel=hotel)

    @classmethod
    def _build_table_rate(self, name, code, room):
        return Rate.objects.create(name=name, code=code, room=room)

    @classmethod
    def _build_table_inventory(self, price, cupo, date, rate):
        return Inventory.objects.create(price=price, cupo=cupo, date=date, rate=rate)

    def test_inventory_match_with_dates_in_same_rate_ok(self):
        """ inventories
        | price | cupo | date       | rate |
        | 10    | 3    | 2021-01-01 | rt1  |
        | 5.5   | 1    | 2021-01-02 | rt1  |
        | 9.5   | 4    | 2021-01-03 | rt1  |
        | 7     | 2    | 2021-01-03 | rt2  |
        """
        self._build_table_inventory(10, 3, datetime(2021, 1, 1), self.rt1)
        self._build_table_inventory(5.5, 1, datetime(2021, 1, 2), self.rt1)
        self._build_table_inventory(9.5, 4, datetime(2021, 1, 3), self.rt1)
        self._build_table_inventory(7, 2, datetime(2021, 1, 3), self.rt2)

        hotel_code = 'h1'
        check_in_date = '20210101'
        check_out_date = '20210103'

        data = avaliability_rooms_by_hotel_code(hotel_code, check_in_date, check_out_date)

        expected = {
            'rooms':
                [{
                    'ro1': {
                        'rates': [{
                            'rt1': {
                                'total_price': 25.0,
                                'breakdown':
                                    [{
                                        '2021-01-01': {'price': 10.0, 'allotment': 3},
                                        '2021-01-02': {'price': 5.5, 'allotment': 1},
                                        '2021-01-03': {'price': 9.5, 'allotment': 4}
                                    }]
                            }
                        }]
                    }
                }]
        }

        self.assertEqual(expected, data)

    def test_inventory_no_match_with_date_ko(self):
        """ inventories
        | price | cupo | date       | rate |
        | 10    | 3    | 2021-01-01 | rt1  |
        | 5.5   | 1    | 2021-01-02 | rt1  |
        | 9.5   | 4    | 2021-01-03 | rt1  |
        | 7     | 2    | 2021-01-03 | rt2  |
        """
        self._build_table_inventory(10, 3, datetime(2021, 1, 1), self.rt1)
        self._build_table_inventory(5.5, 1, datetime(2021, 1, 2), self.rt1)
        self._build_table_inventory(9.5, 4, datetime(2021, 1, 3), self.rt1)
        self._build_table_inventory(7, 2, datetime(2021, 1, 3), self.rt2)

        hotel_code = 'h1'
        check_in_date = '20210104'
        check_out_date = '20210105'

        data = avaliability_rooms_by_hotel_code(hotel_code, check_in_date, check_out_date)

        expected = {'error': 'There is no inventory'}

        self.assertEqual(expected, data)

    def test_inventory_hotel_not_exist_ko(self):
        """ inventories
        | price | cupo | date       | rate |
        | 10    | 3    | 2021-01-01 | rt1  |
        | 5.5   | 1    | 2021-01-02 | rt1  |
        | 9.5   | 4    | 2021-01-03 | rt1  |
        | 7     | 2    | 2021-01-03 | rt2  |
        """
        self._build_table_inventory(10, 3, datetime(2021, 1, 1), self.rt1)
        self._build_table_inventory(5.5, 1, datetime(2021, 1, 2), self.rt1)
        self._build_table_inventory(9.5, 4, datetime(2021, 1, 3), self.rt1)
        self._build_table_inventory(7, 2, datetime(2021, 1, 3), self.rt2)

        hotel_code = 'h99999'
        check_in_date = '20210101'
        check_out_date = '20210103'

        data = avaliability_rooms_by_hotel_code(hotel_code, check_in_date, check_out_date)

        expected = {'error': 'There is no inventory'}

        self.assertEqual(expected, data)

    def test_inventory_check_in_gt_check_out_ko(self):
        """ inventories
        | price | cupo | date       | rate |
        | 10    | 3    | 2021-01-01 | rt1  |
        | 5.5   | 0    | 2021-01-02 | rt1  |
        | 9.5   | 4    | 2021-01-03 | rt1  |
        | 7     | 2    | 2021-01-03 | rt2  |
        """
        self._build_table_inventory(10, 3, datetime(2021, 1, 1), self.rt1)
        self._build_table_inventory(5.5, 1, datetime(2021, 1, 2), self.rt1)
        self._build_table_inventory(9.5, 4, datetime(2021, 1, 3), self.rt1)
        self._build_table_inventory(7, 2, datetime(2021, 1, 3), self.rt2)

        hotel_code = 'h1'
        check_in_date = '20210103'
        check_out_date = '20210102'

        data = avaliability_rooms_by_hotel_code(hotel_code, check_in_date, check_out_date)

        expected = {'error': 'check-out date < check-in date'}

        self.assertEqual(expected, data)

    def test_inventory_check_in_invalid_date_ko(self):
        """ inventories
        | price | cupo | date       | rate |
        | 10    | 3    | 2021-01-01 | rt1  |
        | 5.5   | 0    | 2021-01-02 | rt1  |
        | 9.5   | 4    | 2021-01-03 | rt1  |
        | 7     | 2    | 2021-01-03 | rt2  |
        """
        self._build_table_inventory(10, 3, datetime(2021, 1, 1), self.rt1)
        self._build_table_inventory(5.5, 1, datetime(2021, 1, 2), self.rt1)
        self._build_table_inventory(9.5, 4, datetime(2021, 1, 3), self.rt1)
        self._build_table_inventory(7, 2, datetime(2021, 1, 3), self.rt2)

        hotel_code = 'h1'
        check_in_date = '20210231'
        check_out_date = '20210102'

        data = avaliability_rooms_by_hotel_code(hotel_code, check_in_date, check_out_date)

        expected = {'error': 'Invalid date'}

        self.assertEqual(expected, data)

    def test_inventory_check_out_invalid_date_ko(self):
        """ inventories
        | price | cupo | date       | rate |
        | 10    | 3    | 2021-01-01 | rt1  |
        | 5.5   | 0    | 2021-01-02 | rt1  |
        | 9.5   | 4    | 2021-01-03 | rt1  |
        | 7     | 2    | 2021-01-03 | rt2  |
        """
        self._build_table_inventory(10, 3, datetime(2021, 1, 1), self.rt1)
        self._build_table_inventory(5.5, 1, datetime(2021, 1, 2), self.rt1)
        self._build_table_inventory(9.5, 4, datetime(2021, 1, 3), self.rt1)
        self._build_table_inventory(7, 2, datetime(2021, 1, 3), self.rt2)

        hotel_code = 'h1'
        check_in_date = '20210101'
        check_out_date = '20210231'

        data = avaliability_rooms_by_hotel_code(hotel_code, check_in_date, check_out_date)

        expected = {'error': 'Invalid date'}

        self.assertEqual(expected, data)

    def test_inventory_cupo_with_0_ko(self):
        """ inventories
        | price | cupo | date       | rate |
        | 10    | 3    | 2021-01-01 | rt1  |
        | 5.5   | 0    | 2021-01-02 | rt1  |
        | 9.5   | 4    | 2021-01-03 | rt1  |
        | 7     | 2    | 2021-01-03 | rt2  |
        """
        self._build_table_inventory(10, 3, datetime(2021, 1, 1), self.rt1)
        self._build_table_inventory(5.5, 0, datetime(2021, 1, 2), self.rt1)
        self._build_table_inventory(9.5, 4, datetime(2021, 1, 3), self.rt1)
        self._build_table_inventory(7, 2, datetime(2021, 1, 3), self.rt2)

        hotel_code = 'h1'
        check_in_date = '20210101'
        check_out_date = '20210103'

        data = avaliability_rooms_by_hotel_code(hotel_code, check_in_date, check_out_date)

        expected = {'error': 'There is no inventory'}

        self.assertEqual(expected, data)
