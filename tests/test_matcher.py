import datetime
from input_helper.matcher import (
    LeadingSpacesMatcher, DoubleQuoteMatcher, SingleQuoteMatcher,
    BacktickMatcher, MentionMatcher, TagMatcher, CommentMatcher,
    CapitalizedPhraseMatcher, AllCapsPhraseMatcher, CurlyMatcher, ParenMatcher,
    DollarCommandMatcher, UrlDetailsMatcher, UrlMatcher, NonUrlTextMatcher,
    ScrotFileMatcher, ScrotFileMatcher2, FehSaveFileMatcher,
    PsOutputMatcher, ZshHistoryLineMatcher,
    SpecialTextMultiMatcher, MasterMatcher,
)


class TestLeadingSpacesMatcher(object):
    def test_line_with_spaces(self):
        line = '    dogs and cats'
        spacematcher = LeadingSpacesMatcher()
        result = spacematcher(line)
        assert result == {'leading_spaces': 4}

    def test_line_with_tabs(self):
        line = '\t\tdogs and cats'
        spacematcher = LeadingSpacesMatcher()
        result = spacematcher(line)
        assert result == {'leading_spaces': 8}

    def test_line_without_spaces(self):
        line = 'jumping up and down'
        spacematcher = LeadingSpacesMatcher()
        result = spacematcher(line)
        assert result == {}


class TestDoubleQuoteMatcher(object):
    def test_multiple(self):
        line = 'Something in "double quotes" and "something else"'
        dqmatcher = DoubleQuoteMatcher()
        result = dqmatcher(line)
        assert result == {'doublequoted_list': ['double quotes', 'something else']}


class TestSingleQuoteMatcher(object):
    def test_apostrophe_words(self):
        line = "Don't match apostrophe inside words (like don't)"
        m = SingleQuoteMatcher()
        result = m(line)
        assert result == {}

    def test_simple(self):
        line = "look up 'rethinkdb 2.0 tornado youtube' later"
        m = SingleQuoteMatcher()
        result = m(line)
        assert result == {'singlequoted_list': ['rethinkdb 2.0 tornado youtube']}

    def test_multiple(self):
        line = "'this' and 'that' are in single quotes"
        m = SingleQuoteMatcher()
        result = m(line)
        assert result == {'singlequoted_list': ['this', 'that']}


class TestBacktickMatcher(object):
    def test_multiple(self):
        line = 'Something in `backticks` and `something else`'
        bm = BacktickMatcher()
        result = bm(line)
        assert result == {'backtick_list': ['backticks', 'something else']}


class TestMentionMatcher(object):
    def test_multiple_with_email(self):
        line = '@jimmy should email @sue sue@blah.net'
        mentionmatcher = MentionMatcher()
        result = mentionmatcher(line)
        assert result == {'mention_list': ['jimmy', 'sue']}


class TestTagMatcher(object):
    def test_leading_tag_and_url(self):
        line = '#python http://stackoverflow.com/questions/855759/python-try-else/855764#855764 try/except/else/finally'
        tagmatcher = TagMatcher()
        result = tagmatcher(line)
        assert result == {'tag_list': ['python']}

    def test_tags_and_nontags(self):
        line = 'This is a #string that has #tags and non#tags'
        tagmatcher = TagMatcher()
        result = tagmatcher(line)
        assert result == {'tag_list': ['string', 'tags']}

    def test_no_tags(self):
        line = 'There are no tags in this line of text'
        tagmatcher = TagMatcher()
        result = tagmatcher(line)
        assert result == {}


class TestCommentMatcher(object):
    def test_comment(self):
        line = '% git log -p --since=2.day   # commits & changes for last 2 days'
        commentmatcher = CommentMatcher()
        result = commentmatcher(line)
        assert result == {
            'non_comment': '% git log -p --since=2.day',
            'line_comment': 'commits & changes for last 2 days'
        }

    def test_comment_and_tags(self):
        line = 'This is a #cooltag and # this is a comment'
        commentmatcher = CommentMatcher()
        result = commentmatcher(line)
        assert result == {
            'non_comment': 'This is a #cooltag and',
            'line_comment': 'this is a comment'
        }

    def test_double_comment(self):
        line = 'This is a line  # this is a comment  # some extra'
        commentmatcher = CommentMatcher()
        result = commentmatcher(line)
        assert result == {
            'non_comment': 'This is a line',
            'line_comment': 'this is a comment  # some extra'
        }


class TestCapitalizedPhraseMatcher(object):
    def test_phrase_in_parens(self):
        line = 'I was at the lake this weekend (Rice Lake Wisconsin)'
        cm = CapitalizedPhraseMatcher()
        result = cm(line)
        assert result == {'capitalized_phrase_list': ['I', 'Rice Lake Wisconsin']}

    def test_phrase_in_doublequotes(self):
        line = '"Double Quoted Phrase" ... lazy'
        cm = CapitalizedPhraseMatcher()
        result = cm(line)
        assert result == {'capitalized_phrase_list': ['Double Quoted Phrase']}

    def test_phrases_with_simple_punctuation(self):
        line = 'Mrs. Jones went to the park to meet Ms. Smith'
        cm = CapitalizedPhraseMatcher()
        result = cm(line)
        assert result == {'capitalized_phrase_list': ['Mrs. Jones', 'Ms. Smith']}


class TestAllCapsPhraseMatcher(object):
    def test_simple_phrase(self):
        line = 'Time to GET OUT!!'
        cm = AllCapsPhraseMatcher()
        result = cm(line)
        assert result == {'allcaps_phrase_list': ['GET OUT']}


class TestCurlyMatcher(object):
    def test_multiple(self):
        line = '{_ts} -> field1={field1}, field2={field2}'
        curlymatcher = CurlyMatcher()
        result = curlymatcher(line)
        assert result == {'curly_group_list': ['_ts', 'field1', 'field2']}


class TestParenMatcher(object):
    def test_leading_parentheses(self):
        line = '(dunno why you would do this) since parens usually come after some other text to clarify it'
        parenmatcher = ParenMatcher()
        result = parenmatcher(line)
        assert result == {'paren_group_list': ['dunno why you would do this']}

    def test_multiple_parentheses_groups(self):
        line = 'This is a #string (a collection of characters) that contains multiple sets of #parentheses (but they are not nested) and here is somefunc() and another_func(with, args)'
        parenmatcher = ParenMatcher()
        result = parenmatcher(line)
        assert result == {'paren_group_list': ['a collection of characters', 'but they are not nested']}

    def test_no_parens(self):
        line = 'There are no parentheses in this line of text'
        parenmatcher = ParenMatcher()
        result = parenmatcher(line)
        assert result == {}


class TestDollarCommandMatcher(object):
    def test_simple(self):
        line = 'During my input session, I may decide to run a command like $(google "python regular expression")... if it existed'
        dcm = DollarCommandMatcher()
        result = dcm(line)
        assert result == {'command_group_list': ['google "python regular expression"']}


class TestUrlDetailsMatcher(object):
    def test_url_with_no_path(self):
        line = 'http://simple.net/'
        um = UrlDetailsMatcher()
        result = um(line)
        assert result == {
            'url_details_list': [
                {
                    'domain': 'simple.net',
                    'protocol': 'http',
                    'full_url': 'http://simple.net',
                    'filename_prefix': 'simple.net'
                }
            ]}

    def test_multiple_urls(self):
        line = 'https://docs.python.org/2/howto/regex.html https://docs.python.org/2/library/re.html'
        um = UrlDetailsMatcher()
        result = um(line)
        assert result == {
            'url_details_list': [
                {
                    'domain': 'docs.python.org',
                    'path': {
                        'full_path': '/2/howto/regex.html',
                        'uri': '/2/howto/regex.html'
                    },
                    'protocol': 'https',
                    'full_url': 'https://docs.python.org/2/howto/regex.html',
                    'filename_prefix': 'docs.python.org--2--howto--regex.html'
                },
                {
                    'domain': 'docs.python.org',
                    'path': {
                        'full_path': '/2/library/re.html',
                        'uri': '/2/library/re.html'
                    },
                    'protocol': 'https',
                    'full_url': 'https://docs.python.org/2/library/re.html',
                    'filename_prefix': 'docs.python.org--2--library--re.html'
                }
            ]}

    def test_url_in_parens(self):
        line = '(https://docs.python.org/2.7/tutorial/index.html)'
        um = UrlDetailsMatcher()
        result = um(line)
        assert result == {
            'url_details_list': [
                {
                    'domain': 'docs.python.org',
                    'full_url': 'https://docs.python.org/2.7/tutorial/index.html',
                    'filename_prefix': 'docs.python.org--2.7--tutorial--index.html',
                    'path': {
                        'full_path': '/2.7/tutorial/index.html',
                        'uri': '/2.7/tutorial/index.html'
                    },
                    'protocol': 'https'}
            ]}


class TestNonUrlTextMatcher(object):
    def test_youtubelink(self):
        line = 'https://www.youtube.com/watch?v=U8NFS8WXfCI a 14 minute #jazz track'
        nutm = NonUrlTextMatcher()
        result = nutm(line)
        assert result == {'non_url_text': 'a 14 minute #jazz track'}

    def test_line_with_no_url(self):
        line = 'This is just some text without a URL'
        nutm = NonUrlTextMatcher()
        result = nutm(line)
        assert result == {}


class TestScrotFileMatcher(object):
    def test_filename(self):
        filename = '2015_0526--2014_00--cb120--496x212.png'
        scrotmatcher = ScrotFileMatcher()
        result = scrotmatcher(filename)
        assert result == {
            'datestamp': datetime.datetime(2015, 5, 26, 20, 14),
            'hostname': 'cb120',
            'dimensions': {
                'text': '496x212',
                'height': 212,
                'area': 105152,
                'width': 496
            },
            'filename': '2015_0526--2014_00--cb120--496x212.png'
        }


class TestScrotFileMatcher2(object):
    def test_filename(self):
        filename = '2015-06-23-205812_1916x1048_scrot.png'
        scrotmatcher = ScrotFileMatcher2()
        result = scrotmatcher(filename)
        assert result == {
            'datestamp': datetime.datetime(2015, 6, 23, 20, 58, 12),
            'dimensions': {
                'text': '1916x1048',
                'height': 1048,
                'area': 2007968,
                'width': 1916
            },
            'filename': '2015-06-23-205812_1916x1048_scrot.png'
        }


class TestFehSaveFileMatcher(object):
    def test_filename(self):
        filename = 'feh_016660_000004_2015-06-12-233003_1920x1080_scrot.png'
        fehmatcher = FehSaveFileMatcher()
        result = fehmatcher(filename)
        assert result == {
            'other_filename': '2015-06-12-233003_1920x1080_scrot.png',
            'feh_prefix': 'feh_016660_000004_',
            'filename': 'feh_016660_000004_2015-06-12-233003_1920x1080_scrot.png'
        }


class TestPsOutputMatcher(object):
    def test_output_line(self):
        line = 'postgres  1022     1 ?        /usr/lib/postgresql/9.4/bin/postgres -D /var/lib/postgresql/9.4/main -c config_file=/etc/postgresql/9.4/main/postgresql.conf'
        psmatcher = PsOutputMatcher()
        result = psmatcher(line)
        assert result == {
            'cmd': '/usr/lib/postgresql/9.4/bin/postgres -D /var/lib/postgresql/9.4/main -c config_file=/etc/postgresql/9.4/main/postgresql.conf',
            'tty': '?',
            'ppid': 1,
            'pid': 1022,
            'user': 'postgres'
        }


class TestZshHistoryLineMatcher(object):
    def test_hist_line(self):
        line = ': 1430044418:137;sudo vim /etc/default/grub'
        zshmatcher = ZshHistoryLineMatcher()
        result = zshmatcher(line)
        assert result == {
            'duration': 137,
            'timestamp': datetime.datetime(2015, 4, 26, 5, 33, 38),
            'cmd': 'sudo vim /etc/default/grub'
        }


class TestSpecialTextMultiMatcher(object):
    def test_line_with_debug(self):
        line = 'This #line has #tags (things starting with "#")... and SpecialTextMultiMatcher will match http://some.link.net  # also has comments and parentheses'
        stm = SpecialTextMultiMatcher(debug=True)
        result = stm(line)
        assert result == {
            '_key_matcher_dict': {
                'capitalized_phrase_list': 'CapitalizedPhraseMatcher',
                'doublequoted_list': 'DoubleQuoteMatcher',
                'line_comment': 'CommentMatcher',
                'text': 'IdentityMatcher',
                'non_comment': 'CommentMatcher',
                'non_url_text': 'NonUrlTextMatcher',
                'paren_group_list': 'ParenMatcher',
                'tag_list': 'TagMatcher',
                'url_list': 'UrlMatcher'
            },
            'capitalized_phrase_list': ['This', 'SpecialTextMultiMatcher'],
            'doublequoted_list': ['#'],
            'line_comment': 'also has comments and parentheses',
            'text': 'This #line has #tags (things starting with "#")... and SpecialTextMultiMatcher will match http://some.link.net  # also has comments and parentheses',
            'non_comment': 'This #line has #tags (things starting with "#")... and SpecialTextMultiMatcher will match http://some.link.net',
            'non_url_text': 'This #line has #tags (things starting with "#")... and SpecialTextMultiMatcher will match # also has comments and parentheses',
            'paren_group_list': ['things starting with "#"'],
            'tag_list': ['line', 'tags'],
            'url_list': ['http://some.link.net']
        }


class TestMasterMatcher(object):
    def test_several(self):
        """Gonna leave this gnarly test for now"""
        line = 'http://umich.edu/~archive/mac/game/war/bolo/misc/recgamesbolofaq1.9.txt Bolo 0.99.2 FAQ'
        line2 = ': 1430044418:137;sudo vim /etc/default/grub'
        filename = '2015_0526--2014_00--cb120--496x212.png'
        mastermatcher = MasterMatcher()
        result = mastermatcher(line)
        assert result['non_url_text'] == 'Bolo 0.99.2 FAQ'
        assert result['url_details_list'][0]['domain'] == 'umich.edu'
        result2 = mastermatcher(filename)
        assert result2['hostname'] == 'cb120'
        result3 = mastermatcher(line2)
        assert result3['timestamp'].month == 4

    def test_empty(self):
        line = ''
        mm = MasterMatcher()
        result = mm(line)
        assert result == {'text': ''}

    def test_empty_with_debug(self):
        line = ''
        mm = MasterMatcher(debug=True)
        result = mm(line)
        assert result == {
            '_key_matcher_dict': {'text': 'IdentityMatcher'},
            'text': ''
        }

    def test_simple_line1(self):
        line = 'Checkout the #kenjyco repo: https://github.com/kenjyco/kenjyco'
        mm = MasterMatcher()
        result = mm(line)
        assert result == {
            'tag_list': ['kenjyco'],
            'capitalized_phrase_list': ['Checkout'],
            'non_url_text': 'Checkout the #kenjyco repo:',
            'text': 'Checkout the #kenjyco repo: https://github.com/kenjyco/kenjyco',
            'url_details_list': [
                {
                    'domain': 'github.com',
                    'path': {
                        'full_path': '/kenjyco/kenjyco',
                        'uri': '/kenjyco/kenjyco'
                    },
                    'protocol': 'https',
                    'full_url': 'https://github.com/kenjyco/kenjyco',
                    'filename_prefix': 'github.com--kenjyco--kenjyco'
                }
            ],
            'url_list': ['https://github.com/kenjyco/kenjyco']
        }

    def test_simple_line2_with_debug(self):
        line = 'http://www.amazon.com/Practical-Vim-Thought-Pragmatic-Programmers/dp/1934356980/ref=sr_1_1?ie=UTF8&qid=1434287619&sr=8-1&keywords=vim+book&pebp=1434287625417&perid=25745CD3359A47339D43 #Vim book that is supposed to be real good'
        mm = MasterMatcher(debug=True)
        result = mm(line)
        assert result == {
            '_key_matcher_dict': {
                'non_url_text': 'NonUrlTextMatcher',
                'tag_list': 'TagMatcher',
                'url_details_list': 'UrlDetailsMatcher',
                'url_list': 'UrlMatcher',
                'text': 'IdentityMatcher'
            },
            'non_url_text': '#Vim book that is supposed to be real good',
            'tag_list': ['Vim'],
            'text': 'http://www.amazon.com/Practical-Vim-Thought-Pragmatic-Programmers/dp/1934356980/ref=sr_1_1?ie=UTF8&qid=1434287619&sr=8-1&keywords=vim+book&pebp=1434287625417&perid=25745CD3359A47339D43 #Vim book that is supposed to be real good',
            'url_details_list': [
                {
                    'domain': 'amazon.com',
                    'full_url': 'http://www.amazon.com/Practical-Vim-Thought-Pragmatic-Programmers/dp/1934356980/ref=sr_1_1?ie=UTF8&qid=1434287619&sr=8-1&keywords=vim+book&pebp=1434287625417&perid=25745CD3359A47339D43',
                    'filename_prefix': 'www.amazon.com--Practical-Vim-Thought-Pragmatic-Programmers--dp--1934356980--ref%3Dsr_1_1%3Fie%3DUTF8%26qid%3D1434287619%26sr%3D8-1%26keywords%3Dvim%2Bbook%26pebp%3D1434287625417%26perid%3D25745CD3359A47339D43',
                    'path': {
                        'full_path': '/Practical-Vim-Thought-Pragmatic-Programmers/dp/1934356980/ref=sr_1_1?ie=UTF8&qid=1434287619&sr=8-1&keywords=vim+book&pebp=1434287625417&perid=25745CD3359A47339D43',
                        'parameters': {
                            'ie': 'UTF8',
                            'keywords': 'vim+book',
                            'pebp': '1434287625417',
                            'perid': '25745CD3359A47339D43',
                            'qid': '1434287619',
                            'sr': '8-1'
                        },
                        'querystring': 'ie=UTF8&qid=1434287619&sr=8-1&keywords=vim+book&pebp=1434287625417&perid=25745CD3359A47339D43',
                        'uri': '/Practical-Vim-Thought-Pragmatic-Programmers/dp/1934356980/ref=sr_1_1'
                    },
                    'protocol': 'http'
                }
            ],
            'url_list': ['http://www.amazon.com/Practical-Vim-Thought-Pragmatic-Programmers/dp/1934356980/ref=sr_1_1?ie=UTF8&qid=1434287619&sr=8-1&keywords=vim+book&pebp=1434287625417&perid=25745CD3359A47339D43']
        }
