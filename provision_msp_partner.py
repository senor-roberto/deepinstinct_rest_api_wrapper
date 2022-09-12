#Import DI API Wrapper. Always use latest from https://github.com/pvz01/deepinstinct_rest_api_wrapper
import deepinstinct30 as di, json

di.key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NDg0NzAwMDgsIm5iZiI6MTY0ODQ3MDAwOCwianRpIjoiNDA4ZjJlZDktYzUzOS00MDY4LTljMzEtNTJmODc5ZDNlZjViIiwiaWRlbnRpdHkiOnsia2V5IjoyNH0sImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyJ9.9dVVMCn7eVdS8yuhvTR3HZ6rj8qF294go1I2-lwnCzg'
di.fqdn = 'partner-emea.customers.deepinstinctweb.com'

if __name__ == '__main__':
	#define details of the new customer
	customer_name = input('Enter name of new MSP [PTE - NL - MSPNAME]: ')
	license_count = input('Enter license count for new MSP: ')

	#define which already-existing MSP on the server is the template (to copy policies from)
	template_msp_id = input('Enter already-existing MSP ID which acts as the template (to copy policies from): ')

	#create new msp for the customer and one tenant within it
	new_msp = di.create_msp(customer_name, int(license_count))
	new_tenant = di.create_tenant(customer_name, int(license_count), new_msp['name'])

	#pretty-print the new Tenant information, which includes activation tokens
	print(json.dumps(new_tenant, indent=4))

	#copy the policy data from the template to the new MSP
	di.migrate_policies(source_msp_id=int(template_msp_id), destination_msp_id=new_msp['id'])

