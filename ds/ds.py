import random
import string
colors = ['Apricot', 'Aquamarine', 'Bittersweet','Black','Blue','BlueGreen', 'BlueViolet', 'BrickRed', 'Brown','BurntOrange', 'CadetBlue' ,'CarnationPink', 'Cerulean','CornflowerBlue', 'Cyan', 'Dandelion', 'DarkOrchid', 'Emerald','ForestGreen','Fuchsia', 'Goldenrod','Gray','Green','GreenYellow','JungleGreen','Lavender','LimeGreen','Magenta', 'Maroon', 'Melon', 'MidnightBlue', 'Mulberry','NavyBlue', 'OliveGreen', 'Orange' ,'OrangeRed', 'Orchid', 'Peach'	,'Periwinkle' ,'PineGreen','Plum', 'ProcessBlue', 'Purple', 'RawSienna', 'Red', 'RedOrange', 'RedViolet', 'Rhodamine','RoyalBlue','RoyalPurple','RubineRed','Salmon','SeaGreen','Sepia','SkyBlue','SpringGreen','Tan','TealBlue','Thistle','Turquoise','Violet','VioletRed','WildStrawberry','Yellow','YellowGreen','YellowOrange']

binary = [R'\frac{{ {0} }}{{ {1} }}', '{0}+{1}', '{0}-{1}', R'{0} \cdot {1}']
unary = [R'\sqrt{{ {0} }}', R'\int {0} ', R'\left({0}\right)', R'f\left({0}\right)', R'F\left({0}\right)', R'G\left({0}\right)']
op = binary+unary
letters='xyabcd'
symbols = string.digits+letters
def color_expr(expr):
    return '\color{{ {0} }}{{ {1} }}'.format(random.choice(colors), expr)

def color_expr(expr, c):
    return '\color{{ {0} }}{{ {1} }}'.format(c, expr)

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
        c1, c2 = 'brown','blue'
        l.append(random.choice(binary).format(color_expr(single(d), c1), color_expr(single(d), c2)))
    return l


if __name__ == "__main__":
    for expr in sample(20, 5):
        print('$$ '+expr + ' $$')