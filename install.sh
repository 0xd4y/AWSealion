#!/bin/bash
: '
This bash script puts the following Python code in your AWS session.py file. This code allows you to create a file ~/.awsealion/user_agent.txt which will act as the user agent for all your AWS API calls.

try:
    with open(os.getenv("HOME") + "/.awsealion/user_agent.txt","r") as user_agent_file:
        user_agent = user_agent_file.read().strip()
        user_agent_file.close()
        if len(user_agent) != 0:
            base = user_agent
except Exception:
    pass

'

pip install -r requirements.txt
chmod +x AWSealion.py
mkdir $HOME"/.awsealion" 2>/dev/null
mkdir $HOME"/.awsealion/default" 2>/dev/null
touch $HOME"/.awsealion/default/user_agent.txt"
echo 'test' >  ~/.awsealion/user_agent.txt
echo '{"engagement_set": "default", "engagements_list": "default"}' > ~/.awsealion/engagements.json
sealion_location=$(readlink -f AWSealion.py)
python=$(which python3)

# If python3 in PATH
if [ ! -z "$python" ]; then
				:
# If python3 not in PATH check if python is
else
				python=$(which python)
fi

session_file_location=$($python -c "import boto3;print(boto3.__file__)"|awk -F "boto3" '{print $1}')
session_file_location=$session_file_location"botocore/session.py"

# Had to create a second function because sed was being weird with indentation.
write_user_agent_2 () {
				base_line=$(grep "return base" $1 -n 2>&1|awk -F: {'print $1'})
				## Not the cleanest looking, but this code is run once and it works.
				### Line 1
				sed -i ${base_line}$'i \
        try:' $1
				base_line="$(($base_line+1))"
				### Line 2
				sed -i ${base_line}$'i \
            with open(os.getenv("HOME") + "/.awsealion/user_agent.txt","r") as user_agent_file:' $1
				base_line="$(($base_line+1))"
				### Line 3
				sed -i ${base_line}$'i \
                user_agent = user_agent_file.read().strip()' $1
				base_line="$(($base_line+1))"
				### Line 4
				sed -i ${base_line}$'i \
                user_agent_file.close()' $1
				base_line="$(($base_line+1))"
				### Line 5
				sed -i ${base_line}$'i \
                if len(user_agent) != 0:' $1
				base_line="$(($base_line+1))"
				### Line 6
				sed -i ${base_line}$'i \
                    base = user_agent' $1
				base_line="$(($base_line+1))"
				### Line 7
				sed -i ${base_line}$'i \
        except Exception:' $1
				base_line="$(($base_line+1))"
				### Line 8
				sed -i ${base_line}$'i \
            pass' $1
}

write_user_agent () {
				# If the botocore file was not already manipulated with sealion
				if ! grep -q 'awsealion/user_agent.txt' "$session_file_location"; 
				then
								write_user_agent_2 $session_file_location
				fi
}

if [ -f $session_file_location ];
then
				echo ''
				echo "[x] Attempting to write AWSealion code in the botocore session.py file located at "$session_file_location" for user agent manipulation."
				write_user_agent
				# Editing botocore file so that the user agent is read from ~/.awsealion/user_agent.txt
				if [ "$($python -c "import boto3;print(boto3.session.Session()._session.user_agent())")" = 'test' ]; then					
								echo "[x] Creating an alias for AWSealion in $HOME/.bashrc so that it can be run with 'aws'."
								echo 'alias aws='$sealion_location >> $HOME"/.bashrc"
								echo "[x] AWSealion was successfully installed."
				else
								echo "The path to the used botocore session.py file could not be found. Please see the README file."
				fi
fi

echo '' > $HOME"/.awsealion/user_agent.txt"
