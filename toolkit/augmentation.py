import subprocess
from subprocess import CalledProcessError
import argparse
import os
import numpy as np
import json
from uuid import uuid4


def generate_job_file(out_file_path: str, template_path: str, level: int, parts: int, samples: int):
    with open(template_path, 'r') as template_file:
        template = json.load(template_file)

    template['max-depth'] = level
    template['parts'] = parts
    template['samples-in-part'] = samples
    template['level-augmentation'] = False
    template['deeper-chance'] = 1

    with open(out_file_path, 'w+') as out_file:
        out_file.write(json.dumps(template))


def generate_aug(cfg: dict, dataset_script: str, template_path):
    multithread = cfg['parts']
    perlvl = cfg['samples-in-part-per-lvl']
    for idx, lvl in enumerate(perlvl):
        print(f'Depth {idx}: generate {lvl} samples')

        tmp_job_file = f'.job_tmp_{uuid4()}.json'
        generate_job_file(tmp_job_file, template_path, idx, multithread, lvl)
        try:
            pass
            # completed_proc = subprocess.run([
            #     'python3', dataset_script,
            #     '--job', ''
            # ])

            # completed_proc.check_returncode()
        except CalledProcessError:
            print(f'ERROR during generating depth {lvl}')
            exit(1)

        os.remove(tmp_job_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--aug-job', help='Augmentation job config file path', required=True, type=str)
    parser.add_argument(
        '--job-template', help='Template for single job config file path', required=True, type=str)
    parser.add_argument(
        '--dataset-script', help='Path to generate script', required=True, type=str)

    args = parser.parse_args()
    config_path = args.aug_job
    template_path = args.job_template
    with open(config_path, 'r') as cfg_file:
        cfg = json.loads(cfg_file.read())

    generate_aug(cfg, args.dataset_script, template_path)
