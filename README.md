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
```
