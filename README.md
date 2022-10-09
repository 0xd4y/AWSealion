<p align="center">
  <img src="https://user-images.githubusercontent.com/77868212/190444390-01be54f7-7b21-4d87-a7fa-5f8b894be341.png">
</p>

#
:link: You can contact me on the following platforms:<br>
LinkedIn - https://www.linkedin.com/in/segev-eliezer/<br>
YouTube - https://www.youtube.com/channel/UCSumP9z5Rzquqih-jpusTOQ<br>
Web - https://0xd4y.com


## Description
AWSealion is a CLI tool designed to work as a plugin for the AWS CLI to be used by pentesters and security enthusiasts in both professional and CTF settings, however it can also be used by developers and security engineers to speed up their work. This tool helps in staying stealthy during red team and pentesting engagements to ensure that your attacking footprint is as small as possible in an AWS environment. 

AWSealion works through not allowing the same API call to be run twice, allowing user-agent customization on a per-engagement and per-profile basis, saving the output of all API calls, and much more. Furthermore, the AWSealion tool creates an organized file structure which the user can easily reference, ensuring that you do not drift away from your commands.

**This tool is meant to be used for legal purposes only. Misuse of this tool is strictly prohibited.**

## Key Features
:star: Detects duplicate commands and reads the output of the API call from memory rather than passing the command to the AWS API<br>
:star: User-agent customization on a per-engagement and per-profile basis<br>
:star: Saves the output of all API calls <br>
:star: Allows enumeration of multiple regions via the `--regions` and `--all-regions` arguments

## Installation
```
git clone https://github.com/0xd4y/AWSealion
cd AWSealion
bash install.sh
source ~/.bashrc
```

## Sealion Config 
```
┌─[0xd4y@Writeup]─[~/tools/AWSealion]
└──╼ $aws sealion
Created by: Segev Eliezer (0xd4y) | https://www.linkedin.com/in/SegevEliezer

usage: AWSealion.py [-h] [--set-engagement] [--delete-engagement] [--list-engagements] [--set-regions  [...]] [--set-user-agent ] [--set-profile-user-agent]
                    [--set-default-user-agent SET_DEFAULT_USER_AGENT]

Engagements can be found in the following directory: /home/0xd4y/.awsealion/

optional arguments:
  -h, --help            show this help message and exit
  --set-engagement      Sets the current engagement. Creates an engagement if it does not yet exist.
  --delete-engagement   Deletes engagement and command history.
  --list-engagements    Shows all engagements including the currently selected engagements.
  --set-regions  [ ...]
                        Selects regions to enumerate within the environment. These regions can be invoked by using "--regions selected".
  --set-user-agent      Sets the user agent to be used for all API calls across all profiles in a specific engagement.
  --set-profile-user-agent
                        Sets the user agent to be used for all API calls for a specific profile in a specific engagement. This user agent takes precedence over "--set-user-agent" when using the specified profile.
  --set-default-user-agent SET_DEFAULT_USER_AGENT
                        Sets the default user agent to be used if an engagement user agent and profile user agent do not exist.

[x] Example Usage:
aws sealion --set-engagement project_name
aws sealion --delete-engagement project_name
aws sealion --list-engagements
aws sealion --set-regions us-east-1 us-east-2 us-west-1 us-west-2
aws sealion --set-user-agent my_engagement "aws-cli/1.16.145 Python/3.6.7 Linux/4.15.0-45-generic botocore/1.12.168"
aws sealion --set-profile-user-agent
aws sealion --set-default-user-agent "my_user_agent"
```

## Example Usage
### Setting an Engagement and Profile User Agent
![image](https://user-images.githubusercontent.com/77868212/190917207-4f9eb30a-579d-43e6-ba81-0405f90bde0e.png)
![image](https://user-images.githubusercontent.com/77868212/190280947-0ac376ee-d8f8-4dd5-926d-365bf2b1af8b.png)
![image](https://user-images.githubusercontent.com/77868212/190281101-e00fbf93-d431-4f24-a4ee-ae4bce51e750.png)
- Profile user agent takes precedence over engagement user agent

### AWSealion Command Saved
![image](https://user-images.githubusercontent.com/77868212/190449067-a6907fb2-7d05-4b33-b42d-ba284fbf9ae3.png)


## User-Agent Manipulation Within AWSealion
The user agent is determined by the `session.py` file in the `botocore` package. By modifying the `session.py` file to read the user agent from a txt file on the local system, it is possible to change one's AWS API user agent. This allows the user to stay stealthy even when conducting API calls from a pentesting distro, therefore bypassing GuardDuty's `Pentest:` findings. 
AWSealion is configured to retrieve user agent information from `~/.awsealion/user-agent.txt`. The data in this user-agent file is constantly updated depending on the user agent set for the profile making the call, or the currently set engagement.

### Per Profile User Agent Manipulation
A user agent set for a profile takes precedence over a user agent set for an engagement.

### Per Engagement User Agent Manipulation
When configuring a user agent for an engagement, the engagement's user agent is applied to all profile in a set engagement unless a profile has an assigned specific user agent.

### Default User Agent Manipulation
When using the `--set-default-user-agent` argument, it is possible to set a defualt user agent that would be used across all engagements if the engagement user agent or profile user agent are not set.

### User Agent Hierarchy
1. Most important: Profile user agent
2. Less important: Engagement user agent
3. Least important: Default user agent

## Errors
If the installation script does not work, this is likely due to the script not finding where your installed `session.py` file is. Therefore, you must find where this file is located, and input the following code right before the `return base` line:
```python
try:
    with open(os.getenv("HOME") + "/.awsealion/user_agent.txt","r") as user_agent_file:
        user_agent = user_agent_file.read().strip()
        user_agent_file.close()
        if len(user_agent) != 0:
            base = user_agent
except Exception:
    pass
```
- This code reads from the `user_agent.txt` file and uses it as the user agent for the API call.

## User Agents File
This user agents file was added to give the user some quick and easy access to some example user agents. This file was taken from the Pacu tool created by RhinoSecurityLabs. All credits to this specific file go to RhinoSecurityLabs.
