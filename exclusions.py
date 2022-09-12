import urllib3.util.ssltransport

API_KEY = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2NDgyMDU3NTIsIm5iZiI6MTY0ODIwNTc1MiwianRpIjoiNDc2NGIyYzctNWNhYy00NmQxLTkwNDMtZWYwYzRkNmE1YmMxIiwiaWRlbnRpdHkiOnsia2V5Ijo1NH0sImZyZXNoIjpmYWxzZSwidHlwZSI6ImFjY2VzcyJ9.vQFr-iLznkKkoHlUAXdOB3SIgm4-ei3hgl6hX8sQkgM'
API_ROOT = 'https://selab.customers.deepinstinctweb.com/api/v1'
import requests
import argparse
import json

auth_header = {'Authorization': API_KEY}


def read_json(file):
    with open(file) as openfile:
        output = json.loads(openfile.read())
    return output


def get_msps():
    msps = requests.get(url=f'{API_ROOT}/multitenancy/msp/',
                        headers=auth_header)

    if msps.ok:
        return msps.json()['msps']
    else:
        print(f'Error: {msps.content}')


def select_msp(msps, args):
    if 'msp_filter' in args:
        msps = [s for s in msps if args['msp_filter'].lower() in s['name'].lower()]
    msps_sorted = sorted(msps, key=lambda d: d['name'].lower())
    print(f'{"MSP Name": >25}  MSP ID')
    for n in msps_sorted:
        print(f'{n["name"]: >25}: {n["id"]}')


def get_policies(msp_id):
    policies = requests.get(url=f'{API_ROOT}/policies/',
                            headers=auth_header)
    policies = [s for s in policies.json() if(int(s['msp_id']) == int(msp_id))]

    print(f'{"ID": >6}  Policy Name')
    for n in policies:
        print(f'{n["id"]: >6}: {n["name"]}')


def define_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("-msp", "--mspfilter", dest="msp_filter", help="Filter the MSP list")
    return parser


def define_exclusions():
    available_exclusions = read_json('exclusions.json')
    print(f'{"ID": >3}  Product Name')
    for n in available_exclusions:
        print(f'{n["id"]: >3}: {n["name"]}')


def retrieve_args(args):
    response = {}
    if args.msp_filter:
        response['msp_filter'] = args.msp_filter

    return response


def apply_exclusions(policy_ids, exclusion_id):
    policy_ids = list(policy_ids.split(','))
    policy_ids = [s.strip() for s in policy_ids]

    exclusions = read_json('exclusions.json')
    exclusions = next((s for s in exclusions if s['id'] == exclusion_id), None)
    current_exclusions = exclusions['exclusions']
    if 'folder_path' in current_exclusions:
        paths_to_add = {'items': []}
        for n in current_exclusions['folder_path']:
            paths_to_add['items'].append({'comment': f'{exclusions["name"]} - API', 'item': n})
        for n in policy_ids:
            r = requests.post(url=f'{API_ROOT}/policies/{n}/exclusion-list/folder_path',
                          headers=auth_header,
                          json=paths_to_add)
            if r.ok:
                print('Folder Paths added')
            else:
                print('Error adding Folder Paths')
    if 'process_path' in current_exclusions:
        paths_to_add = {'items': []}
        for n in current_exclusions['process_path']:
            paths_to_add['items'].append({'comment': f'{exclusions["name"]} - API', 'item': n})
        for n in policy_ids:
            r = requests.post(url=f'{API_ROOT}/policies/{n}/exclusion-list/process_path',
                          headers=auth_header,
                          json=paths_to_add)
            if r.ok:
                print('Process Paths added')
            else:
                print(f'Error adding process paths')


if __name__ == '__main__':
    parser = define_args()
    args = retrieve_args(parser.parse_args())
    define_exclusions()
    selected_exclusion = input('Enter ID of exclusion: ')
    msps = get_msps()
    select_msp(msps, args)
    selected_msp = input('Enter MSP ID: ')
    get_policies(selected_msp)
    selected_policies = input('Policies to apply to (comma seperated): ')
    apply_exclusions(selected_policies, selected_exclusion)


