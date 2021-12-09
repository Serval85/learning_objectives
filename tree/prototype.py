import re


def dict_result(result, fam, num):
    if result.get(fam):
        new_val = result.get(fam)
        new_val.append(re.sub(r'[\D, ^+]', '', num))
        result.update({fam: new_val})
    else:
        result.update({fam: [re.sub(r'[\D, ^+]', '', num)]})
    return result


def search_num(need_num: str, dict_tel: dict):
    need_num = need_num.replace('+', '\+')
    reg_need_num = re.compile(need_num)
    result = {}
    for tels in dict_tel.items():
        n_val = re.sub(r'[\D, ^+]', '', tels[0])
        if reg_need_num.findall(n_val) and\
                reg_need_num.findall(n_val):
            result = dict_result(result, tels[1], tels[0])
    return result


def search_lname(fam: str, dict_tel: dict):
    reg_need_fam = re.compile(fam)
    result = {}
    for tels in dict_tel.items():
        if reg_need_fam.findall(tels[1]):
            result = dict_result(result, tels[1], tels[0])
    return result


def search_both(num: str, fam: str, dict_tel: dict):
    need_num = num.replace('+', '\+')
    reg_need_num = re.compile(need_num)
    reg_need_fam = re.compile(fam)
    result = {}
    for tels in dict_tel.items():
        n_val = re.sub(r'[\D, ^+]', '', tels[0])
        if reg_need_num.findall(n_val) and\
                reg_need_num.findall(n_val) and\
                reg_need_fam.findall(tels[1]):
            result = dict_result(result, tels[1], tels[0])
    return result


def main():
    while True:
        print()
        print('Input Last name, phone or both... or parts, but number first')
        query = input()
        if query == 'exit':
            break
        with open('tels.txt') as f:
            dict_tel = {line.split()[0]: line.split()[1] for line in f}

        dict_q = query.split(' ')
        if len(dict_q) == 2:
            num = dict_q[0].replace('+', '').replace('*', '')
            fam = dict_q[1].replace('*', '')
            search_result = search_both(num, fam, dict_tel)
        elif len(dict_q) == 1:
            buf = dict_q[0].replace('+', '').replace('*', '')
            reg_isnum = re.findall(r'\D', buf)
            if not reg_isnum:
                search_result = search_num(buf, dict_tel)
            else:
                search_result = search_lname(buf, dict_tel)
        if search_result:
            print(search_result)
        else:
            print('404 Not found? try again :D')


if __name__ == "__main__":
    main()
