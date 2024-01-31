# Dashboard Reference API
=======================

- Port: `34001`
- Base URL: `/api/v1.0/`
  
## Endpoints

### GET /test

- Description: Test if the server is running
- Response: 
  - `{"status": true, "data": "OK"}`

### GET /test-mqtt

- Description: Test if the MQTT configuration is correct
- Data: 
  - `host` - MQTT Broker Host
  - `port` - MQTT Broker Port
  - `username` - MQTT Broker Username
  - `password` - MQTT Broker Password
- Response: 
  - `{"status": true, "data": {"status": true, "error": null}}`
  - `{"status": true, "data": {"status": false, "error": "Timeout"}}`
  - `{"status": true, "data": {"status": false, "error": "Connection failed, Check hostname and port"}}`
  - `{"status": true, "data": {"status": false, "error": "Connection failed, Check username and password"}}`
  - `{"status": false, "error": "ERROR, host not found"}`
  - `{"status": false, "error": "ERROR, port not found"}`
  - `{"status": false, "error": "ERROR, username not found"}`
  - `{"status": false, "error": "ERROR, password not found"}`

### GET /get-all (deprecated)

- Description: Get all status
- Response:
  - `{"status": true, "data": {}`

### GET /get-config

- Description: Get configuration
- Response:
  - `{"status": true, "data": {}`

### GET /get-history

- Description: Get history
- Data:
  - `n` - Number of records to return
- Response:
  - `{"status": true, "data": []}`

### GET /get-time-range

- Description: Get time range
- Data:
  - `start` - Start time
  - `end` - End time
  - `key`(optional) - Key to filter
- Response:
  - `{"status": true, "data": []}`

### GET /get-log-list

- Description: Get log list
- Response:
    ```
    {
      "status": true,
      "data": [
        "config.log",
        "mqtt_client.log",
        "data_logger.log.2",
      ]
    }
    ```

### GET /get-log

- Description: Get log
- Data:
  - `log` - Log file name
  - `n`(optional) - Number of records to return
  - `filter`(optional) - Filter, divided by comma
  - `level`(optional) - Log level `['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']`
- Response:
  - `{"status": false, "error": "ERROR, file not found"}`
  - `{"status": true, "data": []}`

### POST /set-fan-mode

- Description: Set fan mode
- Data:
  - `data` - Fan mode `['auto', 'performance', 'normal', 'quiet']`
- Response:
  - `{"status": true, "data": data}`

### POST /set-fan-state

- Description: Set fan state
- Data:
  - `data` - Fan state `[true, false]`
- Response:
  - `{"status": true, "data": data}`

### POST /set-config

- Description: Set configuration
- Data:
  - `data` - Configuration data
- Response:
  - `{"status": true, "data": data}`
