import inspect
import re
import sys
import datetime
import urllib


class Matcher(object):
    """Create a Python dictionary from a line/chunk of text (using named regex)

    Sub-class Matcher, define a compiled regular expression (with NAMED
    GROUPS) for `rx` or `rx_iter`, and create methods using the group names in
    the regular expression.

    - only ONE named group may be used with `rx_iter`
    - only `rx` OR `rx_iter` may be defined for a Matcher sub-class (not both)

    A `finalize` method can be defined to perform any extra processing on the
    'results' dict before returning. (Accept the results dict, update it, and
    return it).

    - Methods of the sub-class should accept a 'text' parameter and return a
      Python object
    """
    rx = None
    rx_iter = None

    def __call__(self, text):
        # Complain if rx and rx_iter are defined (only one allowed)
        if self.rx and self.rx_iter:
            message = 'Cannot specify both "rx" and "rx_iter" for {}'
            raise ValueError(message.format(self.__class__.__name__))

        try:
            match_dict = self.rx.match(text).groupdict()
        except AttributeError:
            match_dict = {}

        try:
            match_iter_list = [x.groupdict() for x in self.rx_iter.finditer(text)]
        except AttributeError:
            match_iter_list = []

        if match_dict:
            # Collect methods of sub-class as the `methods` dict
            methods = dict(filter(
                lambda x: x[0] in match_dict.keys(),
                inspect.getmembers(self)
            ))

        if match_iter_list:
            # Complain if rx_iter has more than one named group
            named_groups = match_iter_list[0].keys()
            if len(named_groups) > 1:
                message = '"rx_iter" has more than 1 named group for {}: {}'
                raise ValueError(message.format(
                    self.__class__.__name__, repr(named_groups))
                )

            # Collect methods of sub-class as the `methods2` dict
            _keys = set([key for k in match_iter_list for key in k.keys()])
            methods2 = dict(filter(
                lambda x: x[0] in _keys,
                inspect.getmembers(self)
            ))

        results = {}

        for group, text in match_dict.items():
            try:
                results[group] = methods[group](text)
            except KeyError:
                results[group] = text

        for d in match_iter_list:
            for group, text in d.items():
                key = '{}_list'.format(group)
                try:
                    value = methods2[group](text)
                except KeyError:
                    value = text
                try:
                    results[key].append(value)
                except KeyError:
                    results[key] = [value]

        results = self.finalize(results)
        return results

    def finalize(self, results):
        return results


class MultiMatcher(object):
    """Multiple Matcher sub-classes in a single object"""
    def __init__(self, matchers=None, debug=False):
        """Initialize with a list of matcher instances

        If debug is True, include a '_key_matcher_dict' key (in the return dict)
        containing fields that were matched, and the matcher instance that
        updated the field's data.
        """
        if matchers:
            self.matchers = matchers
        else:
            self.matchers = []

        self.debug = debug

    def __call__(self, text):
        """
        """
        if self.debug:
            results = {'_key_matcher_dict': {}}
        else:
            results = {}

        for matcher in self.matchers:
            res = matcher(text)
            results.update(res)

            if self.debug:
                # Add the Matcher sub-class name for returned fields
                results['_key_matcher_dict'].update(
                    dict([(k, matcher.__class__.__name__) for k in res.keys()]))
        return results

    def add_matcher_instances(self, *matchers):
        self.matchers.extend(matchers)


class IdentityMatcher(Matcher):
    """Match the entire line"""
    rx = re.compile(r'^(?P<text>.*)$')


class LeadingSpacesMatcher(Matcher):
    """Match number of leading spaces (replacing any tabs with 4 spaces)"""
    rx = re.compile(r'^(?P<leading_spaces>\s+)')

    def leading_spaces(self, text):
        # Replace any tab characters with 4 spaces
        text = text.replace('\t', ' '*4)
        return len(text)


class DoubleQuoteMatcher(Matcher):
    """Match text between double quotes"""
    rx_iter = re.compile(r'\"(?P<doublequoted>[^"]+)\"')


class SingleQuoteMatcher(Matcher):
    """Match text between single quotes, but not single quotes inside words"""
    rx_iter = re.compile(r"(^|\s|\b|[^\w])\'(?P<singlequoted>[^']+)\'[^\w]")


class BacktickMatcher(Matcher):
    """Match text between backticks"""
    rx_iter = re.compile(r'\`(?P<backtick>[^`]+)\`')


class MentionMatcher(Matcher):
    """Match all @mentions, preceeded by a space or "start of line"

    Ignore any '@' that are in the middle of a string (like in an email address).
    """
    rx_iter = re.compile(r'(^|\s)@(?P<mention>\S+)')


class TagMatcher(Matcher):
    """Match all #tags, preceeded by a space or "start of line"

    Ignore any tags that are in the middle of a string (like in a URL).
    """
    rx_iter = re.compile(r'(^|\s)#(?P<tag>\S+)')


class CommentMatcher(Matcher):
    """Match comments (after #) and non-comment text"""
    rx = re.compile(r'^(?P<non_comment>.*?)#\s+(?P<line_comment>.*)$')

    def non_comment(self, text):
        return text.strip()


class CapitalizedPhraseMatcher(Matcher):
    """Match a capitalized phrase (but not smart enough to capture "of/in/a"..

    Enhanced version of http://stackoverflow.com/a/4113070
    """
    rx_iter = re.compile(r'(^|\s|\"|\()(?P<capitalized_phrase>[A-Z][\w\-\.,]*(\s+[A-Z][\w\-\.,]*)*)')


class AllCapsPhraseMatcher(Matcher):
    """Match phrases/words written in ALL CAPS"""
    rx_iter = re.compile(r'(^|\s|\"|\()(?P<allcaps_phrase>[A-Z][A-Z\-\.,]+(\s+[A-Z][A-Z\-\.,]+)*)')


class CurlyMatcher(Matcher):
    """Match text between curly braces

    No attempt to perform nested matching.
    """
    rx_iter = re.compile(r'\{(?P<curly_group>[^\}]+)\}')


class ParenMatcher(Matcher):
    """Match text between parentheses

    Ignore any parentheses groups where the opening paren is not preceeded by a
    space or isn't the start of a line

    Also, no attempt to perform nested matching.
    """
    rx_iter = re.compile(r'(^|\s)\((?P<paren_group>[^\)]+)\)')


class DollarCommandMatcher(Matcher):
    """Match text in the parentheses of $()"""
    rx_iter = re.compile(r'(^|\s)\$\((?P<command_group>[^\)]+)\)')


class _UrlDetailsMatcher(Matcher):
    """Match a URL and split into details

    Primarily intended to be used by the `UrlMatcher`.
    """
    rx = re.compile(r"""
        (?P<full_url>
            (?P<protocol>\w+)://(www\.)?
            (?P<domain>[^/\s]+)
            (?P<path>([/]\S+)?))
        """, re.VERBOSE)

    def path(self, text):
        if not text:
            return {}

        try:
            uri, querystring = text.split('?')
        except ValueError:
            uri = text
            querystring = ''

        if not querystring:
            return {'full_path': text, 'uri': uri}

        parameters = {}
        for param in querystring.split('&'):
            try:
                key, val = param.split('=')
            except ValueError:
                key = param
                val = None
            parameters[key] = val

        return {
            'full_path': text,
            'uri': uri,
            'querystring': querystring,
            'parameters': parameters}

    def finalize(self, results):
        if not results['path']:
            results.pop('path')

        # The 'filename_prefix' is safe to use as part of a filename
        results['filename_prefix'] = urllib.parse.quote_plus(
            results['full_url'].split('://')[1]
        ).replace('%2F', '--')

        return results


class UrlDetailsMatcher(Matcher):
    """Match all URLs on a line and return details about the parts of each"""
    rx_iter = re.compile(r'(?P<url_details>\w+://\S+)')
    udm = _UrlDetailsMatcher()

    def url_details(self, text):
        return self.udm(text.strip(')').strip(']'))


class UrlMatcher(Matcher):
    """Match all URLs on a line"""
    rx_iter = re.compile(r'(?P<url>\w+://\S+)')


class NonUrlTextMatcher(Matcher):
    """For lines with URL(s), return the text that is not part of the URL(s)

    Kinda hacky...
    """
    rx = re.compile(r'^(?P<non_url_text>.*\w+://\S+.*)$')
    rx_url = re.compile(r'\w+://\S+')

    def non_url_text(self, text):
        """
        Replace any URLs with an empty string, then split/join remaining text
        to ensure there are not multiple consecutive spaces.
        """
        text = self.rx_url.sub('', text)
        return ' '.join(text.split())


class ScrotFileMatcher(Matcher):
    """Match `scrot` filenames that were created with the following command

        scrot -s '%Y_%m%d--%H%M_%S--'$(hostname)'--$wx$h.png'
    """
    rx = re.compile(r"""
        ^(?P<filename>
            (?P<datestamp>\d{4}_\d{4}--\d{4}_\d{2})--
            (?P<hostname>.*)--
            (?P<dimensions>\d+x\d+).png)
        """, re.VERBOSE)

    def datestamp(self, text):
        return datetime.datetime.strptime(text, '%Y_%m%d--%H%M_%S')

    def dimensions(self, text):
        width, height = text.split('x')
        return {
            'text': text,
            'width': int(width),
            'height': int(height),
            'area': int(width) * int(height)}


class ScrotFileMatcher2(ScrotFileMatcher):
    """Match `scrot` filenames that have standard format

        2015-06-23-205812_1916x1048_scrot.png
    """
    rx = re.compile(r"""
        ^(?P<filename>
            (?P<datestamp>\d{4}-\d{2}-\d{2}-\d{6})_
            (?P<dimensions>\d+x\d+)_scrot.png)
        """, re.VERBOSE)

    def datestamp(self, text):
        return datetime.datetime.strptime(text, '%Y-%m-%d-%H%M%S')


class FehSaveFileMatcher(Matcher):
    """Match files saved with the 's' hotkey while viewing with `feh`"""
    rx = re.compile(r"""
        ^(?P<filename>
            (?P<feh_prefix>feh_\d{6}_\d{6}_)
            (?P<other_filename>.*))$
        """, re.VERBOSE)


class PsOutputMatcher(Matcher):
    """Match output of `ps -eo user,pid,ppid,tty,cmd:200`"""
    rx = re.compile(r"""
        ^(?P<user>[\S]+)[\s]+
        (?P<pid>[\d]+)[\s]+
        (?P<ppid>[\d]+)[\s]+
        (?P<tty>[\S]+)[\s]+
        (?P<cmd>.*$)""", re.VERBOSE)

    def pid(self, text):
        return int(text)

    def ppid(self, text):
        return int(text)


class ZshHistoryLineMatcher(Matcher):
    """Match lines from the zsh history file (using `setopt extendedhistory`)"""
    rx = re.compile(r"""
        ^:\s*
        (?P<timestamp>\d+):
        (?P<duration>\d+);
        (?P<cmd>.*$)
        """, re.VERBOSE)

    def timestamp(self, text):
        return datetime.datetime.fromtimestamp(int(text))

    def duration(self, text):
        return int(text)


class SpecialTextMultiMatcher(MultiMatcher):
    def __init__(self, debug=False):
        super().__init__(debug=debug)
        self.add_matcher_instances(
            DoubleQuoteMatcher(), SingleQuoteMatcher(), BacktickMatcher(),
            MentionMatcher(), TagMatcher(), CommentMatcher(),
            CapitalizedPhraseMatcher(), AllCapsPhraseMatcher(),
            ParenMatcher(), UrlMatcher(), NonUrlTextMatcher(),
            IdentityMatcher(), CurlyMatcher(),
        )


class FilenameMultiMatcher(MultiMatcher):
    def __init__(self, debug=False):
        super().__init__(debug=debug)
        self.add_matcher_instances(
            ScrotFileMatcher(), ScrotFileMatcher2(), FehSaveFileMatcher(),
        )


class MasterMatcher(MultiMatcher):
    """Use most sub-classes of Matcher defined in this module

    Ignore any sub-classes that have a name that starts with '_'
    """
    def __init__(self, debug=False):
        global MATCHER_INSTANCES
        super().__init__(debug=debug)
        self.add_matcher_instances(*MATCHER_INSTANCES)


MATCHER_INSTANCES = [
    c[1]()
    for c in inspect.getmembers(sys.modules[__name__], inspect.isclass)
    if issubclass(c[1], Matcher) and c[0] != 'Matcher' and not c[0].startswith('_')
]
