import random
import string
import argparse
import sys

def color_wrap(r,g,b,expr):
    return fR'\\color[rgb]{{ {r}, {g}, {b} }}'

def mul():
    return '\cdot'

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

binary = [R'\frac{{ {0} }}{{ {1} }}', '{0}+{1}', '{0}-{1}', R'{0} \cdot {1}']
unary = [R'\sqrt{{ {0} }}', R'\int {0} ', R'\left({0}\right)', R'f\left({0}\right)', R'F\left({0}\right)', R'G\left({0}\right)']

op = binary+unary
letters='xyabcd'
symbols = string.digits+letters

def color_expr(expr, c):
    return '{{\color[rgb]{{ {0} }} {1} }}'.format(c, expr)

def randbool(f):
    return random.randint(0,100) < f * 100

def atom():
    if randbool(0.5):
        return f'{random.choice(symbols)}{random.choice(letters)}'
    else:
        return f'{random.choice(symbols)}'

def single(depth):
    if randbool(0.3) or depth == 1:
        return atom()
    return random.choice(op).format(single(depth-1), single(depth-1))

def sample(k, d):
    l = []
    for _ in range(k):
        c1, c2 = '1,0,0','0,0,1'
        s1, s2 = single(d), single(d)
        bop = random.choice(binary)
        yield bop.format(color_expr(s1, c1), color_expr(s2, c2)), bop.format(s1, s2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--samples', help='number of samples', required=True, type=int)
    parser.add_argument('--max_depth', help='max allowed depth of LaTeX tree', required=True, type=int)
    args = parser.parse_args()

    for expr, epxr_no_color in sample(args.samples, args.max_depth):
        print(expr)
        eprint(epxr_no_color)