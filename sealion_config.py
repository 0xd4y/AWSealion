import argparse
from pathlib import Path
import sys
import json
import os
import shutil
from termcolor import cprint

command_arguments = sys.argv[1::1]
command = ' '.join(command_arguments)

sealion_path = os.getenv('HOME') + '/.awsealion/'
f = open(sealion_path + 'user_agent.txt','r')
default_user_agent = ''.join(f.readlines())
f.close()

data = open(sealion_path + 'engagements.json') 

try:
    engagements_data = json.load(data)
    engagements_list = engagements_data['engagements_list']
    current_engagement = engagements_data['engagement_set']
    if 'default' not in engagements_list and len(engagements_list) == 0:
        engagements_list = 'default'
        if not os.path.exists(sealion_path + 'default'):
            os.mkdir(sealion_path + 'default')
        Path(sealion_path + 'default/user_agent.txt').touch()

    elif 'default' not in engagements_list:
        engagements_list += ',default'
        if not os.path.exists(sealion_path + 'default'):
            os.mkdir(sealion_path + 'default')
        if not os.path.exists(sealion_path + 'default/user_agent.txt'):
            Path(sealion_path + 'default/user_agent.txt').touch()

    
except Exception as e:
    pass


def engagements(engagement):
    global engagement_path
    engagement = engagement[0]
    if ',' in engagement or '/' in engagement or '"' in engagement:
        cprint('[x] The "," "/" and " characters are not allowed.','red')
        sys.exit()
    engagement_path = sealion_path + engagement
    if engagement == current_engagement:
        cprint('[x] The engagement ' + engagement + ' is already set.','red')
    elif os.path.exists(sealion_path + engagement):
        cprint('[x] The following engagement was set: ' + engagement, 'blue')
        if len(engagements_list) > 0 and engagement not in engagements_list.split(','):
            engagements_data.update({"engagements_list": engagements_list + engagement})

        pass
    else:
        os.mkdir(engagement_path)
        cprint('[x] New engagement set at ' + engagement_path, 'blue')
        if len(engagements_list) > 0:
            engagements_data.update({"engagements_list": engagements_list + ',' + engagement})
        else:
            engagements_data.update({"engagements_list": engagements_list + engagement})
        
        with open(engagement_path + '/user_agent.txt','w') as user_agent_engagement_file:
            #if len(default_user_agent) == 0:
            user_agent_engagement_file.write('')
            user_agent_engagement_file.close()
            #else:
             #   user_agent_engagement_file.write(default_user_agent)
              #  user_agent_engagement_file.close()

    engagements_data['engagement_set'] = engagement
    with open(sealion_path + 'engagements.json', 'w') as f:
        json.dump(engagements_data, f)
        f.close()




def delete_engagements(engagement):
    global engagements_list
    engagement = engagement[0]
    engagement_path = sealion_path + engagement + '/'
    confirmation = input('Are you sure you want to remove ' + engagement + '? [y|n]: ')
    try:
        if confirmation == 'y':
            if engagement == engagements_data['engagement_set']:
                engagements_data['engagement_set'] = 'default'
            engagements_list_temp = engagements_list.split(',')
            delete_engagement_index = engagements_list_temp.index(engagement)
            del engagements_list_temp[delete_engagement_index]
            engagements_list = ','.join(engagements_list_temp)
            cprint('[x] The following engagement was deleted: ' + engagement, 'red')
            with open(sealion_path + 'engagements.json', 'w') as f:
                engagements_data['engagements_list'] = engagements_list
                json.dump(engagements_data, f)
        else:
            cprint('[x| Deletion canceled.','blue')

        if os.path.exists(sealion_path + engagement):
            shutil.rmtree(sealion_path+engagement)
    except ValueError:
        cprint('[x] The engagement ' + engagement + ' was not found.','red')

def list_engagement():
    if len(engagements_list) == 0:
        print('No current engagements.')
    elif len(engagements_list) == 1:
            print('*** Current engagement:', engagement + ' ***')
    else:
        cprint('[x| Engagements: ', 'blue')
        for engagement in engagements_list.split(','):
            if engagement == engagements_data['engagement_set']:
                cprint('* ' + engagement, 'green')
            else:
                print(engagement)

def select_regions(regions):
    if ',' in regions[0]:
        regions = regions[0].split(',')

    with open(sealion_path + current_engagement + '/selected_regions.txt','w') as f:
        for region in regions:
            f.write(region +'\n')
        f.close()
    cprint('[x] The following regions were set: ' + ' '.join(regions) + '','blue')

def select_user_agent(set_user_agent):
    if set_user_agent[0] in engagements_list:
        engagement = set_user_agent[0]
        user_agent = set_user_agent[1]
    elif set_user_agent[1] in engagements_list:
        engagement = set_user_agent[1]
        user_agent = set_user_agent[0]
    else:
        cprint('[x] The specified engagement was not found. The following are all the engagements.\n','red')
        list_engagement()
        sys.exit()

    if not os.path.exists(sealion_path + current_engagement):
        confirmation = input('The profile directory ' + engagement_path + profile + ' was not found. Are you sure this is the correct profile and would like to proceed? [y|n]: ')
        if confirmation == 'y':
            os.mkdir(sealion_path + current_engagement)
        else:
            sys.exit()
    with open(sealion_path + current_engagement + '/user_agent.txt','w') as agent_file:
        agent_file.write(user_agent)
        agent_file.close()
        cprint('[x] Set user agent "' + user_agent + '" at ' + sealion_path + current_engagement + '/user_agent.txt','blue')

def select_profile_user_agent(set_user_agent):
    list_engagement()
    engagement = input('[ENGAGEMENT]: ')
    if not os.path.exists(sealion_path + engagement):
        cprint('[x] ' + engagement + ' does not exist. It can be created with "aws sealion --set-engagement <ENGAGEMENT_NAME>"','red')
        sys.exit()
    profile = input('[PROFILE]: ')

    engagement_path = sealion_path + engagement
    if not os.path.exists(engagement_path + '/' + profile):
        confirmation = input('The profile directory ' + engagement_path + '/' + profile + ' was not found. Are you sure this is the correct profile and would like to proceed? [y|n]: ')
        if confirmation == 'y':
            os.makedirs(engagement_path + '/' +  profile)
        else:
            sys.exit()
    set_user_agent = input('[USER_AGENT]: ')

    with open(sealion_path + engagement + '/' + profile + '/user_agent.txt','w') as agent_file:
        agent_file.write(set_user_agent)
        agent_file.close()
    cprint('[x] User agent ' + set_user_agent + ' set for profile ' + profile + '. You currently have the ' + current_engagement + ' engagement set. If you would like to change the engagement, use "aws sealion --set-engagement <ENGAGEMENT_NAME>"','green')

def set_default_agent(master_user_agent):
    master_user_agent = master_user_agent[0]
    with open(sealion_path + 'user_agent.txt','w') as f:
        f.write(master_user_agent)
        f.close()
    cprint('The user agent ' + master_user_agent + ' is now the default user agent.','green')

parser = argparse.ArgumentParser(description = '\nEngagements can be found in the following directory: ' + sealion_path, epilog='[x] Example Usage:\naws sealion --set-engagement project_name\naws sealion --delete-engagement project_name\naws sealion --list-engagements\naws sealion --set-regions us-east-1 us-east-2 us-west-1 us-west-2\naws sealion --set-user-agent my_engagement "aws-cli/1.16.145 Python/3.6.7 Linux/4.15.0-45-generic botocore/1.12.168"\naws sealion --set-profile-user-agent\naws sealion --set-default-user-agent "my_user_agent"', formatter_class=argparse.RawTextHelpFormatter)
 #parser.add_argument('args', nargs=argparse.REMAINDER, help=argparse.SUPPRESS)
parser.add_argument('--set-engagement', type=str, metavar = '', help='Sets the current engagement. Creates an engagement if it does not yet exist.', nargs=1)
parser.add_argument('--delete-engagement', type=str, metavar = '', help='Deletes engagement and command history.', nargs=1)
parser.add_argument('--list-engagements', action='store_true', help='Shows all engagements including the currently selected engagements.')
parser.add_argument('--set-regions', type=str, metavar = '', help='Selects regions to enumerate within the environment. These regions can be invoked by using "--regions selected".', nargs='+')
parser.add_argument('--set-user-agent', type=str, metavar = '', help='Sets the user agent to be used for all API calls across all profiles in a specific engagement.', nargs=2)
parser.add_argument('--set-profile-user-agent', action='store_true', help='Sets the user agent to be used for all API calls for a specific profile in a specific engagement. This user agent takes precedence over "--set-user-agent" when using the specified profile.', )
parser.add_argument('--set-default-user-agent', help='Sets the default user agent to be used if an engagement user agent and profile user agent do not exist.', nargs=1)
parser.add_argument('sealion',nargs='+', help=argparse.SUPPRESS)

args = parser.parse_args()
set_engagement = args.set_engagement
delete_engagement = args.delete_engagement
list_engagements = args.list_engagements
set_regions = args.set_regions
set_user_agent = args.set_user_agent
master_user_agent = args.set_default_user_agent
sealion = args.sealion

if '--set-engagement' in command:
    engagements(set_engagement)
elif '--delete-engagement' in command:
    delete_engagements(delete_engagement)
elif '--list-engagements' in command:
    list_engagement()
elif '--set-regions' in command:
    select_regions(set_regions)
elif '--set-user-agent' in command:
    select_user_agent(set_user_agent)
elif '--set-profile-user-agent' in command:
    select_profile_user_agent(set_user_agent)
elif '--set-default-user-agent' in command:
    set_default_agent(master_user_agent)


if len(command_arguments) == 0 or command_arguments[-1] == 'sealion':
    cprint('Created by: Segev Eliezer (0xd4y) | https://www.linkedin.com/in/SegevEliezer\n','blue')
    parser.print_help()
