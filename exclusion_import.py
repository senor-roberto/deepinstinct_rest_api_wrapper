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

# -- USAGE NOTES ---

# This script accepts a pair of input files. One for Folder Exclusions and one
# for Process Exclusions. Both input files should be single sheet (tab) OOXML
# spreadsheets.
#
# The process exclusions input file must contain the following columns. Column
# names are cASE seNSITive. Column order is irrelevant. Additional columns will
# be ignored.
#   Comment
#   Policies
#   Process
#
# The folder exclusions input file must contain the following columns. Column
# names are cASE seNSITive. Column order is irrelevant. Additional columns will
# be ignored.
#   Comment
#   Policies
#   Folder
#
# The Policies column must contain exactly one of the following:
#   The word All
#   The name of one policy
#   A list of policies delimited by <comma><space>. Example: Policy 1, Policy 2
# Note: All of the above are cASE seNSITive
#
# This input file syntax is identical to what is created if you use the GUI to
# export the exclusion lists. I suggest to take an export and then use that as
# your template.

import deepinstinct30 as di
import pandas
import time

def run_exclusion_import(fqdn, key, process_exclusions_file_name, folder_exclusions_file_name):

    start_time = time.perf_counter()

    di.fqdn = fqdn
    di.key = key

    #read exclusions from files on disk as Pandas dataframes
    process_exclusions_dataframe = pandas.read_excel(process_exclusions_file_name)
    folder_exclusions_dataframe = pandas.read_excel(folder_exclusions_file_name)

    #replace any null values with empty string to avoid subsequent errors
    process_exclusions_dataframe.fillna('', inplace=True)
    folder_exclusions_dataframe.fillna('', inplace=True)

    #convert Pandas dataframes to Python dictionaries
    process_exclusions = process_exclusions_dataframe.to_dict('records')
    folder_exclusions = folder_exclusions_dataframe.to_dict('records')

    #convert policy field from string to list
    for exclusion in process_exclusions:
        exclusion['Policies'] = exclusion['Policies'].split(", ")
    for exclusion in folder_exclusions:
        exclusion['Policies'] = exclusion['Policies'].split(", ")

    #get policy list, then filter it to get a list of just Windows policies
    all_policies = di.get_policies()
    windows_policies = []
    for policy in all_policies:
        if policy['os'] == 'WINDOWS':
            windows_policies.append(policy)

    #iterate through each of the Windows policies
    for policy in windows_policies:

        print('INFO: Beginning processing of policy', policy['id'], policy['name'])


        #PROCESS EXCLUSIONS

        #create a list to store process exclusions that apply to this policy
        process_exclusions_this_policy = []

        #iterate though the imported process exclusion list
        for exclusion in process_exclusions:
            #check if the exclusion applies to all policies
            if exclusion['Policies'] == ['All']:
                process_exclusions_this_policy.append(exclusion)
            #check if the exclusion applies to this specific policy
            elif policy['name'] in exclusion['Policies']:
                process_exclusions_this_policy.append(exclusion)

        #if we found some exclusions applicable to this policy, create them
        if len(process_exclusions_this_policy) > 0:
            print('INFO: Adding', len(process_exclusions_this_policy), 'process exclusions to policy', policy['id'], policy['name'])
            for exclusion in process_exclusions_this_policy:
                di.add_process_exclusion(exclusion['Process'], exclusion['Comment'], policy['id'])


        #FOLDER EXCLUSIONS

        #create a list to store folder exclusions that apply to this policy
        folder_exclusions_this_policy = []

        #iterate though the imported folder exclusion list
        for exclusion in folder_exclusions:
            #check if the exclusion applies to all policies
            if exclusion['Policies'] == ['All']:
                folder_exclusions_this_policy.append(exclusion)
            #check if the exclusion applies to this specific policy
            elif policy['name'] in exclusion['Policies']:
                folder_exclusions_this_policy.append(exclusion)

        #if we found some exclusions applicable to this policy, create them
        if len(folder_exclusions_this_policy) > 0:
            print('INFO: Adding', len(folder_exclusions_this_policy), 'folder exclusions to policy', policy['id'], policy['name'])
            for exclusion in folder_exclusions_this_policy:
                di.add_folder_exclusion(exclusion['Folder'], exclusion['Comment'], policy['id'])


        print('INFO: Done with policy', policy['id'], policy['name'])

    runtime_in_seconds = time.perf_counter() - start_time
    print('Runtime was', runtime_in_seconds, 'seconds.')


def main():

    #prompt for config parameters

    fqdn = input('Enter FQDN of DI Server, or press enter to accept the default [di-service.customers.deepinstinctweb.com]: ')
    if fqdn == '':
        fqdn = 'di-service.customers.deepinstinctweb.com'

    key = input('Enter API Key for DI Server: ')

    process_exclusions_file_name = input('Enter name of file containing process exclusions to import, or press enter to accept the default [process_exclusions.xlsx]: ')
    if process_exclusions_file_name == '':
        process_exclusions_file_name = 'process_exclusions.xlsx'

    folder_exclusions_file_name = input('Enter name of file containing folder exclusions to import, or press enter to accept the default [folder_exclusions.xlsx]: ')
    if folder_exclusions_file_name == '':
        folder_exclusions_file_name = 'folder_exclusions.xlsx'

    #run the import
    return run_exclusion_import(fqdn=fqdn, key=key, process_exclusions_file_name=process_exclusions_file_name, folder_exclusions_file_name=folder_exclusions_file_name)


if __name__ == "__main__":
    main()
