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
