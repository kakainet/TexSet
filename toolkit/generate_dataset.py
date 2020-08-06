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
        output_cp_files[j].write(read_files[j].read().replace('0,0,1', '0,0,0').replace('1,0,0', '0,0,0'))
    for j in range(cfg['parts']):
        output_cp_files[j].close()

@dump_func_name  
def generate_images():
    os.chdir('dataset/latex2image/src')
    colorfull = glob.glob('*.in')
    black = glob.glob('*.in.black')
    subprocess.run(['bash', 'set.sh', *colorfull])
    os.rename('output','output_color')
    os.rename('labels.txt', 'itl_labels.txt')
    subprocess.run(['bash', 'set.sh', *black])
    os.rename('output','output_black')
    os.remove('labels.txt')
    for f in black+colorfull:
        os.remove(f)

@dump_func_name
def generate_bbox():
    shutil.move('output_color', os.path.join(owd, result_dir)) 
    shutil.move('output_black', os.path.join(owd, result_dir))
    shutil.move('itl_labels.txt', os.path.join(owd, result_dir))

    os.chdir(owd)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    owd = os.getcwd()

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='config file', required=True, type=str)

    args = parser.parse_args()
    cfg = load_config()
    result_dir = 'output'

    output_files = [open(os.path.join('dataset/latex2image/src', f'input{j}.in'), 'w+') for j in range(cfg['parts'])]
    output_cp_files = [open(os.path.join('dataset/latex2image/src', f'input{j}.in.black'), 'w+') for j in range(cfg['parts'])]
    read_files = [open(os.path.join('dataset/latex2image/src', f'input{j}.in'), 'r') for j in range(cfg['parts'])]

    generate_inputs()
    copy_black_inputs()
    generate_images()
    generate_bbox()
