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

#import API Wrapper (Python bindings) and additional libraries
import deepinstinct30 as di
import pandas, datetime
from dateutil import parser

#define server config
di.key = 'BAR'
di.fqdn = 'FOO.customers.deepinstinctweb.com'

#get events from server
search_parameters = {}
search_parameters['type'] = ['STATIC_ANALYSIS']
search_parameters['action'] = ['PREVENTED']
search_parameters['last_action'] = ['QUARANTINE_SUCCESS']
events = di.get_events(search=search_parameters)

#using events, calculate list of unique hashes
hash_list = []
for event in events:
    if event['file_hash'] not in hash_list:
        hash_list.append(event['file_hash'])

#get policies
all_policies = di.get_policies()

#filter policy list
windows_policies = []
for policy in all_policies:
    if policy['os'] == 'WINDOWS':
        windows_policies.append(policy)

#iterate through Windows policies and add the allow lists to each
for policy in windows_policies:
    di.add_allow_list_hashes(hash_list, policy['id'])

#save hash list and event list for later usage
hash_list_df = pandas.DataFrame(hash_list)
events_df = pandas.DataFrame(events)
folder_name = di.create_export_folder()
file_name = 'premature_prevention_recovery.xlsx'

with pandas.ExcelWriter(f'{folder_name}/{file_name}') as writer:
    hash_list_df.to_excel(writer, sheet_name='hash_list', index=False)
    events_df.to_excel(writer, sheet_name='event_list', index=False)

print('Data written to', f'{folder_name}/{file_name}')
