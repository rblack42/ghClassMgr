import subprocess

def shell(command):
    parts = command.split()
    p = subprocess.Popen(parts, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
    )
    out, err = p.communicate()
    return out
