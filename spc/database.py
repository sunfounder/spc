from influxdb import InfluxDBClient

class DB:
    def __init__(self):
        self.client = InfluxDBClient(host='localhost', port=8086)
        self.database = 'spc'

        # 检查数据库是否存在，如果不存在则创建
        databases = self.client.get_list_database()
        if not any(db['name'] == self.database for db in databases):
            self.client.create_database(self.database)
            print(f"Database '{self.database}' created successfully")

        # 连接到指定数据库
        self.client.switch_database(self.database)

    def set(self, measurement, data):
        # 处理布尔值
        def handle_boolean(value):
            if isinstance(value, bool):
                return str(value).lower()
            return value

        # 递归处理数据字典
        def handle_data(data):
            for key, value in data.items():
                if isinstance(value, dict):
                    data[key] = handle_data(value)
                else:
                    data[key] = handle_boolean(value)
            return data

        data = handle_data(data)

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

    def get_latest_data(self, measurement):
        query = f"SELECT * FROM {measurement} ORDER BY time DESC LIMIT 1"
        result = self.client.query(query)
        return list(result.get_points())

    def close_connection(self):
        self.client.close()

def test():
    from spc.spc import SPC
    from spc.utils import get_memory_info, get_disks_info, get_network_info, get_cpu_info, get_boot_time

    spc = SPC()
    db = DB()
    data = spc.read_all()
    data['cpu'] = get_cpu_info()
    data['memory'] = get_memory_info()
    data['disk'] = get_disks_info()
    data['network'] = get_network_info()
    data['boot_time'] = get_boot_time()

    db.set('history', data)

    # 获取指定时间区段的数据
    start_time = '2021-01-01T00:00:00Z'
    end_time = '2021-01-01T23:59:59Z'
    results = db.get_data_by_time_range('history', start_time, end_time)
    print("Data within time range:")
    for result in results:
        print(result)

    # 获取最新数据
    latest_data = db.get_latest_data('history')
    print("Latest data:")
    print(latest_data)

    db.close_connection()

if __name__ == "__main__":
    test()