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

#read hash list from Excel file on disk
file_name = 'premature_prevention_recovery.xlsx'
folder_name = di.create_export_folder()
hash_list_df = pandas.read_excel(f'{folder_name}/{file_name}', sheet_name='hash_list')
hash_list_df.columns=['hashes']
hash_list = hash_list_df['hashes'].values.tolist()

#get events from server
search_parameters = {}
search_parameters['type'] = ['STATIC_ANALYSIS']
search_parameters['action'] = ['PREVENTED']
search_parameters['last_action'] = ['QUARANTINE_SUCCESS']
events = di.get_events(search=search_parameters)

#calculate list of hashes for files still in quarantine
hash_list_still_in_quarantine = []
for event in events:
    if event['file_hash'] not in hash_list_still_in_quarantine:
        hash_list_still_in_quarantine.append(event['file_hash'])

#calculate hashes safe to remove from allow list
hashes_to_remove = []
for hash in hash_list:
    if hash not in hash_list_still_in_quarantine:
        hashes_to_remove.append(hash)

#get policies
all_policies = di.get_policies()

#filter policy list
windows_policies = []
for policy in all_policies:
    if policy['os'] == 'WINDOWS':
        windows_policies.append(policy)

#iterate through Windows policies and remove the allow lists from each
for policy in windows_policies:
    di.remove_allow_list_hashes(hashes_to_remove, policy['id'])
