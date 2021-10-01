from itertools import groupby

from api.models import Inventory


def avaliability_rooms_by_hotel_code(hotel_code, checkin_date, checkout_date):
    inventories = list(Inventory.objects.select_related(
        'rate', 'rate__room', 'rate__room__hotel'
    ).filter(
        rate__room__hotel__code=hotel_code,
        date__range=(checkin_date, checkout_date)
    ).order_by('rate__room', 'rate'))

    if not inventories:
        return {'error': 'There is no inventory'}

    total_expectet_dates = (checkout_date - checkin_date).days + 1

    rooms = {}
    for room_code, group_room in groupby(inventories, lambda x: x.rate.room.code):
        rates = []
        for rate_code, group_rate in groupby(group_room, lambda x: x.rate.code):
            rate_available = True
            total_price = 0.0
            breakdown_data = {}
            for inventory in group_rate:
                total_price += inventory.price
                breakdown_data[inventory.date.strftime("%Y-%m-%d")] = {
                    'price': inventory.price, 'allotment': inventory.cupo
                }
                if not inventory.cupo:
                    rate_available = False
            if len(breakdown_data.keys()) != total_expectet_dates or not rate_available:
                continue
            rate_data = {
                'total_price': total_price,
                'breakdown': [breakdown_data]
            }
            rates.append({rate_code: rate_data})
        if not rates:
            continue
        rooms[room_code] = {'rates': rates}

        return {'rooms': [rooms]}

    return {'error': 'There is no inventory'}
