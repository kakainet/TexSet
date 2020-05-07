import random
import string
colors = ['Apricot', 'Aquamarine', 'Bittersweet','Black','Blue','BlueGreen', 'BlueViolet', 'BrickRed', 'Brown','BurntOrange', 'CadetBlue' ,'CarnationPink', 'Cerulean','CornflowerBlue', 'Cyan', 'Dandelion', 'DarkOrchid', 'Emerald','ForestGreen','Fuchsia', 'Goldenrod','Gray','Green','GreenYellow','JungleGreen','Lavender','LimeGreen','Magenta', 'Mahogany', 'Maroon', 'Melon', 'MidnightBlue', 'Mulberry','NavyBlue', 'OliveGreen', 'Orange' ,'OrangeRed', 'Orchid', 'Peach'	,'Periwinkle' ,'PineGreen','Plum', 'ProcessBlue', 'Purple', 'RawSienna', 'Red', 'RedOrange', 'RedViolet', 'Rhodamine','RoyalBlue','RoyalPurple','RubineRed','Salmon','SeaGreen','Sepia','SkyBlue','SpringGreen','Tan','TealBlue','Thistle','Turquoise','Violet','VioletRed','White','WildStrawberry','Yellow','YellowGreen','YellowOrange']

binary = [R'\frac{0}{1}', '{0}+{1}', '{0}-{1}', R'{0} \cdot {1}']
unary = [R'\sqrt{0}', R'\int{0}', R'\left({0}\right)']
op = binary+unary

def color_expr(expr):
    return fR'\color{random.choice(colors)}{expr}'

def single(depth):
    if depth == 1:
        return random.choice(string.digits)
    return random.choice(op).format(single(depth-1), single(depth-1))

def sample(k, d):
    return [f'{color_expr(single(d))}+{color_expr(single(d))}' for _ in range(k)]


if __name__ == "__main__":
    for expr in sample(30, 2)
        print(expr)