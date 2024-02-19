import subprocess
import os
import json

def SCPToServer(file_to_send, sendoffjson):

    json_file = open(sendoffjson)
    json_obj = json.load(json_file)
    sendoff_con = json_obj['Username']+"@"+json_obj['Host']+":"+json_obj['Path']
    scp_proc = subprocess.Popen(['scp', file_to_send, sendoff_con])
    scp_proc.communicate()

    print('{} has transfered'.format(file_to_send))