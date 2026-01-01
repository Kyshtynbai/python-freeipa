import subprocess
import time
import datetime
from utils.colors import bcolors
from utils.crypto import generate_password

def get_users_list(f: str) -> list:
    """ Возвращает список со строками пользаков из файла. Один юзер -- одна строка. Элемент списка [4] -- логин """

    with open(f, 'r', encoding='utf-8') as fname:
        users = []
        for line in fname:
            line = line.rstrip()
            users.append(line.split(','))
    return users

def check_user(login, verbosity=False):
    """ Проверяет и печатает инфу о пользователях, проверив наличие пользователя и возвращает True, если пользователь НЕ найден """

    not_present = 0

    command = [
        'ipa', '-n', 'user-show', login, '--all'
    ]

    try:
        process = subprocess.run(command, 
        capture_output=True, 
        text=True, check=True)
        output = process.stdout.strip()
        errors = process.stderr.strip()
        (pager, email, exp) = user_details(output)
        print(f"Пользователь {login:30} {bcolors.WARNING}найден{bcolors.ENDC:10} {login};{email};{pager};{exp}")
        return not_present
    except subprocess.CalledProcessError as e:
        not_present = 1
        print(f"Пользователь {login:30} {bcolors.OKBLUE}не найден {bcolors.ENDC:7}", end='')
        print(f"{e.stderr}", end='')
        return not_present

def set_password(user):
    """ Устанавливает юзеру пароль """
    print(f"Setting password to user {user}")
    pw = generate_password(25)
    command = [
            'ipa', '-n', 'user-mod', user,
            '--password', pw
            ]
    try:
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        return pw
    except subprocess.CalledProcessError as e:
        print("Ошибка ипы: ", e)

def set_expitation_date(user):
    """ Устанавливает дату истечения пароля """
    ctime = time.strftime('%Y%m%d%H%M%S',time.localtime())
    begin_time = datetime.datetime.strptime(ctime, '%Y%m%d%H%M%S')
    end_time = begin_time + datetime.timedelta(days=60)
    end_time = end_time.strftime('%Y%m%d%H%M%S') + 'Z'
    print(f"Setting password expiration date {end_time}")
    command = [
            'ipa', '-n', 'user-mod', user,
            '--password-expiration', end_time
            ]
    try:
        process = subprocess.run(command, capture_output=True, text=True, check=True)
    except CalledProcessError as e:
        print("Ошибка установки даты экспирации пароля: ", e)
    pass

def create_user(*args):
    """ Создаёт пользователя в ipa. Возвращает кортеж с UID, выводом и ошибками и паролем """
    # Команда запускается как список строк
    command = [
        'ipa', '-n', 'user-add', args[4],
        '--first', args[1],
        '--last', args[0],
        '--phone', args[2],
        '--pager', args[5],
        '--email', args[3],
        '--orgunit', args[6]
    ]

    try:
        # Запускаем процесс и ожидаем завершения
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        
        # Получаем стандартный вывод и ошибки
        output = process.stdout.strip()
        errors = process.stderr.strip()
        pw = set_password(args[4])
        set_expitation_date(args[4])
        return (args[4], output, errors, pw)
    
    except subprocess.CalledProcessError as e:
        print(f"Ошибка создания пользователя: {e}")


def user_details(ipa_output):

    hash = {}
    for field in ipa_output.split("\n"):
        key, value = field.split(":")
        key = key.strip()
        hash[key] = value.strip()
    return hash.get('Pager Number'), hash.get('Email address'), hash.get('User password expiration')

def get_report():
    pass
