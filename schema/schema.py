from mongoengine import Document, fields


class Location(Document):
    """
    This class represents a location in the database
    """
    name = fields.StringField(required=True)
    city = fields.StringField(required=True)
    country = fields.StringField(required=True)
    iata = fields.StringField()
    icao = fields.StringField()
    location = fields.GeoPointField()
    altitude = fields.FloatField()
    timezone = fields.FloatField()
    dst = fields.StringField()
    tz = fields.StringField()

    meta = {
        'allow_inheritance': True
    }


class Airport(Location):
    pass


class TrainStation(Location):
    pass


class Port(Location):
    pass


class UnknownLocation(Location):
    pass


class Airline(Document):
    """
    This model represents an airline company
    """
    name = fields.StringField()
    alias = fields.StringField()
    iata = fields.StringField()
    icao = fields.StringField()
    callsign = fields.StringField()
    country = fields.StringField()
    active = fields.BooleanField()


class Route(Document):
    """
    This model defines a route in the world
    """
    airline = fields.ReferenceField(Airline)
    source = fields.ReferenceField(Location)
    destination = fields.ReferenceField(Location)
    codeshare = fields.BooleanField()
    stops = fields.IntField()
    equipment = fields.StringField()

    meta = {
        'allow_inheritance': True
    }


class AirRoute(Route):
    pass
