# Description
AWSealion is a CLI tool designed to work as a plugin for the AWS CLI for use by pentesters and security enthusiasts in both professional and CTF settings. This tool helps in staying stealthy during red team and pentesting engagements to ensure that your attacking footprint is as small as possible in an AWS environment. 

AWSealion works through not allowing the same API call to be run twice, allowing user-agent customization in a per-engagement and per-profile basis, saving the output of all API calls, and much more. Furthermore, the AWSealion tool creates an organized file structure which the user can easily reference.

## Key Features
- User-agent customization on a per-engagement per-profile basis
- Saving output of all API calls 
- Detects duplicate commands and reads the output of the API call from memory rather than passing the command to the AWS API
- Allows enumeration of specific regions via the --regions argument

## Installation
```
git clone https://github.com/0xd4y/AWSealion
bash AWSealion/install.sh
source ~/.bashrc
```

![image](https://user-images.githubusercontent.com/77868212/190279321-d13e7a94-78e8-4335-8510-0e5d835b8ed9.png)
![image](https://user-images.githubusercontent.com/77868212/190280947-0ac376ee-d8f8-4dd5-926d-365bf2b1af8b.png)

## How User-Agent Maniupation Works within AWSealion
The user agent is determined by the `session.py` file in the `botocore` package. By modifying the `session.py` file to read the user agent from a txt file on the local system, it is possible to change one's AWS API user agent. This allows the user to stay stealthy even when conducting API calls from a pentesting distro, therefore bypassing GuardDuty's `Pentest:` findings. 
AWSealion is configured to retrieve user agent information from `~/.awsealion/user-agent.txt`. The data in this user-agent file is constantly updated depending on the user agent set for the profile making the call, or the currently set engagement.

### Per Profile User Agent Manipulation
A user agent set for a profile takes precedence over a user agent set for an engagement.

### Per Engagement User Agent Manipulation
When configuring a user agent for an engagement, the engagement's user agent is applied to all profile in a set engagement unless a profile has an assigned specific user agent.

![image](https://user-images.githubusercontent.com/77868212/190280123-9fecb43d-a3f5-427c-95fb-6c6a4b3a7d65.png)


