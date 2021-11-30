# -*- coding: utf-8 -*-
# !/usr/bin/env python
import http.client
from datetime import date, timedelta
import argparse
from btc_track.db_sqllite import DBWorker
import json
import logging
from btc_track import graph


DB_NAME = r'/db/crypto.db'
dbw = DBWorker(DB_NAME)


def api_get(method, uri):
    """Send GET request and return response"""
    logging.debug('api_get: method: ' + str(method) + ', uri: ' + str(uri))
    conn = http.client.HTTPSConnection('api.coindesk.com')
    conn.request(method, uri)
    result = conn.getresponse()
    logging.debug('api_get: result: ' + str(result))
    return result


def get_min_date(coin_name):
    """GET minimum date for coin"""
    exists_date = dbw.get_first_date(coin_name)
    if not exists_date:
        logging.debug('get_min_date: no exists_date')
        response = api_get('GET',
                           '/v1/' + coin_name + '/historical/close.json'
                                                '?start=1900-01-01'
                                                '&end=' +
                           str(date.isoformat(date.today())))
        response_data = response.read().decode()

        first_date = str(response_data[46:56])
        logging.debug('get_min_date: no exists_date: new first_date: '
                      + str(first_date))
        dbw.db_insert_first_date('bpi', start_date)
    else:
        first_date = exists_date
    logging.debug('get_min_date: return first_date: ' + str(first_date))
    return first_date


def request_api(date1: str, date2: str, coin_name: str):
    """Minimise query count from api"""
    res = api_get('GET',
                  '/v1/' + coin_name + '/historical/close.json'
                                       '?start=' + date1 +
                  '&end=' + date2)
    logging.debug('request_api: res.status: ' + str(res.status))
    if res.status == 200:
        res_data = json.loads(res.read().decode())
        res_data = res_data.get(coin_name)
        logging.debug('request_api: res_data = ' + str(res_data.items()))
        dbw.db_insert(coin_name, res_data)


def request_min_db(date1, date2, coin_name, day_delta):
    """Minimise query data from api"""
    date_list_db = list(dbw.get_data(coin_name, date1, date2))
    date_set_db = set()
    for i in date_list_db:
        date_set_db.add(str(i[0]))

    base = date.fromisoformat(start_date)
    date_list = [str(base + timedelta(days=x)) for x in
                 range(day_delta.days + 1)]
    date_set_query = set(date_list)
    date_set_query.symmetric_difference_update(date_set_db)

    date_set_list = list(date_set_query)
    date_set_list.sort()
    logging.debug('request_min_db: date_set_list:' + str(date_set_list))
    q_list = []  # query list
    list_number = 0
    last_i = str(date.fromisoformat(date1) - timedelta(2))

    for i in date_set_list:
        if date.fromisoformat(i) > date.fromisoformat(last_i) + timedelta(1):
            q_list.append([])
            q_list[list_number].append(i)
            list_number += 1

        if date.fromisoformat(i) == date.fromisoformat(last_i) + timedelta(1):
            q_list[list_number - 1].append(i)
        last_i = i

    logging.debug('request_min_db: q_list:' + str(q_list))
    for i in q_list:
        logging.debug('request_min_db: request_api:' + str(i[0]) + ' ' +
                      str(i[len(i) - 1]) + ' ' +  str(coin_name))
        request_api(i[0], i[len(i) - 1], coin_name)


def data_retrieval(s_date: str, e_date: str, coin_name: str,
                   min_param: str, day_delta):
    """Request data from database depending on the minimise parameter"""
    if min_param == 'a':  # Minimise query count from api
        logging.debug('data_retrieval: Requesting with minimise query count '
                      'from api')
        request_api(s_date, e_date, coin_name)
    elif min_param == 'db':  # Minimise query count from database
        logging.debug('data_retrieval: Requesting with minimise query count '
                      'from database')
        request_min_db(s_date, e_date, coin_name, day_delta)
    plt_data = dbw.get_data(coin_name, s_date, e_date)
    plt_file_name = str(s_date) + '__' + str(e_date)
    graph.graph_plt(plt_data, plt_file_name, coin_name)


def check_date(start_dt, end_dt):
    """Check dates for correct and fix if need"""
    logging.debug('check_date: start_dt=' + str(start_dt) +
                  ', end_dt=' + str(end_dt))
    min_date = get_min_date(args.coin)
    if date.fromisoformat(start_dt) < date.fromisoformat(min_date):
        start_dt = min_date
    if date.fromisoformat(args.end_date) > date.today():
        end_dt = date.today().strftime('%Y-%m-%d')
    if start_dt > end_date:
        start_dt = end_dt
    logging.debug('check_date: return: start_dt=' + str(start_dt) +
                  ', end_dt=' + str(end_dt))
    return start_dt, end_dt


if __name__ == "__main__":
    logging.basicConfig(filename='log.log', filemode='w',
                        format='%(asctime)s %(name)s '
                               '- %(levelname)s - '
                               '%(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S',
                        level=logging.DEBUG)  # pylint: disable = duplicate-code
    parser = argparse.ArgumentParser(description='Arguments to coin tracker')
    parser.add_argument('-sd', dest='start_date', type=str,
                        default=(date.today() - timedelta(7))
                        .strftime('%Y-%m-%d'),
                        help="Start date fo search data")
    parser.add_argument('-ed', dest='end_date', type=str,
                        default=date.today().strftime('%Y-%m-%d'),
                        help="End date fo search data")
    parser.add_argument('-c', dest='coin', type=str,
                        default='bpi',
                        help="What coin data query? Bitcoin = bpi")
    parser.add_argument('-m', dest='minimise', type=str,
                        default='db',
                        help="Minimise query for api (-m=a) or query from db "
                             "(-m=db)")
    args = parser.parse_args()
    start_date = args.start_date
    end_date = args.end_date
    minimise = args.minimise
    logging.info('Start params: start_date: ' + str(args.start_date) +
                 ', end_date: ' + str(args.end_date) +
                 ', minimise: ' + str(args.minimise))
    start_date, end_date = check_date(start_date, end_date)

    days_delta = date.fromisoformat(args.end_date) - \
                 date.fromisoformat(args.start_date)

    if days_delta > timedelta(100):
        logging.error("Too long period. Maximum 100 days for query.")
    else:
        data_retrieval(args.start_date, args.end_date, args.coin, minimise,
                       days_delta)
