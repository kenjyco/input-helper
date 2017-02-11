import re
import textwrap
from datetime import timedelta
from os.path import isfile


RX_HMS = re.compile(r'^((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?$')
RX_COLON = re.compile(r'^((?P<hours>\d+):)?(?P<minutes>\d+):(?P<seconds>\d+)$')


def string_to_set(s):
    """Return a set of strings from s where items are separated by any of , ; |"""
    return set(re.split(r'\s*[,;\|]\s*', s)) - set([''])


def get_all_urls(*urls_or_filenames):
    """Return a list of all urls from objects that are urls or files of urls"""
    urls = []
    for thing in urls_or_filenames:
        if isfile(thing):
            with open(thing, 'r') as fp:
                text = fp.read()
            urls.extend([
                url
                for url in re.split('\r?\n', text)
                if url and '://' in url
            ])
        elif '://' in thing:
            urls.append(thing)
    return urls


def from_string(val):
    """Return simple bool, int, and float values contained in a string

    Useful for converting items in config files parsed by
    `configparser.RawConfigParser()` or values pulled from Redis
    """
    if val.lower() == 'true':
        val = True
    elif val.lower() == 'false':
        val = False
    else:
        try:
            val = float(val)
            if val.is_integer():
                val = int(val)
        except ValueError:
            try:
                val = int(val)
            except ValueError:
                pass
    return val


def decode(obj, encoding='utf-8'):
    """Decode the bytes of an object to an encoding"""
    try:
        return obj.decode(encoding)
    except (AttributeError, UnicodeDecodeError):
        return obj


def timestamp_to_seconds(timestamp):
    """Return number of seconds (int) for given timestamp

    - timestamp: a string in one the following formats: '3h4m5s', '2h15s', '47m',
      '300s', '3:04:05', '2:00:15', '47:00', '300'
    """
    try:
        seconds = int(timestamp)
    except ValueError:
        try:
            match_dict = RX_HMS.match(timestamp).groupdict()
        except AttributeError:
            try:
                match_dict = RX_COLON.match(timestamp).groupdict()
            except AttributeError:
                return
        td_kwargs = {
            k: int(v)
            for k, v in match_dict.items()
            if v is not None
        }
        seconds = timedelta(**td_kwargs).seconds
    return seconds


def user_input(prompt_string='input', ch='> '):
    """Prompt user for input

    - prompt_string: string to display when asking for input
    - ch: string appended to the main prompt_string
    """
    try:
        return input(prompt_string + ch)
    except (EOFError, KeyboardInterrupt):
        print()
        return ''


def make_selections(items, prompt='', wrap=True, item_format=''):
    """Generate a menu from items, then return a subset of the items provided

    - items: list of strings or list of dicts
    - prompt: string to display when asking for input
    - wrap: True/False for whether or not to wrap long lines
    - item_format: format string for each item (when items are dicts)

    Note: selection order is preserved in the returned items
    """
    if not items:
        return items

    selected = []

    if not prompt:
        prompt = 'Make selections (separate by space): '

    make_string = lambda x: x
    if item_format:
        make_string = lambda x: item_format.format(**x)

    # Generate the menu and display the items user will select from
    for i, item in enumerate(items):
        if i % 5 == 0 and i > 0:
            print('-' * 70)
        try:
            line = '{:4}) {}'.format(i, make_string(item))
        except UnicodeEncodeError:
            item = {
                k: v.encode('ascii', 'replace')
                for k, v in item.items()
            }
            line = '{:4}) {}'.format(i, make_string(item))
        if wrap:
            print(textwrap.fill(line, subsequent_indent=' '*6))
        else:
            print(line)

    print()
    indices = user_input(prompt)
    if not indices:
        return []

    for index in indices.split():
        try:
            selected.append(items[int(index)])
        except (IndexError, ValueError):
            pass

    return selected


def parse_command(input_line):
    """Split a string into cmd & args based on delimiter defined in the string

    Provides a flexible way to receive a command name and its arguments in a
    single string.

    - first word of the string is the command name
    - remaining parts of the string are the arguments
        - if the delimiter used to separate arguments is not a space, the last
          character(s) of the string should be the delimiter (extra whitespace
          is ok)
        - extra whitespace around individual arguments is trimmed off

    Examples:

    >>> from pprint import pprint

    >>> pprint(parse_command('sum 4 5 18'))
    {'args': ['4', '5', '18'], 'cmd': 'sum'}

    >>> pprint(parse_command('thinger first thing -- second thing -- third thing --'))
    {'args': ['first thing', 'second thing', 'third thing'], 'cmd': 'thinger'}

    >>> pprint(parse_command('   colon grr :: noise a thing makes ::    '))
    {'args': ['grr', 'noise a thing makes'], 'cmd': 'colon'}

    >>> pprint(parse_command('pprint'))
    {'cmd': 'pprint'}
    """
    rx_delim = re.compile(
        r'''^\s*(?P<cmd>\S+)\s+
        (?P<args>.*?)
        \s*(?P<delim>[^A-Za-z0-9\s]+)\s*$
        ''', re.VERBOSE
    )
    rx_space = re.compile(
        r'''^\s*(?P<cmd>\S+)\s+
        (?P<args>.*?)$
        ''', re.VERBOSE
    )
    rx_cmd = re.compile(r'^\s*(?P<cmd>\S+)\s*$')

    try:
        d = rx_delim.match(input_line).groupdict()
    except AttributeError:
        try:
            d = rx_space.match(input_line).groupdict()
        except AttributeError:
            try:
                d = rx_cmd.match(input_line).groupdict()
            except AttributeError:
                return

    if 'args' in d:
        if 'delim' in d:
            d['args'] = [arg.strip() for arg in d['args'].split(d['delim'])]
            d.pop('delim')
        else:
            d['args'] = d['args'].split()

    return d
