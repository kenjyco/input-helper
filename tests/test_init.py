import pytest
import input_helper as ih


@pytest.fixture
def some_dict():
    d = {
        'Thing': -5,
        'Dogs': [10, 3],
        'Cats': [2, 4, 8, 12, 19, 22],
        'Birds': [
            {'Key': 'Name', 'Value': 'Some bird'},
            {'Key': 'Misc', 'Value': 'Whatever'},
            {'Key': 'Other', 'Value': 'Hello'},
            {'Key': 'Name', 'Value': 'Another bird'},
        ],
        'Mice': {
            'a': 5,
            'b': -10,
            'c': [1, 2, 3]
        }
    }
    return d


@pytest.fixture
def some_dicts():
    ds = [
        {
            'status': 'running',
            'name': 'first',
            'thing': {
                'a': 1,
                'b': 2
            }
        },
        {
            'status': 'running',
            'name': 'second',
            'thing': {
                'a': 10,
                'b': 5
            }
        },
        {
            'status': 'stopped',
            'name': 'third',
            'thing': {
                'a': 0,
                'b': 0
            }
        },
        {
            'status': 'running',
            'name': 'fourth',
            'thing': {
                'a': 10,
                'b': 2
            }
        },
        {
            'status': 'unknown',
            'name': 'fifth',
            'thing': {
                'a': 10,
                'b': 20
            }
        },
    ]
    return ds


@pytest.fixture
def some_dicts2():
    ds = [
        {
            'id': 'abc-12345',
            'name': 'first',
        },
        {
            'id': 'def-67890',
            'name': 'second',
        },
        {
            'id': 'hij-12390',
            'name': 'third',
        },
        {
            'id': 'klm-789',
            'name': 'fourth',
        },
    ]
    return ds


class TestMiscThings(object):
    def test_get_list_from_arg_strings(self):
        result = ih.get_list_from_arg_strings(
            ['apple', 'cat', 'dog'],
            'rat, mouse',
            'orange',
            'potato'
        )
        assert result == ['apple', 'cat', 'dog', 'rat', 'mouse', 'orange', 'potato']


class TestDictThings(object):
    def test_filter_keys(self, some_dict):
        result = ih.filter_keys(
            some_dict,
            'Dogs, Cats, Birds.Value',
            'Monkey.Thing.Value',
            Birds__Value=lambda x: x.get('Key') == 'Name',
            Cats=lambda x: x>10,
            Dogs=lambda x: x<5
        )
        assert result == {
            'Dogs': 3,
            'Cats': [12, 19, 22],
            'Birds__Value': ['Some bird', 'Another bird'],
            'Monkey__Thing__Value': None
        }

    def test_ignore_keys(self, some_dict):
        result = ih.ignore_keys(
            some_dict,
            'Thing, Birds',
            'Dogs',
        )
        assert result == {
            'Cats': [2, 4, 8, 12, 19, 22],
            'Mice': {
                'a': 5,
                'b': -10,
                'c': [1, 2, 3]
            }
        }

    def test_find_items_simple(self, some_dicts):
        result = list(ih.find_items(some_dicts, 'thing.a:10'))
        assert result == [
            {
                'status': 'running',
                'name': 'second',
                'thing': {
                    'a': 10,
                    'b': 5
                }
            },
            {
                'status': 'running',
                'name': 'fourth',
                'thing': {
                    'a': 10,
                    'b': 2
                }
            },
            {
                'status': 'unknown',
                'name': 'fifth',
                'thing': {
                    'a': 10,
                    'b': 20
                }
            }
        ]

    def test_find_items_simple_multi(self, some_dicts):
        result = list(ih.find_items(some_dicts, 'thing.a:10, status:unknown, status:stopped'))
        assert result == [
            {
                'status': 'unknown',
                'name': 'fifth',
                'thing': {
                    'a': 10,
                    'b': 20
                }
            }
        ]

    def test_find_items_simple_multi2(self, some_dicts):
        result = list(ih.find_items(some_dicts, 'thing.a:10, thing.a:0, status:unknown, status:stopped'))
        assert result == [
            {
                'status': 'stopped',
                'name': 'third',
                'thing': {
                    'a': 0,
                    'b': 0
                }
            },
            {
                'status': 'unknown',
                'name': 'fifth',
                'thing': {
                    'a': 10,
                    'b': 20
                }
            }
        ]

    def test_find_items_operator_less_num(self, some_dicts):
        result = list(ih.find_items(some_dicts, 'thing.a:<10'))
        assert result == [
            {
                'status': 'running',
                'name': 'first',
                'thing': {
                    'a': 1,
                    'b': 2
                }
            },
            {
                'status': 'stopped',
                'name': 'third',
                'thing': {
                    'a': 0,
                    'b': 0
                }
            }
        ]

    def test_find_items_operator_less_str(self, some_dicts):
        result = list(ih.find_items(some_dicts, 'name:<fourth'))
        assert result == [
            {
                'status': 'running',
                'name': 'first',
                'thing': {
                    'a': 1,
                    'b': 2
                }
            },
            {
                'status': 'unknown',
                'name': 'fifth',
                'thing': {
                    'a': 10,
                    'b': 20
                }
            },
        ]

    def test_find_items_operator_lessequal_num(self, some_dicts):
        result = list(ih.find_items(some_dicts, 'thing.a:<=10'))
        assert result == [
            {
                'status': 'running',
                'name': 'first',
                'thing': {
                    'a': 1,
                    'b': 2
                }
            },
            {
                'status': 'running',
                'name': 'second',
                'thing': {
                    'a': 10,
                    'b': 5
                }
            },
            {
                'status': 'stopped',
                'name': 'third',
                'thing': {
                    'a': 0,
                    'b': 0
                }
            },
            {
                'status': 'running',
                'name': 'fourth',
                'thing': {
                    'a': 10,
                    'b': 2
                }
            },
            {
                'status': 'unknown',
                'name': 'fifth',
                'thing': {
                    'a': 10,
                    'b': 20
                }
            },
        ]

    def test_find_items_operator_lessequal_str(self, some_dicts):
        result = list(ih.find_items(some_dicts, 'status:<=runnings'))
        assert result == [
            {
                'status': 'running',
                'name': 'first',
                'thing': {
                    'a': 1,
                    'b': 2
                }
            },
            {
                'status': 'running',
                'name': 'second',
                'thing': {
                    'a': 10,
                    'b': 5
                }
            },
            {
                'status': 'running',
                'name': 'fourth',
                'thing': {
                    'a': 10,
                    'b': 2
                }
            },
        ]

    def test_find_items_operator_greater_num(self, some_dicts):
        result = list(ih.find_items(some_dicts, 'thing.a:>10'))
        assert result == []

    def test_find_items_operator_greater_str(self, some_dicts):
        result = list(ih.find_items(some_dicts, 'name:>fourth'))
        assert result == [
            {
                'status': 'running',
                'name': 'second',
                'thing': {
                    'a': 10,
                    'b': 5
                }
            },
            {
                'status': 'stopped',
                'name': 'third',
                'thing': {
                    'a': 0,
                    'b': 0
                }
            },
        ]

    def test_find_items_operator_greaterequal_num(self, some_dicts):
        result = list(ih.find_items(some_dicts, 'thing.a:>=10'))
        assert result == [
            {
                'status': 'running',
                'name': 'second',
                'thing': {
                    'a': 10,
                    'b': 5
                }
            },
            {
                'status': 'running',
                'name': 'fourth',
                'thing': {
                    'a': 10,
                    'b': 2
                }
            },
            {
                'status': 'unknown',
                'name': 'fifth',
                'thing': {
                    'a': 10,
                    'b': 20
                }
            },
        ]

    def test_find_items_operator_greaterequal_str(self, some_dicts):
        result = list(ih.find_items(some_dicts, 'status:>=stop'))
        assert result == [
            {
                'status': 'stopped',
                'name': 'third',
                'thing': {
                    'a': 0,
                    'b': 0
                }
            },
            {
                'status': 'unknown',
                'name': 'fifth',
                'thing': {
                    'a': 10,
                    'b': 20
                }
            },
        ]

    def test_find_items_operator_notequal_num(self, some_dicts):
        result = list(ih.find_items(some_dicts, 'thing.a:!10'))
        assert result == [
            {
                'status': 'running',
                'name': 'first',
                'thing': {
                    'a': 1,
                    'b': 2
                }
            },
            {
                'status': 'stopped',
                'name': 'third',
                'thing': {
                    'a': 0,
                    'b': 0
                }
            },
        ]

    def test_find_items_operator_notequal_str(self, some_dicts):
        result = list(ih.find_items(some_dicts, 'status:!running'))
        assert result == [
            {
                'status': 'stopped',
                'name': 'third',
                'thing': {
                    'a': 0,
                    'b': 0
                }
            },
            {
                'status': 'unknown',
                'name': 'fifth',
                'thing': {
                    'a': 10,
                    'b': 20
                }
            },
        ]

    def test_find_items_operator_equal_num(self, some_dicts):
        result = list(ih.find_items(some_dicts, 'thing.a:==10'))
        assert result == [
            {
                'status': 'running',
                'name': 'second',
                'thing': {
                    'a': 10,
                    'b': 5
                }
            },
            {
                'status': 'running',
                'name': 'fourth',
                'thing': {
                    'a': 10,
                    'b': 2
                }
            },
            {
                'status': 'unknown',
                'name': 'fifth',
                'thing': {
                    'a': 10,
                    'b': 20
                }
            },
        ]

    def test_find_items_operator_equal_str(self, some_dicts):
        result = list(ih.find_items(some_dicts, 'name:==first, name:==fifth'))
        assert result == [
            {
                'status': 'running',
                'name': 'first',
                'thing': {
                    'a': 1,
                    'b': 2
                }
            },
            {
                'status': 'unknown',
                'name': 'fifth',
                'thing': {
                    'a': 10,
                    'b': 20
                }
            },
        ]

    def test_find_items_operator_sloppyequal_str(self, some_dicts):
        result = list(ih.find_items(some_dicts, 'status:$run'))
        assert result == [
            {
                'status': 'running',
                'name': 'first',
                'thing': {
                    'a': 1,
                    'b': 2
                }
            },
            {
                'status': 'running',
                'name': 'second',
                'thing': {
                    'a': 10,
                    'b': 5
                }
            },
            {
                'status': 'running',
                'name': 'fourth',
                'thing': {
                    'a': 10,
                    'b': 2
                }
            },
        ]

    def test_find_items_operator_sloppyequal_str2(self, some_dicts):
        result = list(ih.find_items(some_dicts, 'status:$KNOWN'))
        assert result == [
            {
                'status': 'unknown',
                'name': 'fifth',
                'thing': {
                    'a': 10,
                    'b': 20
                }
            },
        ]

    def test_find_items_operator_sloppyequal_mixed(self, some_dicts2):
        result = list(ih.find_items(some_dicts2, 'id:$23'))
        assert result == [
            {
                'id': 'abc-12345',
                'name': 'first',
            },
            {
                'id': 'hij-12390',
                'name': 'third',
            },
        ]

    def test_find_items_operator_sloppynotequal_str(self, some_dicts):
        result = list(ih.find_items(some_dicts, 'status:~run'))
        assert result == [
            {
                'status': 'stopped',
                'name': 'third',
                'thing': {
                    'a': 0,
                    'b': 0
                }
            },
            {
                'status': 'unknown',
                'name': 'fifth',
                'thing': {
                    'a': 10,
                    'b': 20
                }
            },
        ]

    def test_find_items_operator_sloppynotequal_str2(self, some_dicts):
        result = list(ih.find_items(some_dicts, 'status:~RUN'))
        assert result == [
            {
                'status': 'stopped',
                'name': 'third',
                'thing': {
                    'a': 0,
                    'b': 0
                }
            },
            {
                'status': 'unknown',
                'name': 'fifth',
                'thing': {
                    'a': 10,
                    'b': 20
                }
            },
        ]

    def test_find_items_operator_sloppynotequal_mixed(self, some_dicts2):
        result = list(ih.find_items(some_dicts2, 'id:~23'))
        assert result == [
            {
                'id': 'def-67890',
                'name': 'second',
            },
            {
                'id': 'klm-789',
                'name': 'fourth',
            },
        ]

    def test_find_items_operator_sloppy_complex(self, some_dicts):
        result = list(ih.find_items(some_dicts, 'thing.a:<=10, thing.b:<10, status:$run'))
        assert result == [
            {
                'status': 'running',
                'name': 'first',
                'thing': {
                    'a': 1,
                    'b': 2
                }
            },
            {
                'status': 'running',
                'name': 'second',
                'thing': {
                    'a': 10,
                    'b': 5
                }
            },
            {
                'status': 'running',
                'name': 'fourth',
                'thing': {
                    'a': 10,
                    'b': 2
                }
            },
        ]
