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
