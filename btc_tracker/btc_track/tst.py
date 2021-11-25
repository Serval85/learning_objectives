import json
from datetime import date, timedelta
import sqlite3

import json
import pandas as pd
import matplotlib.pyplot as plt

records = [(1, 'Glen', 8),
           (2, 'Elliot', 9),
           (3, 'Bob', 7)]

js = {"2013-09-01": 128.2597, "2013-09-08": 128.2597, "2013-09-02": 127.3648,
      "2013-09-03": 127.5915, "2013-09-04": 120.5738, "2013-09-05": 120.5333}

lst = js.items()
print('lst = ' + str(lst))

dt = (date.today() - timedelta(8)).strftime('%Y-%m-%d')
# print(dt)

conn = sqlite3.connect('mysqlite.db')
c = conn.cursor()

# records or rows in a list
records = [(1, 'Glen', 8),
           (2, 'Elliot', 9),
           (3, 'Bob', 7)]

c.execute('CREATE TABLE IF NOT EXISTS '
          'bpi(date DATE PRIMARY KEY, price REAL);')
conn.commit()

# insert multiple records in a single query
c.executemany('INSERT OR IGNORE INTO bpi VALUES(?,?);', lst)

# print('We have inserted', c.rowcount, 'records to the table.')

# commit the changes to db
conn.commit()
# close the connection

start_date = "2013-08-31"
end_date = "2013-09-15"
c.execute('SELECT DATE FROM bpi WHERE date BETWEEN "' + \
          start_date + '" AND "' + end_date + '"')
res = c.fetchall()
conn.commit()
conn.close()

date_set_db = set()

for i in res:
    date_set_db.add(i[0])
print('date from DB' + str(date_set_db))

days_delta = date.fromisoformat(end_date) - \
             date.fromisoformat(start_date)

base = date.fromisoformat(start_date)
date_list = [str(base + timedelta(days=x)) for x in range(days_delta.days + 1)]
date_set_query = set(date_list)
date_set_query.symmetric_difference_update(date_set_db)

date_set_list = list(date_set_query)
date_set_list.sort()
querys_list = []
list_number = 0
last_i = '1900-07-17'
# print(last_i)
print(date_set_list)
for i in date_set_list:
    print("i = " + str(i))
    print("last_i = " + str(last_i))
    if date.fromisoformat(i) > date.fromisoformat(last_i) + timedelta(1):
        querys_list.append([])
        print(querys_list)
        querys_list[list_number].append(i)
        print(querys_list)
        list_number += 1

    if date.fromisoformat(i) == date.fromisoformat(last_i) + timedelta(1):
        print(list_number)
        querys_list[list_number - 1].append(i)
        print('querys_list app = ' + str(querys_list))

    last_i = i
print('querys_list = ' + str(querys_list))

for i in querys_list:
    res = (i[0], i[len(i) - 1])
    print(res)

data = json.dumps({
    "success":True,
        "data":[
            {

                "record_id":258585618,
                "timestamp":"2018-01-21 22:34:34",
                "bytes":29466,

            }
            ,
            {
                "record_id":258585604,
                "timestamp":"2018-01-21 22:33:14",
                "bytes":37892,
            }
            ,
            {
                "record_id":258584399,
                "timestamp":"2018-01-21 22:37:40",
                "bytes":36396,
            }
        ]
    })

data = json.loads(data)
dates = [i['timestamp'] for i in data["data"]]
values = [i['bytes'] for i in data['data']]

df = pd.DataFrame({'dates':dates, 'values':values})
df['dates'] = [pd.to_datetime(i) for i in df['dates']]

plt.bar(dates, values)