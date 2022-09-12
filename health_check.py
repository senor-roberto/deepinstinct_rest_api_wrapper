import deepinstinct30 as di

di.fqdn = input('Enter FQDN of DI Server, or press enter to accept the default [di-service.customers.deepinstinctweb.com]: ')
if di.fqdn == '':
    di.fqdn = 'di-service.customers.deepinstinctweb.com'

di.key = input('Enter API Key for DI Server: ')

minimum_event_id = input('Enter minimum_event_id as an integer, or press enter to accept the default [0]: ')
if minimum_event_id == '':
    minimum_event_id = 0

di.health_check(minimum_event_id=minimum_event_id)
