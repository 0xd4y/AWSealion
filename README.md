<p align="center">
  <img src="https://user-images.githubusercontent.com/77868212/190444390-01be54f7-7b21-4d87-a7fa-5f8b894be341.png">
</p>

#
:link: You can contact me on the following platforms:<br>
LinkedIn - https://www.linkedin.com/in/segev-eliezer/<br>
YouTube - https://www.youtube.com/channel/UCSumP9z5Rzquqih-jpusTOQ


## Description
AWSealion is a CLI tool designed to work as a plugin for the AWS CLI to be used by pentesters and security enthusiasts in both professional and CTF settings. This tool helps in staying stealthy during red team and pentesting engagements to ensure that your attacking footprint is as small as possible in an AWS environment. 

AWSealion works through not allowing the same API call to be run twice, allowing user-agent customization in a per-engagement and per-profile basis, saving the output of all API calls, and much more. Furthermore, the AWSealion tool creates an organized file structure which the user can easily reference, ensuring that you do not drift away from your commands.



## Key Features
- User-agent customization on a per-engagement and per-profile basis
- Saving output of all API calls 
- Detects duplicate commands and reads the output of the API call from memory rather than passing the command to the AWS API
- Allows enumeration of specific regions via the --regions argument



## Installation
```bash
git clone https://github.com/0xd4y/AWSealion
bash AWSealion/install.sh
source ~/.bashrc
```

## Example Usage
![image](https://user-images.githubusercontent.com/77868212/190279321-d13e7a94-78e8-4335-8510-0e5d835b8ed9.png)
![image](https://user-images.githubusercontent.com/77868212/190280947-0ac376ee-d8f8-4dd5-926d-365bf2b1af8b.png)
![image](https://user-images.githubusercontent.com/77868212/190281101-e00fbf93-d431-4f24-a4ee-ae4bce51e750.png)


## User-Agent Manipulation Within AWSealion
The user agent is determined by the `session.py` file in the `botocore` package. By modifying the `session.py` file to read the user agent from a txt file on the local system, it is possible to change one's AWS API user agent. This allows the user to stay stealthy even when conducting API calls from a pentesting distro, therefore bypassing GuardDuty's `Pentest:` findings. 
AWSealion is configured to retrieve user agent information from `~/.awsealion/user-agent.txt`. The data in this user-agent file is constantly updated depending on the user agent set for the profile making the call, or the currently set engagement.

### Per Profile User Agent Manipulation
A user agent set for a profile takes precedence over a user agent set for an engagement.

### Per Engagement User Agent Manipulation
When configuring a user agent for an engagement, the engagement's user agent is applied to all profile in a set engagement unless a profile has an assigned specific user agent.

## Errors
If the installation script does not work, this is likely due to the script not finding where you're installed `session.py` file is. Therefore, you must find where this file is located, and input the following code right before the `return base` line:
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
