from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBClientError
import json

class Database:
    def __init__(self):
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

    def get(self, measurement, key="*", n=1):
        query = f"SELECT {key} FROM {measurement} ORDER BY time DESC LIMIT {n}"
        result = self.client.query(query)
        if n == 1:
            if len(list(result.get_points())) == 0:
                return None
            return list(result.get_points())[0]
        return list(result.get_points())

    def close_connection(self):
        self.client.close()
