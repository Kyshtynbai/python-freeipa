import argparse
from utils.ustils import get_users_list, check_user, create_user

# Оснастка argparser
argparser = argparse.ArgumentParser()
argparser.add_argument("filename", help="Входные данные в формате (без заголовков!): фамилия,имя отчество,телефон,емейл,логин,заявка,оргюнит")
argparser.add_argument("-v", "--verbose",
                    help="Больше вывода",
                    action="store_true")
argparser.add_argument("-c", "--check",
                    help="Не создавать, только проверить наличие",
                    action="store_true")
args = argparser.parse_args()

# Считывание списка юзеров из входного файла
users = get_users_list(args.filename)
users_report = {}
for user in users:
    users_report[user[4]] = {}
    if check_user(user[4], args.verbose):
        users_report[user[4]]['status'] = 'не существует'
        if not args.check:
           res = create_user(*user)
           if args.verbose: print(res[1])
           users_report[user[4]]['password'] = res[-1]
    else:
        users_report[user[4]]['status'] = 'существует'
print('last,first,phone,email,login,password,expiration,ticket')
for k in users_report:
    print(f"{k}", users_report[k]['status'], users_report[k].get('password','***'), sep=',')

#for i in range(25):
#    print(generate_password(25))
    
# TODO:
# Убрать вербосити, настроить user_details
# args -> kwargs
# input file structure checking
# поиск групп по rn
# --addattr=STR Add an attribute/value pair. Format is attr=value. Использовать для пейджера.
# отчёт (лог) с паролями
# группы (подумать) посмотреть в ролевой модели
