import keyword
import re
import string
import textwrap
from ast import literal_eval
from collections import defaultdict, Counter
from copy import deepcopy
from datetime import timedelta
from fnmatch import fnmatch
from functools import partial
from input_helper import matcher
from json import JSONDecoder, JSONDecodeError
from os.path import isfile
from sys import stdin
try:
    ModuleNotFoundError
except NameError:
    class ModuleNotFoundError(ImportError):
        pass
try:
    import xmljson
    from xml.etree.ElementTree import fromstring as xml_fromstring
except (ImportError, ModuleNotFoundError):
    xmljson = None
    xml_fromstring = None
try:
    from click import getchar
except (ImportError, ModuleNotFoundError):
    try:
        import tty
        import termios
    except (ImportError, ModuleNotFoundError):
        def getchar():
            message = (
                'This platform does not have termios/tty available.\n\n'
                'Please install "click" package if you want to get unbuffered input.'
            )
            raise Exception(message)
    else:
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


SECONDS_IN_HOUR = 60 * 60
SECONDS_IN_DAY = SECONDS_IN_HOUR * 24
SECONDS_IN_WEEK = SECONDS_IN_DAY * 7
RX_HMS = re.compile(r'^((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?$')
RX_COLON = re.compile(r'^((?P<hours>\d+):)?(?P<minutes>\d+):(?P<seconds>\d+)$')
RX_NOT_WHITESPACE = re.compile(r'[^\s]')
RX_ENCLOSING_B_SINGLE_QUOTE = re.compile(r"^b'(.*)'$")
RX_NEWLINE = re.compile(r'\r?\n')
RX_NEWLINE_LEADING_SPACE = re.compile(r'\r?\n\s*')
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


def _less_than(x, y):
    """Return True if x < y"""
    _x, _y = from_string(x), from_string(y)
    try:
        return _x < _y
    except TypeError:
        try:
            return x < y
        except TypeError:
            pass
        return False


def _less_than_or_equal(x, y):
    """Return True if x <= y"""
    _x, _y = from_string(x), from_string(y)
    try:
        return _x <= _y
    except TypeError:
        try:
            return x <= y
        except TypeError:
            pass
        return False


def _greater_than(x, y):
    """Return True if x > y"""
    _x, _y = from_string(x), from_string(y)
    try:
        return _x > _y
    except TypeError:
        try:
            return x > y
        except TypeError:
            pass
        return False


def _greater_than_or_equal(x, y):
    """Return True if x >= y"""
    _x, _y = from_string(x), from_string(y)
    try:
        return _x >= _y
    except TypeError:
        try:
            return x >= y
        except TypeError:
            pass
        return False


def _sloppy_equal(x, y):
    """Return True if y is x, y is in x, or x is in y"""
    result = False
    _x, _y = from_string(x), from_string(y)
    if _x is None:
        if _y is None:
            return True
        return False
    _type_x = type(_x)
    _type_y = type(_y)
    if _type_x == str and _type_y == str:
        _x = _x.lower()
        _y = _y.lower()
    elif _type_x == str and _type_y != str:
        _y = repr(_y).lower()
        _type_y = str
    try:
        if _y == _x or _y in _x or _x in _y:
            result = True
    except TypeError:
        _x, _y = repr(_x).lower(), repr(_y).lower()
        if _y == _x or _y in _x or _x in _y:
            result = True
    return result


def _sloppy_not_equal(x, y):
    """Return True if y is not x and y is not in x and x is not in y"""
    result = False
    _x, _y = from_string(x), from_string(y)
    if _x is None:
        if _y is None:
            return False
        return True
    _type_x = type(_x)
    _type_y = type(_y)
    if _type_x == str and _type_y == str:
        _x = _x.lower()
        _y = _y.lower()
    elif _type_x == str and _type_y != str:
        _y = repr(_y).lower()
        _type_y = str
    try:
        if _y != _x and _y not in _x and _x not in _y:
            result = True
    except TypeError:
        _x, _y = repr(_x).lower(), repr(_y).lower()
        if _y != _x and _y not in _x and _x not in _y:
            result = True
    return result


FIND_OPERATORS = {
    '<': _less_than,
    '<=': _less_than_or_equal,
    '>': _greater_than,
    '>=': _greater_than_or_equal,
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


def splitlines(s):
    """Return a list of strings from s where items are separated by newline

    There will be no empty strings
    """
    return [
        line
        for line in RX_NEWLINE.split(s)
        if line
    ]


def splitlines_and_strip(s):
    """Return a list of strings from s where items are separated by newline

    Each string returned will have no leading/trailing whitespace and there
    will be no empty strings
    """
    results = []
    for line in RX_NEWLINE_LEADING_SPACE.split(s):
        line = line.strip()
        if line:
            results.append(line)

    return results


def string_to_set(s):
    """Return a set of strings from s where items are separated by any of , ; |"""
    try:
        return set(re.split(r'\s*[,;\|]\s*', s)) - set([''])
    except TypeError:
        if type(s) == list:
            return set(s)
        raise


def string_to_list(s):
    """Return a list of strings from s where items are separated by any of , ; |"""
    try:
        return [text for text in re.split(r'\s*[,;\|]\s*', s) if text]
    except TypeError:
        if type(s) == list:
            return s
        raise


def string_to_converted_list(s, keep_num_as_string=False):
    """Return a list of derived items from s where items are separated by , ; |

    - keep_num_as_string: if True, do not attempt to convert number strings to
      int or float
    """
    _from_string = partial(from_string, keep_num_as_string=keep_num_as_string)
    result = []
    if type(s) == str:
        s = s.replace('\\n', '\n').replace('\\t', '\t')
        result = list(map(_from_string, string_to_list(s)))
    return result


def get_list_from_arg_strings(*args):
    """Return a list of strings

    - args: strings that may or may not be separated by one of , ; |
    """
    _args = []
    for arg in args:
        _type = type(arg)
        if _type == str:
            _args.extend(string_to_list(arg))
        elif hasattr(arg, '__iter__'):
            for _arg in arg:
                _args.extend(get_list_from_arg_strings(_arg))
        else:
            _args.extend(string_to_list(str(arg)))
    return _args


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


def _clean_obj_string_for_parsing(s):
    """Return a "cleaned" string to be used in get_obj_from_[xml|json] funcs

    Ensure that bytes are decoded into a string, trailing/leading whitespace is
    removed, and that there is no enclosing 'b' with single quotes (around json)
    """
    s = decode(s).strip()
    match = RX_ENCLOSING_B_SINGLE_QUOTE.match(s)
    if match:
        s = match.group(1)
    return s


def yield_objs_from_json(json_text, pos=0, decoder=JSONDecoder(), cleaned=False):
    """Yield converted JSON objects for stacked JSON objects in a string or file

    - cleaned: if True, don't clean json_text with _clean_obj_string_for_parsing

    See: https://stackoverflow.com/a/50384432
    """
    if not cleaned:
        json_text = _clean_obj_string_for_parsing(json_text)
    if isfile(json_text):
        with open(json_text, 'r') as fp:
            json_text = fp.read()
    while True:
        match = RX_NOT_WHITESPACE.search(json_text, pos)
        if not match:
            return
        pos = match.start()

        try:
            obj, pos = decoder.raw_decode(json_text, pos)
        except JSONDecodeError as e:
            try:
                obj = literal_eval(json_text)
            except:
                raise e
            else:
                yield obj
                break
        yield obj


def get_obj_from_json(json_text, cleaned=False):
    """Return converted JSON object for JSON object in a string or file

    - cleaned: if True, don't clean xml_text with _clean_obj_string_for_parsing

    If there are stacked JSON objects in the string/file, only the first
    is returned
    """
    res = yield_objs_from_json(json_text, cleaned=cleaned)
    obj = next(res)
    if obj:
        return obj


def get_obj_from_xml(xml_text, convention='BadgerFish', warn=True, cleaned=False, **kwargs):
    """Return an object from an XML string or file

    - convention: an allowed type of xml parsing to do (from xmljson package)
        - Abdera, BadgerFish, Cobra, GData, Parker, Yahoo
    - warn: if True, and xmljson is not found, print a message
    - cleaned: if True, don't clean xml_text with _clean_obj_string_for_parsing
    - other kwargs are passed to the xmljson.<convention> init method
        - dict_type=dict (to use a regular dict over default collections.OrderedDict
        - invalid_tags='drop' (to drop any invalid tags)

    See: https://github.com/sanand0/xmljson#conventions
    """
    if xmljson is None:
        if warn:
            print('Could not find xmljson. Try to install with: pip3 install xmljson')
        return
    if not cleaned:
        xml_text = _clean_obj_string_for_parsing(xml_text)
    if isfile(xml_text):
        with open(xml_text, 'r') as fp:
            xml_text = fp.read()
    assert convention in ('Abdera', 'BadgerFish', 'Cobra', 'GData', 'Parker', 'Yahoo')
    parser = getattr(xmljson, convention)(**kwargs)
    obj = xml_fromstring(xml_text)
    return parser.data(obj)


def string_to_obj(s, convention='BadgerFish', **kwargs):
    """Return a dict or list from a string representing JSON or XML

    - convention: passed to get_obj_from_xml if s is xml
    - kwargs: passed to get_obj_from_xml if s is xml

    Wrapper to get_obj_from_json or get_obj_from_xml funcs
    """
    s = _clean_obj_string_for_parsing(s)
    if s.startswith('<'):
        return get_obj_from_xml(s, cleaned=True, convention=convention, **kwargs)
    return get_obj_from_json(s, cleaned=True)


def string_to_version_tuple(s):
    """Return a tuple from a version string (major int, minor int, patch string)"""
    major, minor, *patch = s.split('.')
    major_minor_float = float('{}.{}'.format(major, minor))
    patch = '.'.join(patch) if patch else ''
    return (int(major), int(minor), patch)


def from_string(val, keep_num_as_string=False):
    """Return simple bool, None, int, and float values contained in a string

    - keep_num_as_string: if True, do not attempt to convert number strings to
      int or float

    Useful for converting items in config files parsed by
    `configparser.RawConfigParser()` or values pulled from Redis

    Number strings with a leading "0", (except for leading "0." that happens to
    be a valid float) will be kept as strings
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
    elif keep_num_as_string:
        pass
    else:
        try:
            val = float(val)
            if _val.startswith('0') and len(_val) > 1 and not _val.startswith('0.'):
                val = _val
            else:
                if val.is_integer():
                    if '.' not in _val:
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
    keys = get_list_from_arg_strings(keys)
    data = {
        key: deepcopy(value)
        for key, value in some_dict.items()
        if key not in keys
    }
    return data


def flatten_and_ignore_keys(some_dict, *keys):
    """Return a flattened dict with all keys except the specified ignore keys

    - some_dict: a dict object that may contain other dicts and lists
    - keys: a list of key names or shell-glob style key patterns
        - nested keynames are supported (i.e. 'person.address.zipcode')
        - can also be a list of keys contained in a single string, separated
          by one of , ; |
        - shell-glob patterns supported include '*' to match everything, '?' to
          match a single character, and '[..]' to match specific characters and
          character ranges (when 2 chars are separated by '-' in the range)
    """
    keys = get_list_from_arg_strings(keys)

    def _flatten(current_dict, parent_key='', result=None):
        if result is None:
            result = {}

        for k, v in current_dict.items():
            new_key = '{}.{}'.format(parent_key, k) if parent_key else k
            if not any(fnmatch(new_key, pattern) for pattern in keys):
                if isinstance(v, dict):
                    _flatten(v, new_key, result)
                else:
                    result[new_key] = deepcopy(v)
        return result

    return _flatten(some_dict)


def unflatten_keys(flat_dict):
    """Return a dict with un-nested key names and nested dicts where appropriate

    - flat_dict: a dict object containing no nested dicts, where nested keynames
      are supported (i.e. 'person.address.zipcode')
    """
    data = {}

    for compound_key, value in flat_dict.items():
        keys = compound_key.split('.')
        current_level = data

        for i, key in enumerate(keys):
            if i == len(keys) - 1:
                current_level[key] = value
            else:
                if key not in current_level:
                    current_level[key] = {}
                current_level = current_level[key]

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
    keys = get_list_from_arg_strings(keys)
    data = {}
    for key in keys:
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
    keys = get_list_from_arg_strings(keys)
    some_dicts.sort(
        key=lambda x: tuple([x.get(k) for k in keys]),
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


def unique_counted_items(items):
    """Return list of unique items, prefixed by count, sorted by count

    - items: list of hashable items (not dicts)
    """
    return [
        (count, item)
        for item, count in sorted(
            Counter(items).items(),
            key=lambda x: x[1],
            reverse=True
        )
        if item
    ]


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
    """Return a dict of timestamp strings for the given number of seconds"""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    hms_parts = []
    if h:
        h = int(h)
        hms_parts.append('{}h'.format(h))
    else:
        h = 0
    if m:
        m = int(m)
        hms_parts.append('{}m'.format(m))
    else:
        m = 0
    if s:
        s = round(s)
        hms_parts.append('{}s'.format(s))

    pretty_parts = []
    weeks, seconds = divmod(seconds, SECONDS_IN_WEEK)
    if weeks > 0:
        part = '{} '.format(int(weeks))
        part += 'week' if weeks == 1 else 'weeks'
        pretty_parts.append(part)
    days, seconds = divmod(seconds, SECONDS_IN_DAY)
    if days > 0:
        part = '{} '.format(int(days))
        part += 'day' if days == 1 else 'days'
        pretty_parts.append(part)
    hours, seconds = divmod(seconds, SECONDS_IN_HOUR)
    if hours > 0:
        part = '{} '.format(int(hours))
        part += 'hour' if hours == 1 else 'hours'
        pretty_parts.append(part)
    minutes, seconds = divmod(seconds, 60)
    if minutes > 0:
        part = '{} '.format(int(minutes))
        part += 'minute' if minutes == 1 else 'minutes'
        pretty_parts.append(part)
    if seconds > 0:
        seconds = round(seconds, 3)
        part = '{} '.format(seconds)
        part += 'second' if seconds == 1 else 'seconds'
        pretty_parts.append(part)

    return {
        'colon': '{:02}:{:02}:{:02}'.format(h, m, s),
        'hms': ''.join(hms_parts),
        'pretty': ', '.join(pretty_parts)
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


def start_ipython(warn=True, colors=True, vi=True, confirm_exit=False, **things):
    """Start an ipython session

    - warn: if True, and ipython is not found, print a message
    - colors: if True, use shell colors
    - vi: if True, use vi editing mode
    - confirm_exit: if True, prompt "Do you really want to exit ([y]/n)?" when
      exiting the shell
    - things: any objects that should be available in the ipython session
    """
    try:
        from IPython import embed
        from traitlets.config import Config
    except (ImportError, ModuleNotFoundError):
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
    if confirm_exit is False:
        c.InteractiveShellEmbed.confirm_exit = False
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
