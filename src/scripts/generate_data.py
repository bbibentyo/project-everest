#!/usr/bin/python
"""
Script used to generate random sensor data
"""
import datetime
import pprint
import random

import click
import requests


def _generate_random_ids(count):
    """Generate random device ID's in hexadecimal format, starting from 0x01 up to 0xff"""
    return [hex(i) for i in range(1, count)]


def _generate_time_series(from_date=None, to_date=None):
    end_date = to_date or datetime.datetime.now()
    beginning_date = from_date or end_date - datetime.timedelta(hours=48)
    diff = end_date - beginning_date
    half_hours_elapsed = int(diff.total_seconds() / (30 * 60))  # get elapsed time in 30 minute increments
    date_time_format = '%Y-%m-%d %H:%M'
    return [(from_date + datetime.timedelta(minutes=30*x)).strftime(date_time_format)
            for x in range(half_hours_elapsed)]


def _generate_random_color_codes(count):
    colors = set()
    while True:
        color = '#{:06x}'.format(random.randint(0, 256**3))
        colors.add(color)
        if len(colors) == count:
            break
        else:
            print(f'{len(colors)}/{count}')
    return colors


def _generate_device_data(count=5):
    device_names = _generate_random_ids(count)
    device_colors = _generate_random_color_codes(count)
    return [{'name': x[0], 'color': x[1]} for x in zip(device_names, device_colors)]


def _generate_neighbor_info(device_names):
    return [dict(name=device_name, distance=random.randint(1, 20))
            for device_name in device_names]


def _generate_random_data(device, from_date=None, to_date=None, neighbors=None):
    time_series = _generate_time_series(from_date=from_date, to_date=to_date)
    results = []
    for ts in time_series:
        data = dict(name=device['name'], temperature=random.randint(10, 40),
                    humidity=random.randint(0, 60), date=ts)
        if neighbors:
            data['neighbors'] = _generate_neighbor_info(neighbors)
        results.append(data)
    return results


def post_sensor_identifier(data, token):
    url = "http://localhost:8000/api/sensors/"
    payload = dict(identifier=data['name'], color=data['color'])
    results = requests.post(url, json=payload, headers={'Authorization': f'Token {token}'})
    pprint.pp(results.json())
    print('-' * 20)


def post_sensor_readings(data, token):
    url = "http://localhost:8000/api/remote/upload/"
    results = requests.post(url, json=data, headers={'Authorization': f'Token {token}'})
    if results.status_code != 201:
        print('error')
        pprint.pp(results.json())
    else:
        print('successfully loaded')


@click.command()
@click.argument('token')
@click.option('-d', '--device-count', 'device_count', default=10)
@click.option('-t', '--to-date', 'to_date', help="end date in format: YYYYMMDD")
@click.option('-f', '--from-date', 'from_date', help="start date in format: YYYYMMDD")
def main(from_date, to_date, device_count, token):
    devices = _generate_device_data(device_count)
    device_names = set(x['name'] for x in devices)
    if from_date:
        from_date = datetime.datetime.strptime(from_date, '%Y%m%d')
    if to_date:
        to_date = datetime.datetime.strptime(to_date, '%Y%m%d')

    for device in devices:
        post_sensor_identifier(device, token)

    for device in devices:
        other_devices = [x for x in device_names if x != device['name']]
        neighbors = random.sample(other_devices, random.randint(1, 5))  # each will have 3 neighbors
        device_data = _generate_random_data(device, from_date=from_date, to_date=to_date, neighbors=neighbors)
        pprint.pp(device_data)
        post_sensor_readings(device_data, token)
        print(f"posted {len(device_data)} records")


if __name__ == "__main__":
    main()
