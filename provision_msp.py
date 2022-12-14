# provision_msp.py
# Author: Patrick Van Zandt, Principal Professional Services Engineer
# December 2021

# This script provides an example of how to use the Deep Instinct REST API
# Wrapper published at https://github.com/pvz01/deepinstinct_rest_api_wrapper
# to provision new MSPs on a multi-tenancy server, including pre-populating
# them with a set of policies based upon a template MSP.

# This script is provided as-is and with no warranty. Use at your own risk, and
# please test in a non-production environment first.

# PREREQUISITES
# 1. Python 3.8 or later
# 2. Deep Instinct REST API Wrapper
# 3. Third-party libraries (strongly recommend to install Anaconda)
# 4. Network access to management server on port 443
# 5. Multi-tenancy enabled D-Appliance (management server)
# 6. A Full Access API key for all MSPs

# KNOWN LIMITATIONS AND USAGE NOTES
# Only policy settings that are available to read and write via the
# DI REST API are migrated. Any settings not visible via the API remain
# at their defailts in the destination policies. As of December 2021, the
# non-visible fields in Windows policies are:
# 1. Enable D-Cloud services
# 2. Embedded DDE object in Microsoft Office document
# 3. Suspicious Script Execution
# 4. Malicious PowerShell Command Execution
# 5. Suspicious Activity Detection
# 6. Suspicious PowerShell Command Execution
# 7. Integrate D-Client with Windows Security Center
# 8. Permitted connections for network isolated devices
# 9. Gradual Deployment
# For up-to-date information, reference the WindowsPolicyData model in the API
# documentation on your DI server. If/when additional fields are added, this
# script will automatically migrate them.

# USAGE
# 1. Save the latest version of both this file (provision_msp.py) and
#    the DI API Wrapper (deepinstinct30.py) to the same folder on disk.
# 2. Edit this file to provide the customer name, license count, server, api
#    key, and the id of the template msp in-line below.
# 3. Execute the script with this command:  python provision_msp.py


#define details of the new customer
customer_name = 'testrobh2'
license_count = 1

#Import DI API Wrapper. Always use latest from https://github.com/pvz01/deepinstinct_rest_api_wrapper
import deepinstinct30 as di, json

#set server name (must be a MULTI-TENANCY enabled D-Appliance)
di.fqdn = 'partner-emea.customers.deepinstinctweb.com'

#Set API key (must be FULL ACCESS / ALL MSPS created in DI Hub)
di.key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NDg0NzAwMDgsIm5iZiI6MTY0ODQ3MDAwOCwianRpIjoiNDA4ZjJlZDktYzUzOS00MDY4LTljMzEtNTJmODc5ZDNlZjViIiwiaWRlbnRpdHkiOnsia2V5IjoyNH0sImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyJ9.9dVVMCn7eVdS8yuhvTR3HZ6rj8qF294go1I2-lwnCzg'

#define which already-existing MSP on the server is the template (to copy policies from)
template_msp_id = 43

#create new msp for the customer and one tenant within it
new_msp = di.create_msp(customer_name, license_count)
new_tenant = di.create_tenant(customer_name, license_count, new_msp['name'])

#pretty-print the new Tenant information, which includes activation tokens
print(json.dumps(new_tenant, indent=4))

#copy the policy data from the template to the new MSP
di.migrate_policies(source_msp_id=template_msp_id, destination_msp_id=new_msp['id'])
