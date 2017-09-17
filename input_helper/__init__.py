import re
import textwrap
from datetime import timedelta
from os.path import isfile
from input_helper import matcher


RX_HMS = re.compile(r'^((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?$')
RX_COLON = re.compile(r'^((?P<hours>\d+):)?(?P<minutes>\d+):(?P<seconds>\d+)$')
sm = matcher.SpecialTextMultiMatcher()
um = matcher.UrlMatcher()
cm = matcher.CurlyMatcher()
SPECIAL_TEXT_RETURN_FIELDS = [
    'allcaps_phrase_list', 'backtick_list', 'capitalized_phrase_list',
    'curly_group_list', 'doublequoted_list', 'mention_list', 'paren_group_list',
    'singlequoted_list', 'tag_list', 'url_list'
]


def string_to_set(s):
    """Return a set of strings from s where items are separated by any of , ; |"""
    return set(re.split(r'\s*[,;\|]\s*', s)) - set([''])


def string_to_list(s):
    """Return a list of strings from s where items are separated by any of , ; |"""
    return [text for text in re.split(r'\s*[,;\|]\s*', s) if text]


def get_all_urls(*urls_or_filenames):
    """Return a list of all urls from objects that are urls or files of urls"""
    urls = []
    for thing in urls_or_filenames:
        if isfile(thing):
            with open(thing, 'r') as fp:
                text = fp.read()

            for line in re.split('\r?\n', text):
                matched = um(line)
                if matched:
                    urls.extend(matched['url_list'])
        else:
            matched = um(thing)
            if matched:
                urls.extend(matched['url_list'])
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


def get_string_maker(item_format='', missing_key_default=''):
    """Return a func that will create a string from a dict of data passed to it

    - item_format: format string with placeholder data keys in curly braces
        - if item_format is an empty string, just return identity function
    - missing_key_default: default value to use when the returned 'make_string'
      func is passed a dict that doesn't contain a key in the 'item_format'
    """
    def make_string(data):
        try:
           s = item_format.format(**data)
        except UnicodeEncodeError:
            data = {
                k: v.encode('ascii', 'replace')
                for k, v in data.items()
            }
            try:
                s = item_format.format(**data)
            except KeyError:
                keys = cm(item_format).get('curly_group_list', [])
                data.update({
                    k: missing_key_default
                    for k in keys
                    if k not in data
                })
                s = item_format.format(**data)
        except KeyError:
            keys = cm(item_format).get('curly_group_list', [])
            data.update({
                k: missing_key_default
                for k in keys
                if k not in data
            })
            try:
                s = item_format.format(**data)
            except UnicodeEncodeError:
                data = {
                    k: v.encode('ascii', 'replace')
                    for k, v in data.items()
                }
                s = item_format.format(**data)
        return s

    if item_format:
        return make_string

    return lambda x: x


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


def seconds_to_timestamps(seconds):
    """Return a dict of timestamp strings for the given numnber of seconds"""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    hms_parts = []
    if h:
        hms_parts.append('{}h'.format(h))
    if m:
        hms_parts.append('{}m'.format(m))
    if s:
        hms_parts.append('{}s'.format(s))

    return {
        'colon': '{:02}:{:02}:{:02}'.format(h, m, s),
        'hms': ''.join(hms_parts)
    }


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


def user_input_fancy(prompt_string='input', ch='> '):
    """Wrapper to user_input that will return a dict of parsed information

    - prompt_string: string to display when asking for input
    - ch: string appended to the main prompt_string
    """
    return sm(user_input(prompt_string, ch))


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

    make_string = get_string_maker(item_format)

    # Generate the menu and display the items user will select from
    for i, item in enumerate(items):
        if i % 5 == 0 and i > 0:
            print('-' * 70)
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
