import os
import os.path
import subprocess
import sys

import yaml


def load_config(config_path: str) -> dict:
    with open(config_path, encoding='utf-8') as yml_input:
        try:
            CONFIG = yaml.safe_load(yml_input)
        except Exception as e:
            print(f'There appears to be a syntax problem with your {config_path}', file=sys.stderr)
            raise e

    if 'LICHESS_BOT_TOKEN' in os.environ:
        CONFIG['token'] = os.environ['LICHESS_BOT_TOKEN']

    # [section, type, error message]
    sections = [
        ['API_key', str, 'Section `API_key` must be a string wrapped in quotes.'],
        ['GPT_Settings', dict, 'Section `GPT_Settings` must be a dictionary with indented keys followed by colons.'],

        ['token', str, 'Section `token` must be a string wrapped in quotes.'],
        ['challenge', dict, 'Section `challenge` must be a dictionary with indented keys followed by colons.'],
        ['matchmaking', dict, 'Section `matchmaking` must be a dictionary with indented keys followed by colons.'],
        ['messages', dict, 'Section `messages` must be a dictionary with indented keys followed by colons.']]

    for section in sections:
        if section[0] not in CONFIG:
            raise RuntimeError(f'Your {config_path} does not have required section `{section[0]}`.')

        if not isinstance(CONFIG[section[0]], section[1]):
            raise TypeError(section[2])

    if 'whitelist' in CONFIG:
        if not isinstance(CONFIG['whitelist'], list):
            raise TypeError('If uncommented, "whitelist" must be a list of usernames.')

        CONFIG['whitelist'] = [username.lower() for username in CONFIG['whitelist']]

    if 'blacklist' in CONFIG:
        if not isinstance(CONFIG['blacklist'], list):
            raise TypeError('If uncommented, "blacklist" must be a list of usernames.')

        CONFIG['blacklist'] = [username.lower() for username in CONFIG['blacklist']]

    try:
        output = subprocess.check_output(['git', 'show', '-s', '--date=format:%Y%m%d',
                                         '--format=%cd', 'HEAD'], stderr=subprocess.DEVNULL)
        commit_date = output.decode('utf-8').strip()
        output = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL)
        commit_SHA = output.decode('utf-8').strip()[:7]
        CONFIG['version'] = f'{commit_date}-{commit_SHA}'
    except (FileNotFoundError, subprocess.CalledProcessError):
        CONFIG['version'] = 'nogit'

    return CONFIG
