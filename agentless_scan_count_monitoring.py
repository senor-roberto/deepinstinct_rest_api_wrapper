# Disclaimer:
# This code is provided as an example of how to build code against and interact
# with the Deep Instinct REST API. It is provided AS-IS/NO WARRANTY. It has
# limited error checking and logging, and likely contains defects or other
# deficiencies. Test thoroughly first, and use at your own risk. The API
# Wrapper and associated samples are not Deep Instinct commercial products and
# are not officially supported, although he underlying REST API is. This means
# that to report an issue to tech support you must remove the API Wrapper layer
# and recreate the problem with a reproducible test case against the raw/pure
# DI REST API.
#

import deepinstinct25 as di, datetime, time

# Optional hardcoded config - if not provided, you'll be prompted at runtime
di.fqdn = 'SERVER-NAME.customers.deepinstinctweb.com'
di.key = 'API-KEY'

# Validate config and prompt if not provided above
while di.fqdn == '' or di.fqdn == 'SERVER-NAME.customers.deepinstinctweb.com':
    di.fqdn = input('FQDN of DI Server? ')
while di.key == '' or di.key == 'API-KEY':
    di.key = input('API Key? ')

# Establish variable for tracking scanned file count
current_scanned_file_count = 0

while True: #run indefinitely

    # Save previous scan count and reset current to zero
    previous_scanned_file_count = current_scanned_file_count
    current_scanned_file_count = 0

    # Capture timestamp of the start of this iteration
    start_time = time.perf_counter()

    # Get device data from DI server
    devices = di.get_devices()

    # Calculate sum of scanned files for Agentless connectors
    current_scanned_file_count = 0
    for device in devices:
        if device['os'] == 'NETWORK_AGENTLESS':
            current_scanned_file_count += device['scanned_files']

    # Write data to disk
    file_name = f'current_scanned_file_counts_{di.fqdn}.txt'
    timestamp = f'{datetime.datetime.utcnow().strftime("%Y-%m-%d_%H.%M.%S")}'
    log_file_entry = f'{di.fqdn}' + '\t' + timestamp + '\t' + str(current_scanned_file_count) + '\t' + str(current_scanned_file_count - previous_scanned_file_count)
    #print(log_file_entry)
    file = open(file_name, 'a')
    file.write(log_file_entry + '\n')
    file.close()

    # Sleep for specified number of seconds (less runtime for this iteration)
    runtime = time.perf_counter() - start_time
    #print('Runtime was', runtime, 'seconds')
    time.sleep(3600 - runtime)
