mysl
====

API-wrapper for "Mitt SL"

Requirements
-------------

* requests

Usage
-----

Fetch travel-cards

    import mysl

    api = mysl.MySL(username='my_user_name', password='my_secret_password')
    api.GetTravelCards()

Fetch travel-card details

    api.GetTravelCardDetail(reference='travel_card/XXXXXXX')
