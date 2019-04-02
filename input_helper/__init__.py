import re
import textwrap
import tty
import termios
import string
import keyword
from datetime import timedelta
from os.path import isfile
from sys import stdin
from copy import deepcopy
from collections import defaultdict
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
CH2NUM = dict(zip(string.digits + string.ascii_letters, range(10 + len(string.ascii_letters))))
NUM2CH = dict(zip(range(10 + len(string.ascii_letters)), string.digits + string.ascii_letters))
SIMPLE_CHARACTERS = string.ascii_letters + string.punctuation + ''.join([str(x) for x in range(10)])
CH2NAME = {c: c for c in SIMPLE_CHARACTERS}
CH2NAME.update({
    '\t': 'Tab', '\r': 'Enter', '\x1b': 'Esc', '\x7f': 'Delete', ' ': 'Space',
    '\x1bOP': 'F1', '\x1bOQ': 'F2', '\x1bOR': 'F3', '\x1bOS': 'F4', '\x1b[15~': 'F5',
    '\x1b[17~': 'F6', '\x1b[18~': 'F7', '\x1b[19~': 'F8', '\x1b[20~': 'F9',
    '\x1b[21~': 'F10', '\x1b[24~': 'F12',
    '\x01': 'Ctrl+a', '\x05': 'Ctrl+e', '\x06': 'Ctrl+f', '\x07': 'Ctrl+g',
    '\x0e': 'Ctrl+n', '\x0f': 'Ctrl+o', '\x10': 'Ctrl+p', '\x11': 'Ctrl+q',
    '\x12': 'Ctrl+r', '\x13': 'Ctrl+s', '\x14': 'Ctrl+t', '\x15': 'Ctrl+u',
    '\x16': 'Ctrl+v', '\x17': 'Ctrl+w', '\x18': 'Ctrl+x', '\x19': 'Ctrl+y', '\x1a': 'Ctrl+z',
    '\x1b[D': '(left arrow)', '\x1b[C': '(right arrow)', '\x1b[B': '(down arrow)',
    '\x1b[A': '(up arrow)',
})
NAME2CH = {v: k for k, v in CH2NAME.items()}
TRANS_PUNC_TO_UNDERSCORE = str.maketrans(string.punctuation, '_' * len(string.punctuation))


def _sloppy_equal(x, y):
    """Return True if y is x, or is y is in x"""
    result = False
    x = from_string(x)
    y = from_string(y)
    _type_x = type(x)
    _type_y = type(y)
    if _type_x == str and _type_y == str:
        x = x.lower()
        y = y.lower()
    elif _type_x == str and _type_y != str:
        y = repr(y).lower()
        _type_y = str
    if y == x or y in x:
        result = True
    return result


def _sloppy_not_equal(x, y):
    """Return True if y is not x and y is not in x"""
    result = False
    x = from_string(x)
    y = from_string(y)
    _type_x = type(x)
    _type_y = type(y)
    if _type_x == str and _type_y == str:
        x = x.lower()
        y = y.lower()
    elif _type_x == str and _type_y != str:
        y = repr(y).lower()
        _type_y = str
    if y != x and y not in x:
        result = True
    return result


FIND_OPERATORS = {
    '<': lambda x, y: from_string(x) < from_string(y),
    '<=': lambda x, y: from_string(x) <= from_string(y),
    '>': lambda x, y: from_string(x) > from_string(y),
    '>=': lambda x, y: from_string(x) >= from_string(y),
    '!': lambda x, y: from_string(x) != from_string(y),
    '!=': lambda x, y: from_string(x) != from_string(y),
    '==': lambda x, y: from_string(x) == from_string(y),
    '$': _sloppy_equal,
    '~': _sloppy_not_equal,
}
RX_FIND_OPERATORS = re.compile(
    '^(?P<operator>' +
    '|'.join([
        ''.join([
            '\\{}'.format(y)
            for y in list(x)
        ])
        for x in FIND_OPERATORS
    ]) +
    ')+(?P<value>.*)'
)


def string_to_set(s):
    """Return a set of strings from s where items are separated by any of , ; |"""
    return set(re.split(r'\s*[,;\|]\s*', s)) - set([''])


def string_to_list(s):
    """Return a list of strings from s where items are separated by any of , ; |"""
    return [text for text in re.split(r'\s*[,;\|]\s*', s) if text]


def string_to_converted_list(s):
    """Return a list of derived items from s where items are separated by , ; |"""
    result = []
    if type(s) == str:
        s = s.replace('\\n', '\n').replace('\\t', '\t')
        result = list(map(from_string, string_to_list(s)))
    return result


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
    """Return simple bool, None, int, and float values contained in a string

    Useful for converting items in config files parsed by
    `configparser.RawConfigParser()` or values pulled from Redis
    """
    _val = val
    if type(val) != str:
        pass
    elif val.lower() == 'true':
        val = True
    elif val.lower() == 'false':
        val = False
    elif val.lower() == 'none':
        val = None
    else:
        try:
            val = float(val)
            if _val.startswith('0') and len(_val) > 1:
                val = _val
            else:
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


def make_var_name(s):
    """Return a valid Python variable name from string"""
    result = s.translate(TRANS_PUNC_TO_UNDERSCORE)
    result = result.strip().replace(' ', '_')
    if re.match('^[^_A-z]', result):
        result = '_' + result
    if result in keyword.kwlist:
        result = '_' + result
    return result


def get_keys_in_string(s):
    """Return a list of keys in a given format string"""
    return cm(s).get('curly_group_list', [])


def get_value_at_key(some_dict, key, condition=None):
    """Return the value at a specified key (nested.key.name supported)

    - some_dict: a dict object
    - key: name of a key
        - nested keynames are supported (i.e. 'person.address.zipcode')
    - condition: a single-variable func returning a bool
        - if the value at the key is a list/tuple, the result will be a list
          where items meet the specified condition
        - if the value at the key is anything else, the result will be the value
          if the condition is met, or None
    """
    if not '.' in key:
        _data = some_dict.get(key)
        _data_type = type(_data)
        if _data_type in (list, tuple):
            if condition:
                _data = [x for x in filter(condition, _data)]
            _data_len = len(_data)
            if _data_len == 1:
                _data = _data[0]
            elif _data_len == 0:
                _data = None
        else:
            if condition:
                _data = _data if condition(_data) else None

    else:
        _key, *subkeys = key.split('.')
        _data = some_dict.get(_key, {})
        _data_type = type(_data)
        for subkey in subkeys:
            try:
                _data = _data.get(subkey, {})
            except AttributeError as e:
                if _data_type in (list, tuple):
                    if condition:
                        _data = [x.get(subkey) for x in filter(condition, _data)]
                    else:
                        _data = [x.get(subkey) for x in _data]
                    _data_len = len(_data)
                    if _data_len == 1:
                        _data = _data[0]
                    elif _data_len == 0:
                        _data = None
                else:
                    _data = None
            else:
                if condition:
                    if type(_data) in (list, tuple):
                        _data = [x for x in filter(condition, _data)]
                        _data_len = len(_data)
                        if _data_len == 1:
                            _data = _data[0]
                        elif _data_len == 0:
                            _data = None
                    else:
                        _data = _data if condition(_data) else None
        if _data == {}:
            _data = None

    return _data


def ignore_keys(some_dict, *keys):
    """Return a dict with all keys except the specified ignore keys

    - some_dict: a dict object that may contain other dicts and lists
    - keys: a list of key names (NO nested key)
        - can also be a list of keys contained in a single string, separated
          by one of , ; |
    """
    _keys = []
    for key in keys:
        _type = type(key)
        if _type in (list, tuple):
            for _key in key:
                _keys.extend(string_to_list(_key))
        elif _type == str:
            _keys.extend(string_to_list(key))

    data = {
        key: deepcopy(value)
        for key, value in some_dict.items()
        if key not in _keys
    }
    return data


def filter_keys(some_dict, *keys, **conditions):
    """Return a dict with only the specified keys and values returned

    - some_dict: a dict object that may contain other dicts and lists
    - keys: a list of key names
        - nested keynames are supported (i.e. 'person.address.zipcode')
        - can also be a list of keys contained in a single string, separated
          by one of , ; |
    - conditions: mapping of key names and single-variable funcs returning a bool
        - note: if using a nested key, name the condition using '__' between the
          key name parts instead of '.'
        - if the value at the key is a list/tuple, the result will be a list
          where items meet the specified condition
        - if the value at the key is anything else, the result will be the value
          if the condition is met, or None
    """
    _keys = []
    for key in keys:
        _type = type(key)
        if _type in (list, tuple):
            for _key in key:
                _keys.extend(string_to_list(_key))
        elif _type == str:
            _keys.extend(string_to_list(key))

    data = {}
    for key in _keys:
        key_dunder = key.replace('.', '__')
        condition = conditions.get(key_dunder)
        data[key_dunder] = get_value_at_key(some_dict, key, condition)
    return data


def rename_keys(some_dict, **mapping):
    """Return a dict with the key names mapped from some_dict

    - some_dict: a dict object
    - mapping: names of keys in some_dict and what the new name should be
    """
    new_dict = {}
    for k, v in some_dict.items():
        key = mapping.get(k, k)
        new_dict[key] = deepcopy(v)
    return new_dict


def cast_keys(some_dict, **casting):
    """Return a dict where the specified keys have values cast to another type

    - some_dict: a dict object
    - casting: names of keys in some_dict and the function to cast its value
    """
    new_dict = {}
    for k, v in some_dict.items():
        func = casting.get(k)
        if func:
            try:
                new_dict[k] = func(v)
            except:
                new_dict[k] = deepcopy(v)
        else:
            new_dict[k] = deepcopy(v)
    return new_dict


def sort_by_keys(some_dicts, *keys, reverse=False):
    """Sort the given list of dicts by the specified keys

    - some_dicts: a list of dict objects
    - keys: a list of key names (simple names, NO nesting)
    - reverse: if True, reverse/descending order
    """
    _keys = []
    for key in keys:
        _type = type(key)
        if _type in (list, tuple):
            for _key in key:
                _keys.extend(string_to_list(_key))
        elif _type == str:
            _keys.extend(string_to_list(key))

    some_dicts.sort(
        key=lambda x: tuple([x.get(k) for k in _keys]),
        reverse=reverse
    )


def find_items(some_dicts, terms):
    """Return a generator containing dicts where specified terms are satisfied

    - some_dicts: a list of dict objects
    - terms: string of 'key:value' pairs separated by any of , ; |
        - after the ':' any of the operators defined in FIND_OPERATORS may be
          used before the value (i.e. 'rate:>5')
        - no operator implies the '==' operator
    """
    terms = string_to_set(terms)
    term_dict = defaultdict(list)
    for term in terms:
        key, value = term.split(':', 1)
        op_match = RX_FIND_OPERATORS.match(value)
        if op_match:
            data = op_match.groupdict()
            operator = data['operator']
            if data['value'].startswith('='):
                operator += '='
                value = from_string(data['value'][1:])
            else:
                value = from_string(data['value'])
        else:
            operator = '=='
            value = from_string(value)
        term_dict[key].append((operator, value))

    for some_dict in some_dicts:
        matches = defaultdict(list)
        for key, op_vals in term_dict.items():
            for operator, value in op_vals:
                v = from_string(get_value_at_key(some_dict, key))
                matches[key].append(
                    FIND_OPERATORS[operator](v, value)
                )
        if all([any(v) for v in matches.values()]):
            yield(some_dict)


def chunk_list(some_list, n):
    """Return a generator with n-sized chunks of items in some_list"""
    for i in range(0, len(some_list), n):
        yield some_list[i:i + n]


def get_string_maker(item_format='', missing_key_default=''):
    """Return a func that will create a string from a dict/tuple of data passed to it

    - item_format: format string with placeholder data keys in curly braces
        - if item_format is an empty string, just return identity function
        - if passing a tuple to this function, the positional curly braces
          can be empty, contain integers, etc
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
                keys = get_keys_in_string(item_format)
                data.update({
                    k: missing_key_default
                    for k in keys
                    if k not in data
                })
                s = item_format.format(**data)
        except KeyError:
            keys = get_keys_in_string(item_format)
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
        except TypeError:
           s = item_format.format(*data)
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


def getchar():
    """Get a character of input (unbuffrered) from stdin

    See: http://code.activestate.com/recipes/134892/
    """
    fd = stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(stdin.fileno())
        ch = stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def user_input_unbuffered(prompt_string='input', ch='> ', raise_interrupt=False):
    """Prompt user for a single character of unbuffered input

    - prompt_string: string to display when asking for input
    - ch: string appended to the main prompt_string
    - raise_interrupt: if True, raise KeyboardInterrupt when ctrl+c is pressed
    """
    print(prompt_string + ch, end='\0', flush=True)
    ch = getchar()
    if ch not in ('\x04', '\x03', '\r'):
        print(ch)
        return ch
    elif ch == '\x03' and raise_interrupt:
        raise KeyboardInterrupt
    return ''


def get_selection_range_indices(start, stop):
    """Return the indices that occur between start and stop, including stop"""
    if type(start) == str:
        try:
            start = CH2NUM[start]
        except KeyError:
            try:
                start = int(start)
            except ValueError:
                return []
    if type(stop) == str:
        try:
            stop = CH2NUM[stop]
        except KeyError:
            try:
                stop = int(stop)
            except ValueError:
                return []

    if start < stop:
        return [x for x in range(start, stop)] + [stop]
    else:
        return [x for x in range(start, stop, -1)] + [stop]


def make_selections(items, prompt='', wrap=True, item_format='', unbuffered=False,
                    one=False, raise_interrupt=False, raise_exception_chars=[]):
    """Generate a menu from items, then return a subset of the items provided

    - items: list of strings, list of dicts, or list of tuples
    - prompt: string to display when asking for input
    - wrap: True/False for whether or not to wrap long lines
    - item_format: format string for each item (when items are dicts or tuples)
    - unbuffered: if True, list of 1 item will be returned on key press
        - menu only displays first 62 items (since only 1 character of input
          is allowed.. 0-9, a-z, A-Z)
    - one: if True, return first item selected (instead of a list)
    - raise_interrupt: if True and unbuffered is True, raise KeyboardInterrupt
      when ctrl+c is pressed
    - raise_exception_chars: list of characters that will raise a generic exception
      if typed while unbuffered is True

    Note: selection order is preserved in the returned items
    """
    if not items:
        return items
    if unbuffered:
        items = items[:62]

    selected = []

    if not prompt:
        prompt = 'Make selections (separate by space): '

    make_string = get_string_maker(item_format)
    if len(items) > 62:
        make_i = lambda i: i
    else:
        make_i = lambda i: i if i < 10 else '   {}'.format(NUM2CH[i])

    # Generate the menu and display the items user will select from
    for i, item in enumerate(items):
        if i % 5 == 0 and i > 0:
            print('-' * 70)
        line = '{:4}) {}'.format(
            make_i(i),
            make_string(item)
        )
        if wrap:
            print(textwrap.fill(line, subsequent_indent=' '*6))
        else:
            print(line)

    print()
    if unbuffered:
        index = user_input_unbuffered(prompt, raise_interrupt=raise_interrupt)
        if index in raise_exception_chars:
            raise Exception
        try:
            selected.append(items[int(index)])
        except (IndexError, ValueError):
            try:
                selected.append(items[CH2NUM[index]])
            except (IndexError, KeyError):
                pass
    else:
        indices = user_input(prompt)
        if not indices:
            return []

        if 'all' in indices:
            selected = items[:]
        else:
            for index in indices.split():
                try:
                    selected.append(items[int(index)])
                except (IndexError, ValueError):
                    try:
                        selected.append(items[CH2NUM[index]])
                    except (IndexError, KeyError):
                        if index.count('-') == 1:
                            for i in get_selection_range_indices(*index.split('-')):
                                try:
                                    selected.append(items[i])
                                except IndexError:
                                    pass
                        else:
                            pass

    if selected:
        if one:
            selected = selected[0]
    return selected


def start_ipython(warn=False, colors=True, vi=True, **things):
    """Start an ipython session

    - warn: if True, and ipython is not found, print a message
    - colors: if True, use shell colors
    - vi: if True, use vi editing mode
    - things: any objects that should be available in the ipython session
    """
    try:
        from IPython import embed
        from traitlets.config import Config
    except ImportError:
        if warn:
            print('Could not find ipython. Try to install with: pip3 install ipython')
        return
    if things:
        from pprint import pprint
        print('\n------------------------------------------------------------')
        print('\nThe following objects will be available in ipython:\n')
        pprint(things)
        print('\n------------------------------------------------------------\n')
        locals().update(things)
    c = Config()
    if colors is True:
        c.InteractiveShellEmbed.colors = "Linux"
    if vi is True:
        c.InteractiveShellEmbed.editing_mode = "vi"
    embed(config=c)


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
