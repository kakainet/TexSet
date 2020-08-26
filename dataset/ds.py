import random
import string
import argparse
import sys


def color_wrap(r, g, b):
    return fR'\\color[rgb]{{ {r}, {g}, {b} }}'


def mul():
    return R'\cdot'


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


inline_binary = {'{0}+{1}', '{0}-{1}', R'{0} \cdot {1}'}
binary = inline_binary | {R'\frac{{ {0} }}{{ {1} }}'}
unary = {R'\sqrt{{ {0} }}', R'\int {0} ', R'\left({0}\right)',
         R'f\left({0}\right)', R'F\left({0}\right)', R'G\left({0}\right)'}

opcodes = set(binary | unary)
letters = 'xyabcd'
symbols = string.digits + letters


def color_expr(expr, c):
    return R'{{\color[rgb]{{ {0} }} {1} }}'.format(c, expr)


def randbool(f):
    return random.randint(0, 100) < f * 100


def atom():
    if randbool(0.5):
        return f'{random.choice(symbols)}{random.choice(letters)}'
    else:
        return f'{random.choice(symbols)}'


def single(depth, forbidden_ops=None):
    if randbool(0.3) or depth == 1:
        return atom()

    allowed_ops = opcodes if not forbidden_ops else opcodes - forbidden_ops

    return random.choice(tuple(allowed_ops)).format(single(depth - 1),
                                                    single(depth - 1))


def sample(k, d):
    for _ in range(k):
        c1, c2 = '1,0,0', '0,0,1'
        s1, s2 = single(d, forbidden_ops=inline_binary), single(d)
        bop = random.choice(tuple(binary))
        yield bop.format(
            color_expr(s1, c1), color_expr(s2, c2)
        ), bop.format(s1, s2), bop


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--samples', help='number of samples', required=True,
                        type=int)
    parser.add_argument('--max_depth', help='max allowed depth of LaTeX tree',
                        required=True, type=int)
    parser.add_argument('--ops_path', help='optional operator labels path',
                        required=False, type=str)

    cmd_args = parser.parse_args()
    opcode_labels = []

    for expr, expr_no_color, opcode in sample(cmd_args.samples,
                                              cmd_args.max_depth):
        print(expr)
        eprint(expr_no_color)
        opcode_labels.append(opcode)

    if cmd_args.ops_path:
        with open(cmd_args.ops_path, 'w') as ops_file:
            ops_file.writelines(opcode_labels)
