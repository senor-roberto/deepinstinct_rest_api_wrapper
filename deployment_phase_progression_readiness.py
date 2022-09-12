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

# import required libraries
import deepinstinct30 as di, json, datetime, pandas, re
from dateutil import parser

# Calculates deployment phase for a Windows policy. Non-conforming and non-Windows policies return 0.
def classify_policy(policy):

    if policy['os'] == 'WINDOWS':

        if policy['prevention_level'] == 'DISABLED':
            return 1

        elif policy['prevention_level'] in ['LOW', 'MEDIUM', 'HIGH']:

            if policy['in_memory_protection'] == False:
                return 2

            elif policy['in_memory_protection'] == True:
                if policy['remote_code_injection'] == 'DETECT':
                    if policy['arbitrary_shellcode_execution'] == 'DETECT':
                        if policy['reflective_dll_loading'] == 'DETECT':
                            if policy['reflective_dotnet_injection'] == 'DETECT':
                                if policy['amsi_bypass'] == 'DETECT':
                                    if policy['credentials_dump'] == 'DETECT':
                                        return 3

                if policy['remote_code_injection'] == 'PREVENT':
                    if policy['arbitrary_shellcode_execution'] == 'PREVENT':
                        if policy['reflective_dll_loading'] == 'PREVENT':
                            if policy['reflective_dotnet_injection'] == 'PREVENT':
                                if policy['amsi_bypass'] == 'PREVENT':
                                    if policy['credentials_dump'] == 'PREVENT':
                                        return 4

    return 0


# Calculates search parameters for events based on current deployment phase
def get_event_search_parameters(deployment_phase):

    search_parameters = {}

    #static parameters for all phases
    search_parameters['status'] = ['OPEN']
    search_parameters['threat_severity'] = ['MODERATE', 'HIGH', 'VERY_HIGH']

    if deployment_phase in [1, 2]:
        search_parameters['type'] = ['STATIC_ANALYSIS']
        search_parameters['type'].append('RANSOMWARE_FILE_ENCRYPTION')
        search_parameters['type'].append('SUSPICIOUS_SCRIPT_EXCECUTION')
        search_parameters['type'].append('MALICIOUS_POWERSHELL_COMMAND_EXECUTION')

        if deployment_phase == 1:
            search_parameters['action'] = ['DETECTED']
        else:
            search_parameters['action'] = ['PREVENTED']

    elif deployment_phase in [3, 4]:
        search_parameters['action'] = ['PREVENTED']
        search_parameters['type'] = ['REMOTE_CODE_INJECTION_EXECUTION']
        search_parameters['type'].append('KNOWN_SHELLCODE_PAYLOADS')
        search_parameters['type'].append('ARBITRARY_SHELLCODE')
        search_parameters['type'].append('REFLECTIVE_DLL')
        search_parameters['type'].append('REFLECTIVE_DOTNET')
        search_parameters['type'].append('AMSI_BYPASS')
        search_parameters['type'].append('DIRECT_SYSTEMCALLS')
        search_parameters['type'].append('CREDENTIAL_DUMP')

        if deployment_phase == 3:
            search_parameters['action'].append('DETECTED')

    return search_parameters


def run_deployment_phase_progression_readiness(fqdn, key, config):

    print('\nINFO: Beginning analysis')

    di.fqdn = fqdn
    di.key = key
    config = config

    #collect policy data
    print('INFO: Getting policy list and data from server')
    policies = di.get_policies(include_policy_data=True)
    #calculate deployment_phase for each policy and add to policy data
    print('INFO: Evaluating policy data to determine deployment phase(s)')
    print('phase\t id\t name')
    for policy in policies:
        policy['deployment_phase'] = classify_policy(policy)
        if policy['os'] == 'WINDOWS':
            print(policy['deployment_phase'], '\t', policy['id'], '\t', policy['name'])

    #collect event data
    print('INFO: Calculating event search parameters')
    search_parameters = get_event_search_parameters(config['deployment_phase'])
    print('INFO: Querying server for events matching the following criteria:\n', json.dumps(search_parameters, indent=4))
    events = di.get_events(search=search_parameters)
    print('INFO:', len(events), 'events were returned')
    print('INFO: Summarizing event data by device id')
    event_counts = di.count_data_by_field(events, 'device_id')

    #collect device data
    print('INFO: Getting device list from server')
    devices = di.get_devices(include_deactivated=False)
    print('INFO:', len(devices), 'devices were returned')
    print('INFO: Appending deployment phase data to device list')
    for device in devices:
        for policy in policies:
            if policy['id'] == device['policy_id']:
                device['deployment_phase'] = policy['deployment_phase']

    print('INFO: Filtering device data to remove devices not in a phase', config['deployment_phase'], 'policy')
    filtered_devices = []
    for device in devices:
        if device['deployment_phase'] == config['deployment_phase']:
            filtered_devices.append(device)
    devices = filtered_devices
    print('INFO:', len(devices), 'devices remain')

    print('INFO: Adding event count data to device list')
    for device in devices:
        if device['id'] not in event_counts.keys():
            device['event_count'] = 0
        else:
            device['event_count'] = event_counts[device['id']]

    print('INFO: Calculating days since last contact and adding results to device list')
    for device in devices:
        device['last_contact_days_ago'] = (datetime.datetime.now(datetime.timezone.utc) - parser.parse(device['last_contact'])).days

    #add days_since_deployment field to devices
    print('INFO: Adding days_since_deployment to device data by comparing last_registration to current datetime')
    for device in devices:
        device['days_since_deployment'] = (datetime.datetime.now(datetime.timezone.utc) - parser.parse(device['last_registration'])).days

    print('INFO: Evaluating devices to determine which are ready to progress to the next phase')
    for device in devices:
        device['ready_to_move_to_next_phase'] = False
        if device['last_contact_days_ago'] <= int(config['max_days_since_last_contact']):
            if device['event_count'] <= int(config['max_open_event_quantity']):
                device['ready_to_move_to_next_phase'] = True

    print('INFO: Sorting devices into list by readiness')
    devices_ready = []
    devices_not_ready = []
    for device in devices:
        if device['ready_to_move_to_next_phase']:
            devices_ready.append(device)
        else:
            devices_not_ready.append(device)

    print('INFO: Analysis is complete')

    #print summary to console
    print(len(devices_ready), 'of', len(devices), 'devices are ready to move from phase', config['deployment_phase'], 'to phase', int(config['deployment_phase'])+1, 'and', len(devices_not_ready), 'devices are not based on this criteria:')
    print(json.dumps(config,indent=4))

    #convert data to be exported to dataframes
    print('INFO: Creating pandas dataframes')
    devices_ready_df = pandas.DataFrame(devices_ready)
    devices_not_ready_df = pandas.DataFrame(devices_not_ready)
    config_df = pandas.DataFrame(config.items())
    search_parameters_df = pandas.DataFrame(search_parameters.items())

    #prep for export
    print('INFO: Preparing export folder and file name')
    folder_name = di.create_export_folder()
    from_deployment_phase = config['deployment_phase']
    to_deployment_phase = from_deployment_phase + 1
    if di.is_server_multitenancy_enabled():
        server_shortname = re.sub(r'[^a-z0-9]','',policies[0]['msp_name'].lower())
    else:
        server_shortname = di.fqdn.split(".",1)[0]
    file_name = f'deployment_phase_{from_deployment_phase}_to_phase_{to_deployment_phase}_readiness_assessment_{datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d_%H.%M")}_UTC_{server_shortname}.xlsx'

    #export dataframes to Excel format
    print('INFO: Exporting dataframes to disk')
    with pandas.ExcelWriter(f'{folder_name}/{file_name}') as writer:
        devices_ready_df.to_excel(writer, sheet_name='ready_for_next_phase', index=False)
        devices_not_ready_df.to_excel(writer, sheet_name='not_ready_for_next_phase', index=False)
        config_df.to_excel(writer, sheet_name='config', index=False)
        search_parameters_df.to_excel(writer, sheet_name='event_search_criteria', index=False)
    print(f'{folder_name}\\{file_name}')
    print('Done.')


def main():
    #prompt for config
    fqdn = input('Enter FQDN of DI Server, or press enter to accept the default [di-service.customers.deepinstinctweb.com]: ')
    if fqdn == '':
        fqdn = 'di-service.customers.deepinstinctweb.com'

    key = input('Enter API Key for DI Server: ')

    config = {}

    config['deployment_phase'] = 0
    while config['deployment_phase'] not in (1, 2, 3, 4):
        config['deployment_phase'] = int(input('Enter the deployment phase of the devices you want to evaluate ( 1 | 2 | 3 | 4 ): '))

    config['max_days_since_last_contact'] = input('Enter the maximum days since Last Contact for a device to be eligible to progress to the next phase, or press enter to accept the default [3]: ')
    if config['max_days_since_last_contact'] == '':
        config['max_days_since_last_contact'] = 3

    config['max_open_event_quantity'] = input('Enter the maximum number of Open Events for a device to be eligible to progress to the next phase, or press enter to accept the default [0]: ')
    if config['max_open_event_quantity'] == '':
        config['max_open_event_quantity'] = 0

    return run_deployment_phase_progression_readiness(fqdn=fqdn, key=key, config=config)

if __name__ == "__main__":
    main()
