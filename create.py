import argparse
from utils.ustils import get_users_list, user_exists, create_user, get_user, user_details

# Оснастка argparser
argparser = argparse.ArgumentParser()
argparser.add_argument("filename", help="Входные данные в формате (без заголовков!): фамилия,имя отчество,телефон,емейл,логин,заявка,оргюнит")
argparser.add_argument("-v", "--verbose",
                    help="Больше вывода",
                    action="store_true")
argparser.add_argument("-t", "--test",
                    help="Тестовый запуск",
                    action="store_true")
argparser.add_argument("-c", "--check",
                    help="Не создавать, только проверить наличие",
                    action="store_true")
args = argparser.parse_args()

# Считывание списка юзеров из входного файла
users = get_users_list(args.filename)
users_report = {}
if not args.test:
    for user in users:
        users_report[user[4]] = {}
        if user_exists(user[4])[0] == True:
            users_report[user[4]]['status'] = 'уже существует'
        else:
            users_report[user[4]]['status'] = 'будет создан'
            if not args.check:
               res = create_user(*user)
               if args.verbose: print(res[2])
               users_report[user[4]]['password'] = res[-1][-1]
print("=" * 10)
print('last,first,phone,email,login,password,expiration,ticket')
# TODO Вот этот вывод окучить с помощью get_user и user_details:
for k in users_report:
    print(f"{k}", users_report[k]['status'], users_report[k].get('password','***'), sep=',')
if args.test:
    for u in users:
        (status, message, user_info) = get_user(u[4])
        if status:
            current_user = ()
            current_user = user_details(user_info)
            print(f"Имя: {current_user[0]}, Фамилия: {current_user[1]}, Телефон: {current_user[2]}, Почта: {current_user[3]}, Логин: {current_user[4]}, Тикеты: {current_user[5]}, Отдел: {current_user[6]}, Пароль истекает: {current_user[7]}")
        elif not status:
            print(f"User {u[4]} not found")
        else:
            print(f"Хуй знает, ошибка какая-то: {message}")
# TODO:
# Убрать вербосити, настроить user_details
# input file structure checking
# поиск групп по rn
# --addattr=STR Add an attribute/value pair. Format is attr=value. Использовать для пейджера.
# группы (подумать) посмотреть в ролевой модели
