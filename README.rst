Install
^^^^^^^

::

    % pip install input-helper

Usage
^^^^^

::

    % ipython
    ...

    In [1]: import input_helper as ih

    In [2]: real_args = ih.string_to_set('arg1, arg2, arg3')

    In [3]: real_val = ih.from_string('true')

    In [4]: response = ih.user_input('type some input, human')

    In [5]: selected = ih.make_selections(list_of_items)

    In [6]: seconds = ih.timestamp_to_seconds('1h22m33s')

    In [7]: urls = ih.get_all_urls('some-file-with-urls.txt', 'https://blah.net')

    In [8]: from pprint import pprint

    In [9]: mm = ih.matcher.MasterMatcher(debug=True)

    In [10]: pprint(mm('@handle1 and @handle2 here are the #docs you requested https://github.com/kenjyco/input-helper/blob/master/README.md'))
    {'_key_matcher_dict': {'mention_list': 'MentionMatcher',
                           'non_url_text': 'NonUrlTextMatcher',
                           'tag_list': 'TagMatcher',
                           'text': 'IdentityMatcher',
                           'url_details_list': 'UrlDetailsMatcher',
                           'url_list': 'UrlMatcher'},
     'mention_list': ['handle1', 'handle2'],
     'non_url_text': '@handle1 and @handle2 here are the #docs you requested',
     'tag_list': ['docs'],
     'text': '@handle1 and @handle2 here are the #docs you requested '
             'https://github.com/kenjyco/input-helper/blob/master/README.md',
     'url_details_list': [{'domain': 'github.com',
                           'filename_prefix': 'github.com--kenjyco--input-helper--blob--master--README.md',
                           'full_url': 'https://github.com/kenjyco/input-helper/blob/master/README.md',
                           'path': {'full_path': '/kenjyco/input-helper/blob/master/README.md',
                                    'uri': '/kenjyco/input-helper/blob/master/README.md'},
                           'protocol': 'https'}],
     'url_list': ['https://github.com/kenjyco/input-helper/blob/master/README.md']}

    In [11]: ih.user_input_fancy()
    input> go to https://github.com/kenjyco for a good time #learning stuff
    Out[11]:
    {'line_orig': 'go to https://github.com/kenjyco for a good time #learning stuff',
     'non_url_text': 'go to for a good time #learning stuff',
     'tag_list': ['learning'],
     'url_list': ['https://github.com/kenjyco']}
