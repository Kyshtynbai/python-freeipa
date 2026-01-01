# -*- coding: utf-8 -*-
import subprocess
import argparse

# Оснастка argparser
argparser = argparse.ArgumentParser()
argparser.add_argument("filename", help="Файл со списком логинов по одному на строку")
args = argparser.parse_args()

# Получение аргументов командной строки
file = args.filename

raw_users = []
users = {}
with open (file, 'r') as f:
    for line in f:
        line = line.rstrip()
        res = subprocess.Popen(f"ipa user-show {line}",
            encoding='utf-8',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        output = res.stdout.read()
        errors = res.stderr.read()
        if line not in users: # Вивификация ключа
            users[line] = ''
        if errors:
            users[line] = ('error',errors.rstrip())
        else:
            users[line] = output.split('\n')

print(users)
