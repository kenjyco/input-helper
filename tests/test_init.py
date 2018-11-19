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


class TestDictThings(object):
    def test_filter_keys(self, some_dict):
        result = ih.filter_keys(
            some_dict,
            'Dogs, Cats, Birds.Value, Monkey.Thing.Value',
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

    def test_find_items_complex(self, some_dicts):
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

    def test_find_items_complex2(self, some_dicts):
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
