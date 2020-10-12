import json
import random
import string
import argparse
import sys


def color_wrap(r, g, b):
    return fR'\\color[rgb]{{ {r}, {g}, {b} }}'


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


letters = [c for c in string.ascii_letters] + [R'\phi', R'\alpha', R'\beta', R'\gamma', R'\delta', R'\Phi', R'\Gamma', R'\Delta']
symbols = [c for c in string.digits] + letters


def color_expr(expr, c):
    return R'{{\color[rgb]{{ {0} }} {1} }}'.format(c, expr)


def randbool(f):
    return random.randint(0, 100) < f * 100


def atom():
    if randbool(0.5):
        return f'{random.choice(symbols)}{random.choice(letters)}'
    else:
        return f'{random.choice(symbols)}'


class Operator:
    def __init__(self, opcode: str, latex: str, operands: int, **kwargs):
        self.opcode = opcode
        self.latex = latex.replace('\\\\', "\\")
        self.operands = operands
        for k, v in kwargs.items():
            setattr(self, k, v)

    def is_inline(self):
        return hasattr(self, 'inline') and self.inline


class Operators:
    def __init__(self, ops: set):
        self.all = ops
        self._binary = set(filter(lambda x: x.operands == 2, self.all))
        self._inline_binary = set(filter(Operator.is_inline, self.binary()))
        self._unary = set(filter(lambda x: x.operands == 1, self.all))
        self._leaf = list(filter(lambda x: x.operands == 0, self.all))[0]

    @staticmethod
    def from_dict(ops: dict):
        ops_set = {Operator(k, **v) for k, v in ops.items()}
        return Operators(ops_set)

    def binary(self):
        return self._binary

    def inline_binary(self):
        return self._inline_binary

    def unary(self):
        return self._unary

    def leaf(self):
        return self._leaf


class ExprSampler:
    def __init__(self, ops: Operators):
        self._ops = ops

    def single(self, depth, deep_acc=1, forbidden_ops=None):
        if randbool(1-deeper_chance) or depth == 1:
            return deep_acc, atom()

        allowed_ops = self._ops.all if not forbidden_ops else \
            self._ops.all - forbidden_ops

        (d1, fst), (d2, snd) = self.single(depth-1, deep_acc+1), self.single(depth-1, deep_acc+1)

        return max(d1, d2), random.choice(tuple(allowed_ops)).latex.format(
            fst, snd)

    def sample(self, k, d):
        for _ in range(k):
            if randbool(0.7):
                c1, c2 = '1,0,0', '0,0,1'
                (_, s1), (_, s2) = self.single(
                    d, forbidden_ops=self._ops.inline_binary()), self.single(d)
                bop = random.choice(tuple(self._ops.binary()))
                yield bop.latex.format(
                    color_expr(s1, c1), color_expr(s2, c2)
                ), bop.latex.format(s1, s2), bop.opcode
            else:
                c = '1,0,0'
                deep_acc, s = self.single(d)
                if deep_acc != 1:
                    uop = random.choice(tuple(self._ops.unary()))
                else:
                    uop = self._ops.leaf()
                yield uop.latex.format(color_expr(s, c)), uop.latex.format(s, c), uop.opcode



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ops-cfg', help='operators JSON config',
                        required=True, type=str)
    parser.add_argument('--samples', help='number of samples', required=True,
                        type=int)
    parser.add_argument('--max-depth', help='max allowed depth of LaTeX tree',
                        required=True, type=int)
    parser.add_argument('--op-path', help='optional operator labels save path',
                        required=False, type=str)
    parser.add_argument('--expr-path', help='optional expression save path',
                        required=False, type=str)
    parser.add_argument('--color-path', help='optional colors save path',
                        required=False, type=str)
    parser.add_argument('--deeper-chance', help='Chance to go deeper with generating.',
                        required=False, type=float, default=0.7)
    cmd_args = parser.parse_args()
    print(cmd_args)
    with open(cmd_args.ops_cfg, 'r') as ops_cfg_file:
        ops_config = json.load(ops_cfg_file)

    operators = Operators.from_dict(ops_config)
    sampler = ExprSampler(operators)
    deeper_chance = cmd_args.deeper_chance
    opcode_labels = []

    exprs, exprs_nc, opcodes = [], [], []

    for clr_expr, expr, opcode in sampler.sample(cmd_args.samples,
                                                 cmd_args.max_depth):
        exprs.append(clr_expr)
        exprs_nc.append(expr)
        opcodes.append(opcode)

    def try_export(path, items):
        if path:
            with open(path, 'w+') as outfile:
                outfile.write('\n'.join(items)+'\n')

    try_export(cmd_args.op_path, opcodes)
    try_export(cmd_args.expr_path, exprs_nc)
    try_export(cmd_args.color_path, exprs)
