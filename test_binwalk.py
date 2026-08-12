import subprocess
p = subprocess.Popen(['binwalk', '--run-as=root', '-e', '/usr/bin/ls'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
stdout, stderr = p.communicate()
print('STDOUT:', stdout)
print('STDERR:', stderr)
