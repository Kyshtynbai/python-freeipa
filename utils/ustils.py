import subprocess
import time
import datetime
from utils.colors import bcolors
from utils.crypto import generate_password
from typing import Tuple, Optional

def get_users_list(f: str) -> list:
    """ Возвращает список со строками пользаков из файла.
    Один юзер -- одна строка. Элемент списка [4] -- логин 
    """

    with open(f, 'r', encoding='utf-8') as fname:
        users = []
        for line in fname:
            line = line.rstrip()
            users.append(line.split(','))
    return users

def user_exists(login: str) -> Tuple[bool, Optional[str]]:
    """
    Проверяет существование пользователя во FreeIPA
    
    Returns:
        (exists: bool, error_message: str or none)
    """

    cmd = ['ipa', '-n', 'user-show', login, '--all']

    try:
        result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=False,
                timeout=15
                )
    except subprocess.TimeoutExpired:
        return False, "Команда ipa отвалилась по таймауту"
    except FileNotFoundError:
        return False, "Команда ipa не найдена"
    except Exception as e:
        return False, f"Неожиданная ошибка при запуске команды ipa: {e}"
    if result.returncode == 0: return True, None
    if result.returncode == 2: return False, None
    
    err_msg = result.stderr.strip() or "Неизвестная ошибка"
    return False, f"FreeIPA вернула неожиданную ошибку: {result.returncode}: {err_msg}"

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
        'ipa', '-n', 'user-add', args[4], '--first', 
        args[1], '--last', args[0], '--phone', args[2], 
        '--pager', args[5], '--email', args[3], '--orgunit', args[6], '--random'
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True)
    
    except Exception as e:
        print(f"Ошибка создания пользователя: {e}")
        return None, e, None
    if result.returncode == 0:
        user_info = ()
        set_expitation_date(args[4])
        user_info = user_details(result.stdout.rstrip())
        return (args[4], result.stderr.rstrip(), user_info)
    if result.returncode != 0:
        print("Ощибка!", result.stderr.strip())

def get_user(user: str) -> tuple[bool, str or None, str or None]:
    """
    Ищет пользователя в ldap FreeIPA.
    Возвращает: (Найден, Ошибка или None, Вывод ipa или None)
    """
    cmd = ['ipa', '-n', 'user-show', user, '--all']
    try:
        result = subprocess.run(cmd, 
                                capture_output=True, 
                                text=True, 
                                timeout=15)
    except Exception as e:
        return False, f"Unexpected error while calling ipa client: {e}", None 
    if result.returncode == 0:
        ipa_output = result.stdout.rstrip() or None
        return True, None, ipa_output
    if result.returncode == 2: 
        return False, None, None

def user_details(ipa_output):
    """
    Парсит вывод ipa user-show
    Возвращает кортеж: Фамилия, Имя, Телефон, Почта, Логин, Номер заявки, Отдел, Дата истечения пароля или None 
    """
    hash = {}
    for field in ipa_output.split("\n"):
        if field.startswith('-'): continue
        if field.startswith('Added'): continue
        key, value = field.split(":")
        key = key.strip()
        hash[key] = value.strip()
    return hash.get('First name'), hash.get('Last name'),hash.get('Telephone Number'), hash.get('Email address'), hash.get('User login'), hash.get('Pager Number'), hash.get('Org. Unit'), hash.get('User password expiration'), hash.get('Random password','***')
