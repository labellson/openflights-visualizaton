from mongoengine import connect
from collections import OrderedDict
from tqdm import tqdm
import pandas as pd


from schema.schema import (Location, Airport, TrainStation, Port,
                           UnknownLocation, AirRoute)


def _create_kwargs(args, dtypes, **kwargs):
    for k, v in kwargs.items():
        if v == '\\N':
            continue

        if k in dtypes:
            args[k] = dtypes[k](v)
        else:
            args[k] = v


def load_openflight_data(location_data, route_data, airline_data=None):
    location_dtypes = OrderedDict(
        airport_id=int,
        name=str,
        city=str,
        country=str,
        iata=str,
        icao=str,
        latitude=float,
        longitude=float,
        altitude=float,
        timezone=float,
        dst=str,
        tz=str,
        type=str,
    )
    location_df = pd.read_csv(location_data, names=list(location_dtypes.keys()),
                              usecols=list(range(13)))

    route_dtypes = dict(
        airline_id=int,
        source_id=int,
        destination_id=int,
        codeshare=bool,
        stops=int,
        equipment=str
    )
    route_df = pd.read_csv(route_data, names=list(route_dtypes.keys()),
                           usecols=[1, 3, 5, 6, 7, 8])

    # Dump the location to the database
    loc_dict = {}
    loc_types = {'airport': Airport, 'station': TrainStation, 'port': Port}
    for (airport_id, name, city, country, iata, icao, latitude, longitude,
         altitude, timezone, dst, tz, type_) in tqdm(
             zip(*[location_df[k] for k in location_dtypes.keys()]),
             'Dump Locations', total=len(location_df)
    ):
        kwargs = {}
        _create_kwargs(kwargs, location_dtypes, name=name, city=city,
                       country=country, iata=iata, icao=icao,
                       location=[latitude, longitude], altitude=altitude,
                       timezone=timezone, dst=dst, tz=tz)

        if latitude == '\\N' or longitude == '\\N':
            del(kwargs['location'])

        loc = loc_types.get(type_, UnknownLocation)(**kwargs)
        loc.save()
        loc_dict[airport_id] = loc

    # Replace the NaN in `codeshare` for empty strings
    route_df.fillna(value={'codeshare': ''}, inplace=True)

    # Dump the routes
    for (airline_id, source_id, destination_id, codeshare, stops, equipment) in tqdm(
            zip(*[route_df[k] for k in route_dtypes.keys()]),
            'Dump Routes', total=len(route_df)
    ):
        kwargs = {}
        _create_kwargs(kwargs, route_dtypes, codeshare=codeshare, stops=stops,
                       equipment=equipment, source_id=source_id,
                       destination_id=destination_id)

        source_id = kwargs.pop('source_id', None)
        if source_id in loc_dict:
            kwargs['source'] = loc_dict[source_id]

        destination_id = kwargs.pop('destination_id', None)
        if destination_id in loc_dict:
            kwargs['destination'] = loc_dict[destination_id]

        AirRoute(**kwargs).save()


def load_locations(path_to_data):
    location_dtypes = OrderedDict(
        airport_id=int,
        name=str,
        latitude=float,
        longitude=float,
        type=str,
    )
    df = pd.read_csv(path_to_data, names=list(location_dtypes.keys()),
                     usecols=[0, 1, 6, 7, 12])

    df[df['type'] == 'airport']
    return df


def load_routes(path_to_data):
    route_dtypes = dict(
        source_id=int,
        destination_id=int,
    )
    df = pd.read_csv(path_to_data, names=list(route_dtypes.keys()),
                     usecols=[3, 5])

    df.drop(df[df['source_id'] == '\\N'].index, inplace=True)
    df.drop(df[df['destination_id'] == '\\N'].index, inplace=True)

    return df.astype(int)


def load_routes_join(path_to_data, loc_df):
    r_df = load_routes(path_to_data)
    _loc_df = loc_df.set_index('airport_id')

    # Join the source
    r_df.set_index('source_id', inplace=True)
    r_df = r_df.join(_loc_df)

    # Join the destination
    r_df.reset_index(inplace=True, drop=True)
    r_df = r_df.join(_loc_df, rsuffix='_destination')

    return r_df.dropna()
