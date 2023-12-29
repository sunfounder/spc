from influxdb import InfluxDBClient

class DB:
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
        self.client.write_points(json_body)

    def get_data_by_time_range(self, measurement, start_time, end_time):
        query = f"SELECT * FROM {measurement} WHERE time >= '{start_time}' AND time <= '{end_time}'"
        result = self.client.query(query)
        return list(result.get_points())

    def get_latest_data(self, measurement, n=1):
        query = f"SELECT * FROM {measurement} ORDER BY time DESC LIMIT {n}"
        result = self.client.query(query)
        return list(result.get_points())

    def close_connection(self):
        self.client.close()
