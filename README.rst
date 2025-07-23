A practical utility library for transforming data, handling user input,
and parsing text in Python. Built for interactive development workflows
where you need to quickly process messy real-world data without
wrestling with configuration or format conversion.

This library works immediately without setup ceremonies, accepts
inconsistent input gracefully, and fails helpfully when things go wrong.
Functions are designed around common patterns in data science, CLI
tools, DevOps automation, and exploratory programming.

**Who benefits from this library:** - Data scientists working with
inconsistent input formats - CLI tool builders who need robust text
processing - DevOps engineers automating data transformation tasks -
Anyone prototyping data processing pipelines interactively - Developers
tired of writing the same input handling code repeatedly

This library prioritizes **data integrity** and **cognitive load
reduction**. Key design principles: - **Format Agnosticism**: Functions
accept multiple input formats rather than enforcing strict types -
**Conservative Type Conversion**: Preserves data semantics (like leading
zeros) rather than aggressive normalization - **Graceful Degradation**:
Multiple fallback strategies before giving up - **Self-Documenting**:
Function names describe behavior clearly, reducing documentation
dependency - **REPL-Optimized**: Designed for interactive development
with immediate feedback - **Stateless**: No global configuration or
hidden state; same inputs always produce same outputs

Tested for Python 3.5 - 3.13.

Install
-------

::

   pip install input-helper

Dependencies
~~~~~~~~~~~~

Core functionality requires only Python standard library. Optional
features: - **xmljson**: For XML parsing
(``pip install input-helper[xmljson]``) - **IPython**: For enhanced REPL
sessions (``pip install input-helper[ipython]``)

QuickStart
----------

.. code:: python

   import input_helper as ih

   # Transform messy string data into clean Python objects
   data = ih.string_to_converted_list('dog, 01, 2, 3.10, none, true')
   # Returns: ['dog', '01', 2, 3.1, None, True]
   # Note: leading zeros preserved (often semantic), types inferred safely

   # Parse complex nested structures with dot notation
   nested_data = {
       'order': {'details': {'price': 99.99, 'items': ['phone', 'case']}},
       'user': {'name': 'John', 'verified': True}
   }
   price = ih.get_value_at_key(nested_data, 'order.details.price')  # 99.99
   items = ih.get_value_at_key(nested_data, 'order.details.items')  # ['phone', 'case']

   # Extract structured data from natural text
   mm = ih.matcher.MasterMatcher(debug=True)
   result = mm('@john check out #python https://python.org for more info')
   # Returns rich dictionary with mentions, tags, URLs, and metadata

   # Interactive selection menus with flexible input
   options = ['option1', 'option2', 'option3', 'option4', 'option5']
   selected = ih.make_selections(options)
   # Displays numbered menu, handles ranges (1-3), multiple selections (1 3 5)

   # Selection menus with structured data
   servers = [
       {'name': 'web01', 'status': 'running', 'cpu': 45},
       {'name': 'db01', 'status': 'stopped', 'cpu': 0},
       {'name': 'cache01', 'status': 'running', 'cpu': 78}
   ]
   selected_servers = ih.make_selections(servers, item_format='{name} ({status}) - CPU: {cpu}%')
   # Displays: "web01 (running) - CPU: 45%" etc.

   # Flexible argument handling
   args = ih.get_list_from_arg_strings('a,b,c', ['d', 'e'], 'f,g')
   # Returns: ['a', 'b', 'c', 'd', 'e', 'f', 'g']

**What you gain:** Immediate productivity with real-world data. No setup
overhead, no silent failures, no format wrestling. Functions adapt to
your data instead of forcing you to adapt to the library.

API Overview
------------

Core Data Transformation
~~~~~~~~~~~~~~~~~~~~~~~~

Type Conversion
^^^^^^^^^^^^^^^

-  **``from_string(val, keep_num_as_string=False)``** - Smart
   string-to-type conversion with leading zero preservation

   -  ``val``: String or any value to convert
   -  ``keep_num_as_string``: If True, preserve numeric strings as
      strings
   -  Returns: Converted value (bool, None, int, float, or original
      string)
   -  Internal calls: None (pure implementation)

-  **``string_to_list(s)``** - Split strings on common delimiters
   (comma, semicolon, pipe)

   -  ``s``: String to split or existing list (passed through)
   -  Returns: List of trimmed strings
   -  Internal calls: None (pure implementation)

-  **``string_to_set(s)``** - Convert string to set, handling delimiters
   and duplicates

   -  ``s``: String to split or existing list/set
   -  Returns: Set of unique strings
   -  Internal calls: None (pure implementation)

-  **``string_to_converted_list(s, keep_num_as_string=False)``** -
   Combines splitting and type conversion

   -  ``s``: Delimited string
   -  ``keep_num_as_string``: Preserve numeric strings as strings
   -  Returns: List with appropriate Python types
   -  Internal calls: ``from_string()``, ``string_to_list()``

Flexible Input Processing
^^^^^^^^^^^^^^^^^^^^^^^^^

-  **``get_list_from_arg_strings(*args)``** - Universal argument
   flattening

   -  ``*args``: Any combination of strings, lists, nested structures
   -  Returns: Flattened list of strings (handles recursive nesting)
   -  Internal calls: ``string_to_list()``,
      ``get_list_from_arg_strings()`` (recursive)

-  **``decode(obj, encoding='utf-8')``** - Safe string decoding with
   fallback

   -  ``obj``: Object to decode (bytes or other)
   -  ``encoding``: Target encoding
   -  Returns: Decoded string or original object if not bytes
   -  Internal calls: None (pure implementation)

Data Structure Manipulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dictionary Operations
^^^^^^^^^^^^^^^^^^^^^

-  **``get_value_at_key(some_dict, key, condition=None)``** - Extract
   values with dot notation

   -  ``some_dict``: Source dictionary
   -  ``key``: Simple key or nested path like ‘user.profile.name’
   -  ``condition``: Optional filter function for list values
   -  Returns: Value at key path, filtered if condition provided
   -  Internal calls: None (pure implementation)

-  **``filter_keys(some_dict, *keys, **conditions)``** - Extract and
   filter nested data

   -  ``some_dict``: Source dictionary
   -  ``*keys``: Key paths to extract
   -  ``**conditions``: Field-specific filter functions
   -  Returns: New dictionary with filtered data
   -  Internal calls: ``get_list_from_arg_strings()``,
      ``get_value_at_key()``

-  **``flatten_and_ignore_keys(some_dict, *keys)``** - Flatten nested
   dict, optionally ignoring patterns

   -  ``some_dict``: Nested dictionary to flatten
   -  ``*keys``: Key patterns to ignore (supports wildcards)
   -  Returns: Flat dictionary with dot-notation keys
   -  Internal calls: ``get_list_from_arg_strings()``

-  **``unflatten_keys(flat_dict)``** - Reconstruct nested structure from
   flat dictionary

   -  ``flat_dict``: Dictionary with dot-notation keys
   -  Returns: Nested dictionary structure
   -  Internal calls: None (pure implementation)

-  **``ignore_keys(some_dict, *keys)``** - Remove specified keys from
   dictionary

   -  ``some_dict``: Source dictionary
   -  ``*keys``: Keys or key patterns to remove
   -  Returns: New dictionary without specified keys
   -  Internal calls: ``get_list_from_arg_strings()``

Advanced Dictionary Operations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  **``rename_keys(some_dict, **mapping)``** - Rename dictionary keys

   -  ``some_dict``: Source dictionary
   -  ``**mapping``: old_key=new_key pairs
   -  Returns: Dictionary with renamed keys
   -  Internal calls: None (pure implementation)

-  **``cast_keys(some_dict, **casting)``** - Apply type conversion to
   specific keys

   -  ``some_dict``: Source dictionary
   -  ``**casting``: key=conversion_function pairs
   -  Returns: Dictionary with type-converted values
   -  Internal calls: None (pure implementation)

-  **``sort_by_keys(some_dicts, *keys, reverse=False)``** - Sort list of
   dicts by key values

   -  ``some_dicts``: List of dictionaries
   -  ``*keys``: Keys to sort by (priority order)
   -  ``reverse``: Sort direction
   -  Returns: Sorted list of dictionaries
   -  Internal calls: ``get_list_from_arg_strings()``

-  **``find_items(some_dicts, terms)``** - Query list of dicts with
   flexible operators

   -  ``some_dicts``: List of dictionaries to search
   -  ``terms``: Query string like ‘status:active, price:>100’
   -  Returns: Generator of matching dictionaries
   -  Internal calls: ``string_to_set()``,
      ``get_list_from_arg_strings()``, ``get_value_at_key()``,
      ``from_string()``, ``_less_than()``, ``_less_than_or_equal()``,
      ``_greater_than()``, ``_greater_than_or_equal()``,
      ``_sloppy_equal()``, ``_sloppy_not_equal()``

Text Processing and Parsing
~~~~~~~~~~~~~~~~~~~~~~~~~~~

String Utilities
^^^^^^^^^^^^^^^^

-  **``splitlines(s)``** - Split text on line breaks, preserve empty
   lines

   -  ``s``: String to split
   -  Returns: List of lines
   -  Internal calls: None (pure implementation)

-  **``splitlines_and_strip(s)``** - Split and trim whitespace from each
   line

   -  ``s``: String to split
   -  Returns: List of trimmed lines
   -  Internal calls: None (pure implementation)

-  **``make_var_name(s)``** - Convert string to valid Python variable
   name

   -  ``s``: String to convert
   -  Returns: Valid Python identifier
   -  Internal calls: None (pure implementation)

-  **``get_keys_in_string(s)``** - Extract {placeholder} keys from
   format strings

   -  ``s``: Format string with {key} placeholders
   -  Returns: List of key names
   -  Internal calls: Uses module-level ``cm`` (CurlyMatcher instance)

Data Format Conversion
^^^^^^^^^^^^^^^^^^^^^^

-  **``string_to_obj(s, convention='BadgerFish', **kwargs)``** - Parse
   JSON or XML strings

   -  ``s``: JSON or XML string (auto-detected)
   -  ``convention``: XML parsing convention
   -  Returns: Python dict/list
   -  Internal calls: ``_clean_obj_string_for_parsing()``,
      ``get_obj_from_xml()``, ``get_obj_from_json()``

-  **``get_obj_from_json(json_text, cleaned=False)``** - Parse JSON with
   error recovery

   -  ``json_text``: JSON string
   -  ``cleaned``: Skip string cleaning
   -  Returns: Python object
   -  Internal calls: ``_clean_obj_string_for_parsing()``,
      ``yield_objs_from_json()``

-  **``get_obj_from_xml(xml_text, convention='BadgerFish', warn=True, cleaned=False, **kwargs)``**
   - Parse XML to dict

   -  ``xml_text``: XML string
   -  ``convention``: XML-to-dict conversion style
   -  ``warn``: Show warnings for missing dependencies
   -  Returns: Python dictionary
   -  Internal calls: ``_clean_obj_string_for_parsing()``

-  **``yield_objs_from_json(json_text, pos=0, decoder=JSONDecoder(), cleaned=False)``**
   - Stream JSON objects

   -  ``json_text``: JSON string (potentially multi-object)
   -  ``pos``: Starting position
   -  ``decoder``: Custom JSON decoder
   -  Returns: Generator of Python objects
   -  Internal calls: ``_clean_obj_string_for_parsing()``

Time and Version Handling
^^^^^^^^^^^^^^^^^^^^^^^^^

-  **``timestamp_to_seconds(timestamp)``** - Parse time strings to
   seconds

   -  ``timestamp``: String like ‘1h30m45s’ or ‘01:30:45’
   -  Returns: Total seconds as number
   -  Internal calls: None (pure implementation)

-  **``seconds_to_timestamps(seconds)``** - Convert seconds to multiple
   time formats

   -  ``seconds``: Number of seconds
   -  Returns: Dict with ‘colon’, ‘hms’, and ‘pretty’ formats
   -  Internal calls: None (pure implementation)

-  **``string_to_version_tuple(s)``** - Parse version strings

   -  ``s``: Version string like ‘1.2.3’
   -  Returns: Tuple (major_int, minor_int, patch_string)
   -  Internal calls: None (pure implementation)

User Interaction
~~~~~~~~~~~~~~~~

Input Collection
^^^^^^^^^^^^^^^^

-  **``user_input(prompt_string='input', ch='> ')``** - Basic user input
   with prompt

   -  ``prompt_string``: Prompt text
   -  ``ch``: Prompt suffix
   -  Returns: User input string (empty on Ctrl+C)
   -  Internal calls: None (pure implementation)

-  **``user_input_fancy(prompt_string='input', ch='> ')``** - Input with
   automatic text parsing

   -  ``prompt_string``: Prompt text
   -  ``ch``: Prompt suffix
   -  Returns: Dictionary with optional keys: ``allcaps_phrase_list``,
      ``backtick_list``, ``capitalized_phrase_list``,
      ``curly_group_list``, ``doublequoted_list``, ``mention_list``,
      ``paren_group_list``, ``singlequoted_list``, ``tag_list``,
      ``url_list``, ``line_comment``, ``non_comment``, ``non_url_text``,
      ``text``
   -  Internal calls: ``user_input()``, uses module-level ``sm``
      (SpecialTextMultiMatcher instance)

-  **``user_input_unbuffered(prompt_string='input', ch='> ', raise_interrupt=False)``**
   - Single character input

   -  ``prompt_string``: Prompt text
   -  ``ch``: Prompt suffix
   -  ``raise_interrupt``: Raise KeyboardInterrupt on Ctrl+C
   -  Returns: Single character or empty string
   -  Internal calls: ``getchar()``

Interactive Selection
^^^^^^^^^^^^^^^^^^^^^

-  **``make_selections(items, prompt='', wrap=True, item_format='', unbuffered=False, one=False, raise_interrupt=False, raise_exception_chars=[])``**
   - Generate selection menus

   -  ``items``: List of items to choose from
   -  ``prompt``: Menu prompt text
   -  ``wrap``: Wrap long lines
   -  ``item_format``: Format string for dict/tuple items
   -  ``unbuffered``: Single-key selection mode
   -  ``one``: Return single item instead of list
   -  ``raise_interrupt``: If True and unbuffered is True, raise
      KeyboardInterrupt when Ctrl+C is pressed
   -  ``raise_exception_chars``: List of characters that will raise a
      generic exception if typed while unbuffered is True
   -  Returns: List of selected items (or single item if ``one=True``)
   -  Internal calls: ``get_string_maker()``,
      ``user_input_unbuffered()``, ``user_input()``,
      ``get_selection_range_indices()``, uses module-level ``CH2NUM``,
      ``NUM2CH``

-  **``get_selection_range_indices(start, stop)``** - Generate index
   ranges for selections

   -  ``start``: Start index (numeric or alphanumeric)
   -  ``stop``: End index (inclusive)
   -  Returns: List of indices between start and stop
   -  Internal calls: Uses module-level ``CH2NUM``

Pattern Matching (input_helper.matcher)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Matcher Classes
^^^^^^^^^^^^^^^

-  **``MasterMatcher(debug=False)``** - Comprehensive text analysis

   -  ``debug``: Include execution metadata in results
   -  Extracts: URLs, mentions (@user), hashtags (#tag), quotes, dates,
      file paths
   -  Returns: Rich dictionary with all found patterns

-  **``SpecialTextMultiMatcher(debug=False)``** - Common text pattern
   extraction

   -  Subset of MasterMatcher focused on social media patterns
   -  Extracts: mentions, tags, URLs, quotes, parenthetical text

Individual Matchers (Composable)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  **``AllCapsPhraseMatcher``** - Extract ALL CAPS PHRASES
-  **``BacktickMatcher``** - Extract ``backtick quoted`` text
-  **``CapitalizedPhraseMatcher``** - Extract Capitalized Phrases
-  **``CommentMatcher``** - Separate comments from code/text
-  **``CurlyMatcher``** - Extract {placeholder} patterns
-  **``DatetimeMatcher``** - Extract date/time patterns
-  **``DollarCommandMatcher``** - Extract $(command) patterns
-  **``DoubleQuoteMatcher``** - Extract “double quoted” text
-  **``FehSaveFileMatcher``** - Parse feh image viewer save patterns
-  **``LeadingSpacesMatcher``** - Count leading whitespace
-  **``MentionMatcher``** - Extract @mentions
-  **``NonUrlTextMatcher``** - Extract non-URL text portions
-  **``ParenMatcher``** - Extract parenthetical content
-  **``PsOutputMatcher``** - Parse process list output
-  **``ScrotFileMatcher``** - Parse screenshot filename patterns
-  **``ScrotFileMatcher2``** - Parse alternative screenshot filename
   patterns
-  **``SingleQuoteMatcher``** - Extract ‘single quoted’ text (avoiding
   apostrophes)
-  **``TagMatcher``** - Extract #hashtags
-  **``UrlDetailsMatcher``** - Extract URLs with detailed parsing
   (domain, path, parameters)
-  **``UrlMatcher``** - Extract URLs from text
-  **``ZshHistoryLineMatcher``** - Parse zsh history file entries

Utility Functions
~~~~~~~~~~~~~~~~~

List Operations
^^^^^^^^^^^^^^^

-  **``chunk_list(some_list, n)``** - Split list into chunks of size n

   -  ``some_list``: List to chunk
   -  ``n``: Chunk size
   -  Returns: Generator of list chunks
   -  Internal calls: None (pure implementation)

-  **``unique_counted_items(items)``** - Count unique items with
   ordering

   -  ``items``: Iterable of items
   -  Returns: List of (count, item) tuples, sorted by count
   -  Internal calls: None (pure implementation)

Advanced Utilities
^^^^^^^^^^^^^^^^^^

-  **``get_string_maker(item_format='', missing_key_default='')``** -
   Create safe formatting functions

   -  ``item_format``: Format string with {key} placeholders
   -  ``missing_key_default``: Default for missing keys
   -  Returns: Function that safely formats data
   -  Internal calls: ``get_keys_in_string()``

-  **``parse_command(input_line)``** - Parse command strings with
   flexible delimiters

   -  ``input_line``: Command string like ‘cmd arg1 arg2’ or ‘cmd item –
      item – item –’
   -  Returns: Dict with ‘cmd’ and ‘args’ keys
   -  Internal calls: None (pure implementation)

-  **``start_ipython(warn=True, colors=True, vi=True, confirm_exit=False, **things)``**
   - Launch IPython session

   -  ``warn``: Show warnings if IPython unavailable
   -  ``colors``: Enable syntax highlighting
   -  ``vi``: Use vi editing mode
   -  ``confirm_exit``: Prompt before exit
   -  ``**things``: Objects to pre-load in namespace
   -  Internal calls: None (external dependencies only)

-  **``get_all_urls(*urls_or_filenames)``** - Extract URLs from files or
   strings

   -  ``*urls_or_filenames``: Mix of URLs and files containing URLs
   -  Returns: List of discovered URLs
   -  Internal calls: Uses module-level ``um`` (UrlMatcher instance)

MasterMatcher Example
---------------------

.. code:: python

   In [1]: import input_helper as ih

   In [2]: from pprint import pprint

   In [3]: mm = ih.matcher.MasterMatcher(debug=True)

   In [4]: pprint(mm('@handle1 and @handle2 here are the #docs you requested https://github.com/kenjyco/input-helper/blob/master/README.md'))
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

   In [5]: ih.user_input_fancy()
   input> go to https://github.com/kenjyco for a good time #learning stuff
   Out[5]:
   {'line_orig': 'go to https://github.com/kenjyco for a good time #learning stuff',
    'non_url_text': 'go to for a good time #learning stuff',
    'tag_list': ['learning'],
    'url_list': ['https://github.com/kenjyco']}
