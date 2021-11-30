import matplotlib.pyplot as plt
import os


def save(name='', fmt='png'):
    """Save graphs as file in folder png"""
    pwd = os.getcwd()
    path = './{}'.format(fmt)
    if not os.path.exists(path):
        os.mkdir(path)
    os.chdir(path)
    plt.savefig('{}.{}'.format(name, fmt))
    os.chdir(pwd)


def graph_plt(g_data, g_name, legend):
    """Create and show graph from data"""
    g_dict = {}
    for i in g_data:
        g_dict.update({str(i[0]): i[1]})

    g_list = g_dict.items()
    g_list = sorted(g_list)
    x, y = zip(*g_list)

    plt.plot(x, y)
    plt.xlabel('price')
    plt.ylabel('day')
    plt.title(legend)
    save(name=g_name)
    plt.show()
