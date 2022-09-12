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

import deepinstinct30 as di

#prompt for config
di.fqdn = input('Enter FQDN of DI Server, or press enter to accept the default [di-service.customers.deepinstinctweb.com]: ')
if di.fqdn == '':
    di.fqdn = 'di-service.customers.deepinstinctweb.com'

di.key = input('\nEnter API Key for DI Server: ')

#Prompt for Device Group Name
device_group_name = input('\nEnter Device Group Name to move devices to: ')

#Prompt for hostname(s)
device_name_list = []
device_name = None
print('\nInstructions: Below you will enter the hotname(s) of the device(s) to move with one per line. Suggest to copy/paste from an Excel document or text file. Ensure that there are no leading or trailing spaces, quotations, or other characters. When you are done entering hostnames, provide no input and press return to continue.\n')
while device_name != '':
    device_name = input('Enter a hostname (or just press return to exit): ')
    if device_name != '':
        device_name_list.append(device_name)

#Print preview of the move to the console
print('\nDevice(s) with hostname(s)\n',device_name_list, '\nwill be moved to\n', device_group_name, '\non server\n', di.fqdn, '\nusing API key\n', di.key, '\n')

#Ask user to confirm
user_input = input('To execute the above change, type YES in all caps and press return: ')

#Check user response
if user_input == 'YES':
    print('\nSending request to server')
    #Call move_devices to execute the change
    result = di.move_devices(device_name_list, device_group_name)
    #Check results and print summary to console if successful
    if result != None:
        #change was sucessful. print details to console
        print(result)
    else:
        print('Something went wrong. No devices were moved.')
else:
    #User response did not approve the change
    print('The change was aborted.')
