# Quick script to decode batch generated samples from gpt-2-simple.
# File run in mtgencode repo dir
import os
import subprocess

file_dir = "gen"
files = os.listdir(file_dir)

for i, file in enumerate(files):
    subprocess.call(['python2.7', 'decode.py', '-e',
                     'rfields', '-g', '{}/{}'.format(file_dir, file),
                     'cards_{}.txt'.format(i)])
