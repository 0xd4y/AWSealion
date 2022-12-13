#!/usr/bin/env python3

###############################################################################################
# Created by: vaSegev Eliezer
# LinkedIn: https://www.linkedin.com/in/Segev-Eliezer/
# YouTube: https://YouTube.com/@0xd4y
# This tool is made to help you keep stealthy, organized, and efficient during AWS engagements.
###############################################################################################

import signal
import boto3
import botocore
import sys
import re
from subprocess import PIPE, STDOUT, Popen, call
import os
import json
from termcolor import cprint
from pathlib import Path

tool_arguments = ['--all-regions', '--regions'] # Could potentially be deprecated. Note to self.

command_arguments = sys.argv[1::1]

# Command before try-block manipulation
command_temp = ' '.join(command_arguments)

## Puts help text in paginator just like actual aws binary
if 'help' in command_arguments:
    help_index = command_arguments.index('help')
    if '--' != command_arguments[help_index - 1][:2]:
        command = 'aws ' + command_temp
        os.system(command)
        sys.exit()

# So that the first two arguments are the service and the argument. This avoids breaking the directory and file structure.
try:
    while '-' == command_arguments[0][0]:
        argument = command_arguments.pop(0)
        if argument != '--all-regions':
            argument_value = command_arguments.pop(0)
        command_arguments.append(argument)
        command_arguments.append(argument_value)
    profile_index = command_arguments.index('--profile')
    profile_argument = command_arguments.pop(profile_index)
    profile = command_arguments.pop(profile_index)
    command_arguments.append(profile_argument)
    command_arguments.append(profile)
except Exception as e:
    ## If no profile is specified, use the default profile, but ignore this if the user just wants to configure things
    if len(command_arguments) > 0 and 'sealion' not in command_arguments:
        profile = 'default'
        command_arguments.append('--profile')
        command_arguments.append(profile)

if '--all-regions' in command_arguments and any(argument in command_arguments for argument in ['--regions','--region']):
    cprint('Cannot use --all-regions with another region argument.','red')
    sys.exit()

command = ' '.join(command_arguments)
if len(command_arguments) == 2:
    if 'configure' == command_arguments[0] or 'configure' == command_arguments[1]:
        os.system('aws ' + command)
        sys.exit()

## To avoid freezing bug
if 'ssm' in command_arguments and 'start-session' in command_arguments:
        if '--force' in command_arguments:
            force_index = command_arguments.index('--force')
            del command_arguments[force_index]
            command = ' '.join(command_arguments)
        os.system('aws ' + command)
        sys.exit()

sealion_path = os.getenv('HOME') + '/.awsealion/'
data = open(sealion_path + 'engagements.json')

if 'sealion' in command_arguments:
    import sealion_config
    sys.exit()

default_user_agent = ''.join(open(sealion_path + 'user_agent.txt').readlines())

if len(command_arguments) == 0:
    cprint('[x] Type "aws sealion" to see configuration options.','blue')
    print('This tool is designed to keep you stealthy, organized, and efficient during pentesting. All command outputs are saved in ' + sealion_path + '\n')
    cprint('[x] Tool arguments','blue')
    cprint('--regions','green')
    print('\tAllows enumeration of multiple regions. For example "--regions us" enumerates all us regions, "--regions eu" enumerates all eu regions, etc. Region enumeration can be customized with "' + 'aws sealion --selected-regions region_name1 region_name2 region_name3" and executed with "--regions selected".\n')
    cprint('--all-regions','green')
    print('\tAllows enumeration of all aws regions.\n')
    cprint('--force','green')
    print('\tThis argument lets you run a command even though it was already executed.\n')

    command_output = os.popen('aws').read()
    print(command_output)
    sys.exit()

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
        Path(sealion_path + 'default/user_agent.txt').touch()

except Exception as e:
    pass

boto3_user_agent = boto3.session.Session()._session.user_agent()

try:
    if os.path.exists(sealion_path + current_engagement + '/' + profile + '/user_agent.txt'):
        with open (sealion_path + current_engagement + '/' + profile + '/user_agent.txt','r') as user_agent_file:
            user_agent = user_agent_file.read().strip()
            user_agent_file.close()
    else:
        with open (sealion_path + current_engagement + '/user_agent.txt','r') as user_agent_file:
            user_agent = user_agent_file.read().strip()
            user_agent_file.close()



except Exception as e:
    user_agent = boto3_user_agent

def pentest_user_agent(user_agent):
    bad_user_agents=['kali','parrot','pentoo']
    try:
        with open(sealion_path + current_engagement + '/ignore_pentest_user_agent.txt','r') as pen_user_agent:
            confirmation = pen_user_agent.readlines()
            confirmation = confirmation[0].strip()
            pen_user_agent.close()
        if len(user_agent) == 0 and len(default_user_agent.strip()) == 0:
            if any(bad_user_agent in boto3_user_agent for bad_user_agent in bad_user_agents) and confirmation != 'y':
                cprint('[x] Detected pentesting distro user agent. \nChange this with \'aws sealion --set-user-agent ' + current_engagement + ' "aws-cli/1.16.145 Python/3.6.7 Linux/4.15.0-45-generic botocore/1.12.168"\' or any user agent of your choice.\n', 'red')
                return True

    except Exception as e:
        if len(user_agent) == 0 and len(default_user_agent.strip()) == 0:
            user_agent = default_user_agent
            confirmation = ''
            if any(bad_user_agent in boto3_user_agent for bad_user_agent in bad_user_agents):
                cprint('[x] Detected pentesting distro user agent. \nChange this with \'aws sealion --set-user-agent ' + current_engagement + ' "aws-cli/1.16.145 Python/3.6.7 Linux/4.15.0-45-generic botocore/1.12.168"\' or any user agent of your choice.\n', 'red')
                confirmation = input('Are you sure you want to proceed? Type y to proceed and ignore these warnings, w to proceed and continue receiving these warnings, or n to cancel the API call. [y|w|n]: ')
                if confirmation == 'y' or confirmation == 'w':
                    with open(sealion_path + current_engagement + '/ignore_pentest_user_agent.txt','w') as pen_user_agent:
                        if confirmation == 'y':
                            pen_user_agent.write('y')
                        else:
                            pen_user_agent.write('w')
                        pen_user_agent.close()
                    return True
                else:
                    sys.exit()

pentest_user_agent_bool = pentest_user_agent(user_agent) # Check if pentest distro is being used

# Master agent file is read by the botocore library.
with open(sealion_path + 'user_agent.txt','w') as master_user_agent_file:
    if not pentest_user_agent_bool and len(user_agent) > 0:
        master_user_agent_file.write(user_agent)
    else:
        master_user_agent_file.write(default_user_agent)
    master_user_agent_file.close()

regions = ["us-east-1","us-east-2","us-west-1","us-west-2","eu-west-1","eu-west-2","eu-west-3","eu-central-1","eu-north-1","eu-south-1","af-south-1","ap-east-1","ap-northeast-1","ap-northeast-2","ap-northeast-3","ap-south-1","ap-southeast-1","ap-southeast-2","ap-southeast-3","ca-central-1","cn-north-1","cn-northwest-1","me-south-1","sa-east-1","us-gov-east-1","us-gov-west-1"]
us_regions = ["us-east-1","us-east-2","us-west-1","us-west-2","us-gov-east-1","us-gov-west-1"]
eu_regions = ["eu-west-1","eu-west-2","eu-west-3","eu-central-1","eu-north-1","eu-south-1"]
ap_regions = ["ap-east-1","ap-northeast-1","ap-northeast-2","ap-northeast-3","ap-south-1","ap-southeast-1","ap-southeast-2","ap-southeast-3"]
cn_regions = ["cn-north-1","cn-northwest-1"]

if '--regions selected' in ' '.join(command_arguments):
    try:
        selected_regions = open(sealion_path + current_engagement + '/selected_regions.txt').read()
        selected_regions = selected_regions.replace('\n', ' ').split()
    except FileNotFoundError:
        cprint('[x] The file ' + sealion_path + current_engagement + '/selected_regions.txt does not exist.\nUse "aws sealion --set-regions region_name1 region_name2 region_name3" before running this command.','red')
        sys.exit()

try:
    profile_session = boto3.session.Session(profile_name=profile)
    profile_default_region = profile_session.region_name
    if profile_default_region is None:
        profile_default_region = '' # So that you can concatenate it to a string
except:
    if 'configure' not in command_arguments:
        print('The config profile ('+profile+') could not be found')
        sys.exit()
    pass

if len(command_arguments) == 1:
    os.popen('aws').read()
    sys.exit()


command_arguments_temp = command_arguments.copy()

## Makes directories, so the necessary json and txt files can be written without errors
def make_directories():
    if not os.path.exists(sealion_path + current_engagement + '/' + profile):
        os.makedirs(sealion_path + current_engagement + '/' + profile)
    if not os.path.exists(sealion_path + current_engagement + '/' + profile + '/' + command_arguments[0]):
        os.makedirs(sealion_path + current_engagement + '/' + profile + '/' + command_arguments[0])
    if not os.path.exists(sealion_path + current_engagement + '/' + profile + '/command_history/'):
        os.makedirs(sealion_path + current_engagement + '/' + profile + '/command_history')

def error(error):
    if error == "no_region" or region == '--profile': ## when no region is specified, the region may be --profile
        sys.exit("You have not inputted a value for --regions")
    elif error == "invalid_region":
        sys.exit(f'''You have inputted {region} which is not a valid region. The following are valid regions:\n
        us
        eu
        ap
        cn
        selected
        us-east-1
        us-east-2
        us-west-1
        us-west-2
        us-gov-west-1
        us-gov-west-2
        ca-central-1
        eu-north-1
        eu-west-1
        eu-west-2
        eu-west-3
        eu-central-1
        eu-south-1
        ap-northeast-1
        ap-northeast-2
        ap-northeast-3
        ap-southeast-1
        ap-southeast-2
        ap-southeast-3
        ap-east-1
        ap-south-1
        sa-east-1
        me-south-1
        cn-north-1
        cn-northwest-1
        ''')

if '--regions' in command_arguments:
    regions_index = command_arguments.index('--regions')
elif '--all-regions' in command_arguments:
    regions_index = command_arguments.index('--all-regions')
elif '--selected-regions' in command_arguments:
    regions_index = command_arguments.index('--selected-regions')
elif '--region' in command_arguments:
    regions_index = command_arguments.index('--region')
    region_value_temp = command_arguments[regions_index+1]
    ## Ensures that the user does not make an unnecessary API call if the region does not exist
    if '--region' in command_arguments and region_value_temp not in regions and not re.search('^(us|ap|eu|cn|selected)$', region_value_temp):
        confirmation = input('[x] ' + region_value_temp + ' is not a typical region. Are you sure you want to continue with this API call? [y|n]: ')
        if confirmation != 'y':
            sys.exit()

# Checks if a command was already executed. Prints the output of the command from a local file if it was already executed.
def already_executed(command):
    if '--force' in command_arguments:
        return False
    try:
        with open(sealion_path + current_engagement + '/' + profile + '/command_history/' + command_arguments[0] + ".json","r") as fj:

            ## So that when the user reviews the command later, they can see the full command rather than just the arguments
            if command[:3] != 'aws':
                command = 'aws ' +command

            same_command_test = command + ' --region ' + profile_default_region
            same_command_test = set(same_command_test.split()) ## Takes into account the profile's default region. Using a set so the order does not matter



            ## Sets were used to make sure two commands are the same regardless of the order of the arguments
            command_history = json.load(fj)
            for key, value in command_history.items():
                key_temp = key + ' --region ' + profile_default_region
                if command == key or same_command_test == set(key.split()) or command[4:] == key or same_command_test == set(key_temp.split()): # [4:] beause the first four characters are aws[:space:]
                    print('{\n    "AlreadyExecutedCommand": "'+command+'"\n}\n')
                    try:
                        if "error" in value:
                            print(value, file=sys.stderr)
                    except BrokenPipeError: # If user appends command with |less but does not scroll through entire output
                        pass
                    return True
    except FileNotFoundError as e:
        return False

## Writes the output of the command so that it can be referenced later.
def write_command(command, command_output):
    make_directories()
    json_file = sealion_path + current_engagement + '/' + profile + '/command_history/' + command_arguments[0] + ".json" ## File containing program-readable command history
    command_file = sealion_path + current_engagement + '/' + profile + '/' + command_arguments[0] + '/' + command_arguments[1] + ".txt" ## File containing human-readable command history
    FileNotFound = False
    try:
        with open(json_file,"r") as fjr:
            history = json.load(fjr)
    except Exception as e:
       
        FileNotFound = True
        pass

    with open(json_file,"w") as fjw:
        if FileNotFound:
            command_history_write = json.dumps({command: command_output}) # writes dictionairy with the command as the key and its output as the value
            fjw.write(command_history_write)
        else:
            history[f'{command}'] = command_output # appends a key and value to the command history file
            json.dump(history, fjw)
    with open(command_file,"a") as fw:
        if 'aws' != command[:3]:
            fw.write('{\n    "Command": "aws '+command+ '"\n}\n') #writes command and its output to a readable txt file for later review by the pentester.
        else:
            fw.write('{\n    "Command": "'+command+ '"\n}\n') #writes command and its output to a readable txt file for later review by the pentester.
        fw.write(command_output)
        fw.close()

# Executes AWS commands
def aws_execute(region):
    error = False # For outputting to stderr purposes
    global stderr
    if '--force' in command_arguments_temp:
        force_index = command_arguments_temp.index('--force')
        command_arguments_temp.pop(force_index)
    regions_index = command_arguments_temp.index('--region')
    command_arguments_temp[regions_index+1] = region
    command = 'aws ' + ' '.join(command_arguments_temp)  
    if region in regions:
        if not already_executed(command) or '--force' in command_arguments:
            print('{\n    "Region":"' + region + '"\n}')
            p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
            command_output,aws_error = p.communicate() # Ensures the output is printed out even if there is an error
            aws_error = aws_error.decode('utf-8')

            ## If the command is invalid
            if 'To see help text, you can run:' in aws_error or 'You must specify a region' in aws_error or 'Unknown output type:' in aws_error or 'Unable to locate credentials.' in aws_error:
                error = True
                command_output = aws_error

            ## If the command is valid, but there is some error like unauthorized
            elif len(aws_error) > 0 and 'To see help text, you can run:' not in aws_error:
                error = True
                command_output = aws_error
                write_command(command,command_output)
            else:
                command_output = command_output.decode('utf-8')
                write_command(command,command_output)

            if error == True:
                print(command_output, file=sys.stderr)
            else:
                print(command_output)


# If the user accidentally typed in --region when they meant --regions
if re.search('--region (us|ap|eu|cn|selected)[^\w-]', ' '.join(command_arguments)):
    confirmation = input('You typed in "--region". Did you mean "--regions"? [y|n]: ')
    if confirmation == 'y':
        regions_index = command_arguments.index('--region')
        command_arguments[regions_index] = '--regions'

        if command_arguments[regions_index+1] == 'selected':
            try:
                selected_regions = open(sealion_path + current_engagement + '/selected_regions.txt').read()
                selected_regions = selected_regions.replace('\n', ' ').split()
            except FileNotFoundError:
                cprint('[x] The file ' + sealion_path + current_engagement + '/selected_regions.txt does not exist.\nUse "aws sealion --set-regions region_name1 region_name2 region_name3" before running this command.','red')
                sys.exit()


if '--regions' in command_arguments:
    try:
        for region in command_arguments_temp[regions_index+1].split(','):
            if region not in regions and not re.search('^(us|ap|eu|cn|selected)$',region):
                error("invalid_region")

        regions_value = command_arguments_temp[regions_index+1]
        command_arguments_temp[regions_index] = "--region"

        if regions_value == 'us':
            for region in us_regions:
                aws_execute(region)
        if regions_value == 'eu':
            for region in eu_regions:
                aws_execute(region)
        if regions_value == 'ap':
            for region in ap_regions:
                aws_execute(region)
        if regions_value == 'cn':
            for region in cn_regions:
                aws_execute(region)

        if regions_value == 'selected':
            for region in selected_regions:
                aws_execute(region)

        for region in command_arguments[regions_index+1].split(','):
            aws_execute(region)

    except IndexError:
        error("no_region")


signal.signal(signal.SIGINT, lambda x, y: sys.exit(0)) ## Allows user to quickly Ctrl-C to stop API calls for a list of regions
if '--all-regions' in command_arguments:
    # Making sure --all-regions is the last argument so that it is easy to insert a region value without messing up other arguments
    regions_index = command_arguments_temp.index('--all-regions')
    all_regions = command_arguments_temp.pop(regions_index)
    command_arguments_temp.append(all_regions)
    command_arguments_temp.append('')
    regions_index = command_arguments_temp.index('--all-regions')
    command_arguments_temp[regions_index] = "--region"
    for region in regions:
        aws_execute(region)



## If none of the special sealion arguments are in the command
if not any(command_argument in tool_arguments for command_argument in command_arguments) and not already_executed(command):
    if '--force' in command_arguments:
        force_index = command_arguments.index('--force')
        command_arguments.pop(force_index)
        command = ' '.join(command_arguments)
    if command_arguments[0] != 'aws':
        command = 'aws ' + command
    if 'configure' not in command_arguments:
        p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        command_output,aws_error = p.communicate()
        aws_error = aws_error.decode('utf-8')
        command_output = command_output.decode('utf-8')
    else:
        os.system(command)
        sys.exit()
    if 'To see help text, you can run:' in aws_error or 'You must specify a region' in aws_error or 'Unknown output type:' in aws_error or 'Unable to locate credentials.' in aws_error:
        command_output = aws_error
        error = True
    elif len(aws_error) > 0 and 'aws: error:' not in aws_error:
        error = True
        command_output = aws_error
        write_command(command,command_output)
    elif len(aws_error) == 0:
        write_command(command,command_output)

    try:
        if error == True:
            print(command_output, file=sys.stderr)
        else:
            print(command_output)

    except BrokenPipeError: # If user appends command with |less but does not scroll through entire output
        pass

with open(sealion_path + 'user_agent.txt','w') as master_user_agent_file:
    master_user_agent_file.write(default_user_agent)
    master_user_agent_file.close()
