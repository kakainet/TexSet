import subprocess
import argparse
import json
import shutil
import os
import glob
import signal
import sys

ops_cfg_path = "config/operators.json"


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
def clean_old():
    if os.path.isdir(result_dir):
        shutil.rmtree(result_dir)
    os.mkdir(result_dir)


@dump_func_name
def load_config():
    with open(args.config, 'r+') as json_config:
        return json.load(json_config)


@dump_func_name
def generate_inputs():
    for j in range(len(output_files)):
        black_f = output_cp_files[j]
        color_f = output_files[j]
        subprocess.run(
            ["python3", "dataset/ds.py", f"--ops_cfg={ops_cfg_path}",
             "--max_depth", str(cfg['max-depth']),
             "--samples", str(cfg["samples-in-part"]),
             f"--ops_path=dataset/latex2image/src/input{j}.in.ops"],
            stdout=color_f,
            stderr=black_f)


@dump_func_name
def generate_images():
    os.chdir('dataset/latex2image/src')
    colorfull = glob.glob('*.in')
    black = list(map(lambda x: x+'.black', colorfull))
    subprocess.run(['bash', 'set.sh', *colorfull])
    os.rename('output', 'output_color')
    os.remove('labels.txt')
    subprocess.run(['bash', 'set.sh', *black])
    os.rename('output', 'output_black')
    os.rename('labels.txt', 'itl_labels.txt')
    # TODO: what to do with .ops files, to make them input for annotations?
    for f in black + colorfull:
        os.remove(f)


@dump_func_name
def generate_bbox():
    shutil.move('output_color', os.path.join(owd, result_dir))
    shutil.move('output_black', os.path.join(owd, result_dir))
    shutil.move('itl_labels.txt', os.path.join(owd, result_dir))

    os.chdir(owd)

    subprocess.run(['python3', 'dataset/bbox_gen.py',
                    '--in-dir', os.path.join(result_dir, 'output_color'),
                    '--out-dir', os.path.join(result_dir, 'output_bbox'),
                    '--save', os.path.join(result_dir, 'annotations.json')])


@dump_func_name
def transform_bbox():
    subprocess.run(['python3', 'toolkit/transform_dataset.py', '--input-dir',
                    'output/output_black',
                    '--dim', '224', '--annotations', 'output/annotations.json',
                    '--output-dir', 'output/output_proper'])


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    owd = os.getcwd()

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='config file',
                        required=True, type=str)

    args = parser.parse_args()
    cfg = load_config()
    result_dir = 'output'

    output_files = [open(os.path.join(
        'dataset/latex2image/src', f'input{j}.in'), 'w+') for j in
        range(cfg['parts'])]
    output_cp_files = [open(os.path.join(
        'dataset/latex2image/src', f'input{j}.in.black'), 'w+') for j in
        range(cfg['parts'])]

    clean_old()
    generate_inputs()
    generate_images()
    generate_bbox()
    transform_bbox()

    os.chdir(owd)
