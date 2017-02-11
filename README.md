#### Install

```
% pip install input-helper
```

#### Usage

```
% ipython
...

In [1]: import input_helper as ih

In [2]: real_args = ih.string_to_set('arg1, arg2, arg3')

In [3]: real_val = ih.from_string('true')

In [4]: response = ih.user_input('type some input, human')

In [5]: selected = ih.make_selections(list_of_items)

In [6]: seconds = ih.timestamp_to_seconds('1h22m33s')

In [7]: urls = ih.get_all_urls('some-file-with-urls.txt', 'https://blah.net')

In [8]: from input_helper import matcher

In [9]: from pprint import pprint

In [10]: mm = matcher.MasterMatcher(debug=True)

In [11]: pprint(mm('@handle1 and @handle2 here are the #docs you requested https://github.com/kenjyco/input-helper/blob/master/README.md'))
{'_key_matcher_dict': {'line_orig': 'IdentityMatcher',
                       'mention_list': 'MentionMatcher',
                       'non_url_text': 'NonUrlTextMatcher',
                       'tag_list': 'TagMatcher',
                       'url_list': 'UrlMatcher'},
 'line_orig': '@handle1 and @handle2 here are the #docs you requested '
              'https://github.com/kenjyco/input-helper/blob/master/README.md',
 'mention_list': ['handle1', 'handle2'],
 'non_url_text': '@handle1 and @handle2 here are the #docs you requested',
 'tag_list': ['docs'],
 'url_list': [{'domain': 'github.com',
               'filename_prefix': 'github.com--kenjyco--input-helper--blob--master--README.md',
               'full_url': 'https://github.com/kenjyco/input-helper/blob/master/README.md',
               'path': {'full_path': '/kenjyco/input-helper/blob/master/README.md',
                        'uri': '/kenjyco/input-helper/blob/master/README.md'},
               'protocol': 'https'}]}
```
