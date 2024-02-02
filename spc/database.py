from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError
import json

from .logger import Logger
log = Logger(script_name="database")

class Database:
    def __init__(self, log=None):
        if log is None:
            self.log = log
        self.client = InfluxDBClient(host='localhost', port=8086)
        self.database = 'spc'

        databases = self.client.get_list_database()
        if not any(db['name'] == self.database for db in databases):
            self.client.create_database(self.database)
            print(f"Database '{self.database}' created successfully")

        self.client.switch_database(self.database)

    def set(self, measurement, data):
        json_body = [
            {
                "measurement": measurement,
                "fields": data
            }
        ]
        try:
            self.client.write_points(json_body)
            return True, json_body
        except InfluxDBClientError as e:
            return False, json.loads(e.content)["error"]

    def get_data_by_time_range(self, measurement, start_time, end_time, key="*"):
        query = f"SELECT {key} FROM {measurement} WHERE time >= '{start_time}' AND time <= '{end_time}'"
        result = self.client.query(query)
        return list(result.get_points())

    def if_too_many_nulls(self, result, threshold):
        for point in result:
            if len([key for key, value in point.items() if value is None]) > threshold:
                return True
        return False

    def get(self, measurement, key="*", n=1):
        for _ in range(3):
            query = f"SELECT {key} FROM {measurement} ORDER BY time DESC LIMIT {n}"
            result = self.client.query(query)
            if self.if_too_many_nulls(list(result.get_points()), 3):
                self.log(f"Too many nulls in the result of query: {query}, trying again...", level='WARNING')
                continue
            break
        else:
            return None
        if n == 1:
            if len(list(result.get_points())) == 0:
                return None
            return list(result.get_points())[0][key]
        
        return list(result.get_points())

    def close_connection(self):
        self.client.close()
