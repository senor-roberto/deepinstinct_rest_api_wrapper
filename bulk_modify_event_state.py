# bulk_modify_event_state.py
# Author: Patrick Van Zandt, Principal Professional Services Engineer
# January 2022

# This script provides an example of how to use the Deep Instinct REST API
# Wrapper published at https://github.com/pvz01/deepinstinct_rest_api_wrapper
# to programatically manage event state in mass. Specifically, it shows how
# to get all events from the server, apply filters, and then close or close
# and archive those events. The events where action is taken are written to
# disk in Excel format.

# This script is provided as-is and with no warranty. Use at your own risk.

# Prerequisites:
# 1. Python 3.8 or later
# 2. Deep Instinct REST API Wrapper
# 3. Third-party libraries (strongly recommend to install Anaconda)
# 4. Network access to management server
# 5. API key with appropriate permissions (Full Access | Read and Remediation)

# Usage:
# 1. Save latest version of deepinstinct30.py from
#    https://github.com/pvz01/deepinstinct_rest_api_wrapper to disk
# 2. Save bulk_modify_event_state.py to the same folder on disk
# 3. Modify the code in the section prefixed with "Runtime configuration"
#    comment to define which arction(s) you want to perform
# 4. Modify the code in the section prefixed with "filter the events" comment
#    below to define which events you want to close and/or archive
# 5. Save modified script
# 6. Open a Command Prompt window, CD to the directory containing the 2 PY
#    files, and run this command: python bulk_modify_event_state.py
# 7. When prompted, provide server FQDN in this format:
#    foo.customers.deepinstinctweb.com
# 8. When prompted, provide the API key
# 9. Answer additional prompts. You can exit any time with Ctrl+C. Recommend
#    to review the Excel document written to disk *before* answering "YES" to
#    proceeding (when prompted).


#import API Wrapper
# Note: Always use latest from https://github.com/pvz01/deepinstinct_rest_api_wrapper/blob/main/deepinstinct30.py
import deepinstinct30 as di

#import additional libraries
import json, datetime, pandas, sys
from dateutil import parser

#server configuration
di.fqdn = 'SERVER-NAME.customers.deepinstinctweb.com'
di.key = 'API-KEY'

#runtime configuration
close_events = True
archive_events = False

#prompt for server configuration (unless hardcded values were provided above)
if di.fqdn == 'SERVER-NAME.customers.deepinstinctweb.com':
    di.fqdn = input('FQDN of DI Server? ')
if di.key == 'API-KEY':
    di.key = input('Full Access API Key? ')

#enabling this results in the call to di.get_events() printing updates as it
#gathers events from the server 50 at a time
di.debug_mode = True

#get all events from server
all_events = di.get_events()
print('INFO:', len(all_events), 'total visible events on server')

#filter the events
filtered_events = []
for event in all_events:
    if event['status'] in ['OPEN']:
        if event['recorded_device_info']['hostname'] in ['HOSTNAME01']:
            if event['type'] in ['REFLECTIVE_DOTNET']:
                if event['path'] in ['C:\\Program Files (x86)\\Microsoft SQL Server\\100\\DTS\\Binn\\DTExec.exe']:
                    filtered_events.append(event)
            if event['type'] in ['AMSI_BYPASS']:
                if event['path'] in ['C:\\Program Files (x86)\\Microsoft SQL Server\\100\\DTS\\Binn\\SQLPS.exe']:
                    filtered_events.append(event)


#write data to disk
filtered_events_df = pandas.DataFrame(filtered_events)
folder_name = di.create_export_folder()
file_name = f'mass_closed_events_{datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d_%H.%M")}_UTC.xlsx'
filtered_events_df.to_excel(f'{folder_name}/{file_name}', index=False)
print('INFO:', len(filtered_events), 'events found matching defined criteria and have been written to disk as', f'{folder_name}/{file_name}')

#ask for confirmation to proceed
user_input = input('\nDo you want to proceed? If yes, type YES and press return: ')
if user_input.lower() != 'yes':
    sys.exit(0)

#strip out event ids from filtered_events
event_id_list = []
for event in filtered_events:
    event_id_list.append(event['id'])

#break event_id_list into a list of smaller lists
batch_size = 250
event_id_list_broken_into_batches = [event_id_list[i:i + batch_size] for i in range(0, len(event_id_list), batch_size)]
print('\nINFO: The', len(event_id_list), 'event IDs have been broken into', len(event_id_list_broken_into_batches), 'batches of', batch_size)

#iterate through the batches of event ids
batch_number = 1
for batch in event_id_list_broken_into_batches:
    print('Processing batch', batch_number, 'of', len(event_id_list_broken_into_batches))
    if close_events:
        #close the events
        print('  Closing', len(batch), 'events')
        di.close_events(batch)

    if archive_events:
        #archive the events
        print('  Archiving', len(batch), 'events')
        di.archive_events(batch)
    batch_number += 1
