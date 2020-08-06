import subprocess
import argparse
import json
import shutil
import os
import glob
import signal
import sys

def signal_handler(sig, frame):
    print('Aborted')
    os.chdir(owd)
    sys.exit(0)

def dump_func_name(func):
    def echo_func(*func_args, **func_kwargs):
        print('Start func: {}'.format(func.__name__))
        return func(*func_args, **func_kwargs)
    return echo_func

@dump_func_name    
def load_config():
    with open(args.config, 'r+') as json_config:
        return json.load(json_config)

@dump_func_name  
def generate_inputs():
    for f in output_files:
        subprocess.run(["python3", "dataset/ds.py", "--max_depth", str(cfg['max-depth']), "--samples", str(cfg["samples-in-part"])], stdout=f) 
        
@dump_func_name  
def copy_black_inputs():
    for j in range(cfg['parts']):
        for c in ['0,0,1', '1,0,0']:
            output_cp_files[j].write(read_files[j].read().replace(c, '0,0,0'))

@dump_func_name  
def generate_images():
    os.chdir('dataset/latex2image/src')
    colorfull = glob.glob('*.in') 
    print(colorfull)
    subprocess.run(['bash', 'set.sh', *colorfull])

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='config file', required=True, type=str)
    args = parser.parse_args()
    owd = os.getcwd()
    cfg = load_config()

    output_files = [open(os.path.join('dataset/latex2image/src', f'input{j}.in'), 'w+') for j in range(cfg['parts'])]
    output_cp_files = [open(os.path.join('dataset/latex2image/src', f'input{j}.in.black'), 'w+') for j in range(cfg['parts'])]
    read_files = [open(os.path.join('dataset/latex2image/src', f'input{j}.in'), 'r') for j in range(cfg['parts'])]

    generate_inputs()
    copy_black_inputs()
    generate_images()

    os.chdir(owd)
