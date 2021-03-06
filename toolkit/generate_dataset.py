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
        print(f"{func.__name__}... ", end='')
        res = func(*func_args, **func_kwargs)
        print('done')
        return res

    return echo_func


@dump_func_name
def clean_old():
    if os.path.isdir(result_dir):
        shutil.rmtree(result_dir)
    os.mkdir(result_dir)


@dump_func_name
def load_config():
    with open(args.job, 'r+') as json_config:
        json_data = json.load(json_config)
    return json_data


@dump_func_name
def generate_inputs():
    depth_loop = range(1, cfg['max-depth'] +
                       1) if level_aug else [cfg['max-depth']]
    for d in depth_loop:
        for j in range(cfg['parts']):
            idx = (d - min(depth_loop))*cfg['parts'] + j
            black_f = output_cp_files[j]
            color_f = output_files[j]
            cmd = ["python3", "dataset/ds.py",
                   f"--ops-cfg={ops_cfg_path}",
                   "--max-depth", str(d),
                   "--samples", str(cfg["samples-in-part"]),
                   f"--op-path=dataset/latex2image/src/input{idx}.in.op",
                   f"--depth-path=dataset/latex2image/src/input{idx}.in.depth",
                   f"--expr-path=dataset/latex2image/src/input{idx}.in.black",
                   f"--color-path=dataset/latex2image/src/input{idx}.in",
                   f"--deeper-chance={cfg['deeper-chance']}"]

            subprocess.run(cmd)


@dump_func_name
def generate_images():
    def compare(entry):
        def get_idx(entry): return int(
            entry[len('input'):entry.find('.')])
        return get_idx(entry)

    os.chdir('dataset/latex2image/src')
    colorfull = sorted(glob.glob('*.in'), key=compare)
    black = list(map(lambda x: x+'.black', colorfull))
    subprocess.run(['bash', 'set.sh', *colorfull])
    os.rename('output', 'output_color')
    os.remove('labels.txt')
    subprocess.run(['bash', 'set.sh', *black])
    os.rename('output', 'output_black')
    os.rename('labels.txt', 'itl_labels.txt')

    ops = list(map(lambda x: x+'.op', colorfull))
    dths = list(map(lambda x: x+'.depth', colorfull))

    operators = []
    depths = []
    for part_op in ops:
        with open(part_op, 'r') as partfile:
            operators += partfile.read().splitlines()

    for part_d in dths:
        with open(part_d, 'r') as partfile:
            depths += partfile.read().splitlines()

    with open('operators.txt', 'w+') as opfile:
        opfile.write(
            '\n'.join(list(filter(lambda x: x.strip() != "", operators))))

    with open('depths.txt', 'w+') as dfile:
        dfile.write(
            '\n'.join(list(filter(lambda x: x.strip() != "", depths))))

    for f in black + colorfull + ops + dths:
        os.remove(f)


@dump_func_name
def generate_bbox():
    shutil.move('output_color', os.path.join(owd, result_dir))
    shutil.move('output_black', os.path.join(owd, result_dir))
    shutil.move('itl_labels.txt', os.path.join(owd, result_dir))
    shutil.move('operators.txt', os.path.join(owd, result_dir))
    shutil.move('depths.txt', os.path.join(owd, result_dir))

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


@dump_func_name
def merge_annotations():
    # merges both labels and operators to annotations.json
    with open(os.path.join(result_dir, 'annotations.json'), 'r+') as annotfile:
        json_data = json.load(annotfile)

    with open(os.path.join(result_dir, 'itl_labels.txt'), 'r+') as labelsfile:
        labels = labelsfile.read().splitlines()

    with open(os.path.join(result_dir, 'operators.txt'), 'r+') as opfile:
        operators = opfile.read().splitlines()

    with open(os.path.join(result_dir, 'depths.txt'), 'r+') as dfile:
        depths = dfile.read().splitlines()

    for idx in range(len(json_data)):
        name = json_data[idx]['name']
        assert(int(name[len('eq'):name.find('.')]) == idx)
        json_data[idx]['label'] = labels[idx]
        json_data[idx]['op'] = operators[idx]
        json_data[idx]['depth'] = int(depths[idx])

        if labels[idx] == 'frac':
            json_data[idx]['exprs']=sorted(json_data[idx]['exprs'], key=lambda box: box[1])


    json_out = json.dumps(json_data,  indent=4)

    with open(os.path.join(result_dir, 'annotations.json'), 'w+') as annots:
        annots.write(json_out)


@dump_func_name
def augmentation():
    subprocess.run([
        'python3', 'toolkit/augmentation.py',
        f'--aug-job={args.aug_job}',
        f'--dataset={result_dir}',
        '--annots-path=output/annotations.json',
        '--rescale-config=config/rescale.json'
    ])


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    owd = os.getcwd()

    parser = argparse.ArgumentParser()
    parser.add_argument('--job', help='job config file',
                        required=True, type=str)
    parser.add_argument('--aug-job', help='job config file',
                        required=False, type=str)

    args = parser.parse_args()
    cfg = load_config()
    assert(cfg)
    print('Config loaded:', cfg)
    result_dir = 'output'
    level_aug = cfg['level-augmentation']
    limit = cfg['parts'] if not level_aug else cfg['parts'] * \
        (cfg['max-depth'] - 1)

    output_files = [open(os.path.join(
        'dataset/latex2image/src', f'input{j}.in'), 'w+') for j in
        range(limit)]
    output_cp_files = [open(os.path.join(
        'dataset/latex2image/src', f'input{j}.in.black'), 'w+') for j in
        range(limit)]

    clean_old()
    generate_inputs()
    generate_images()
    generate_bbox()
    transform_bbox()
    merge_annotations()

    if args.aug_job:
        augmentation()

    shutil.copy(args.job, result_dir)
    os.chdir(owd)
