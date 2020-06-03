from argparse import ArgumentParser
from mongoengine import connect

from loader.load_openflight_data import load_openflight_data


def main(args):
    if args.mode == 'load':
        if args.locations_data is None or args.routes_data is None:
            print('Loacations or Route path not provided')
            return

        db, username, password = 'flights', 'root', 'strongpassword'
        connect(
            db=db,
            host=f'mongodb://{username}:{password}@localhost:27017/?authSource=admin'
        )
        load_openflight_data(args.locations_data, args.routes_data)


if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('-m', '--mode', choices=['load'])

    # Model Dump related
    ap.add_argument('--locations-data', default=None,
                    help='Path to the file with locations data')
    ap.add_argument('--routes-data', default=None,
                    help='Path to the file with routes data')

    main(ap.parse_args())
