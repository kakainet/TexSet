import subprocess
import argparse
import json
import shutil

def load_config():
    with open(args.config, 'r+') as json_config:
        return json.load(json_config)


def generate_inputs():
    for f in output_files:
            subprocess.run(["ds.py", "--max_depth", cfg['max-depth'], "--samples", cfg["samples-in-part"]], stdout=f) 

def copy_black_inputs():
    pass

def generate_images():
    pass

def prepare_output():
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='config file', required=True, type=str)
    args = parser.parse_args()

    cfg = load_config()
    output_files = [open(os.path.join('dataset/latex2image/src', f'input{j}.in'), 'w+') for j in range(cfg['parts'])]

   
    generate_inputs()
    copy_black_inputs()
    generate_images()
    prepare_output()




