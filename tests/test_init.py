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
def some_dict2():
    d = {
        'order': {
            'id': 12345,
            'details': {
                'price': 99.99,
                'productDescription': 'Latest model smartphone with advanced features',
                'productID': 'E1234',
                'productName': 'Smartphone',
                'productType': 'Electronics',
                'promoCode': 'DISCOUNT20',
                'quantity': 1
            }
        },
        'user': {
            'address': {
                'city': 'New York',
                'zipcode': '10001'
            },
            'name': 'John Doe'
        },
        'user_ok': True
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
        {
            'status': None,
            'name': 'sixth',
            'thing': {
                'a': 15,
                'b': 21
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


class Test__string_to_version_tuple(object):
    def test_no_patch1(self):
        assert ih.string_to_version_tuple('0.4') == (0, 4, '')

    def test_no_patch2(self):
        assert ih.string_to_version_tuple('10.5') == (10, 5, '')

    def test_no_patch3(self):
        assert ih.string_to_version_tuple('3.10') == (3, 10, '')

    def test_with_patch1(self):
        assert ih.string_to_version_tuple('10.5.2') == (10, 5, '2')

    def test_with_patch2(self):
        assert ih.string_to_version_tuple('0.5.3a') == (0, 5, '3a')

    def test_with_patch3(self):
        assert ih.string_to_version_tuple('8.5.4-rc1') == (8, 5, '4-rc1')

    def test_with_patch4(self):
        assert ih.string_to_version_tuple('2.0.5.post1') == (2, 0, '5.post1')


class Test__from_string(object):
    def test_none(self):
        assert ih.from_string('none') is None
        assert ih.from_string('None') is None
        assert ih.from_string(None) is None

    def test_bool(self):
        assert ih.from_string('true') is True
        assert ih.from_string('True') is True
        assert ih.from_string('TRUE') is True
        assert ih.from_string(True) is True
        assert ih.from_string('false') is False
        assert ih.from_string('False') is False
        assert ih.from_string('FALSE') is False
        assert ih.from_string(False) is False

    def test_int(self):
        value = ih.from_string('10')
        assert type(value) == int
        value = ih.from_string(10)
        assert type(value) == int

    def test_float(self):
        value = ih.from_string('10.0')
        assert type(value) == float
        value = ih.from_string('10.0000')
        assert type(value) == float
        value = ih.from_string(10.0)
        assert type(value) == float

    def test_leading_zeroes_string(self):
        assert type(ih.from_string('1')) == int
        assert type(ih.from_string('.50')) == float
        assert type(ih.from_string('0.50')) == float
        assert type(ih.from_string('00.50')) == str
        assert type(ih.from_string('0.5.0')) == str
        assert type(ih.from_string('01')) == str
        assert type(ih.from_string('00001')) == str
        assert ih.from_string('00001') == '00001'

    def test_num_values(self):
        value = ih.from_string('10.0000')
        assert value == 10.0
        value = ih.from_string('10.00004')
        assert value == 10.00004
        value = ih.from_string('10.0000', keep_num_as_string=True)
        assert value == '10.0000'
        value = ih.from_string('.10')
        assert value == 0.1
        value = ih.from_string('.10', keep_num_as_string=True)
        assert value == '.10'

    def test_object(self):
        assert type(ih.from_string('{"a": 1, "b": 2}')) == str
        assert type(ih.from_string({"a": 1, "b": 2})) == dict
        assert type(ih.from_string('[1, 2]')) == str
        assert type(ih.from_string([1, 2])) == list


class Test__get_list_from_arg_strings(object):
    def test_single_arg1(self):
        result = ih.get_list_from_arg_strings('dog')
        assert result == ['dog']

    def test_single_arg2(self):
        result = ih.get_list_from_arg_strings(['dog', 'cat', 3])
        assert result == ['dog', 'cat', '3']

    def test_single_arg3(self):
        result = ih.get_list_from_arg_strings('dog, cat, mouse')
        assert result == ['dog', 'cat', 'mouse']

    def test_nested_with_non_strings(self):
        result = ih.get_list_from_arg_strings(100, 400, [1, 2, 3, ['04', '05']])
        assert result == ['100', '400', '1', '2', '3', '04', '05']


class TestCompareThings(object):
    def test_less_num(self):
        assert ih._less_than(5, 6)
        assert ih._less_than(5, 6.6)
        assert ih._less_than('5', 6)
        assert ih._less_than(5, '6.6')
        assert not ih._less_than(5, 5)
        assert not ih._less_than(5, None)
        assert not ih._less_than(None, 5)

    def test_less_str(self):
        assert ih._less_than('5', 'Z')
        assert ih._less_than('A', 'a')
        assert ih._less_than('Z', 'a')
        assert ih._less_than('aa', 'aaa')
        assert not ih._less_than('aa', 'aa')
        assert not ih._less_than('aa', 'aAa')
        assert not ih._less_than('a', None)
        assert not ih._less_than(None, 'a')

    def test_less_mixed(self):
        assert ih._less_than([1, 2], [1, 3])
        assert not ih._less_than([1, 2], [1, 2])
        assert not ih._less_than(1, [1, 3])
        assert not ih._less_than([1, 3], 1)
        assert not ih._less_than({'a': 1}, 'abc')
        assert not ih._less_than('abc', {'a': 1})

    def test_lessequal_num(self):
        assert ih._less_than_or_equal(5, 6)
        assert ih._less_than_or_equal(5, 6.6)
        assert ih._less_than_or_equal('5', 6)
        assert ih._less_than_or_equal(5, '6.6')
        assert ih._less_than_or_equal(5, 5)
        assert not ih._less_than_or_equal(5, None)
        assert not ih._less_than_or_equal(None, 5)

    def test_lessequal_str(self):
        assert ih._less_than_or_equal('5', 'Z')
        assert ih._less_than_or_equal('A', 'a')
        assert ih._less_than_or_equal('Z', 'a')
        assert ih._less_than_or_equal('aa', 'aaa')
        assert ih._less_than_or_equal('aa', 'aa')
        assert not ih._less_than_or_equal('aa', 'aAa')
        assert not ih._less_than_or_equal('a', None)
        assert not ih._less_than_or_equal(None, 'a')

    def test_lessequal_mixed(self):
        assert ih._less_than_or_equal([1, 2], [1, 3])
        assert ih._less_than_or_equal([1, 2], [1, 2])
        assert not ih._less_than_or_equal(1, [1, 3])
        assert not ih._less_than_or_equal([1, 3], 1)
        assert not ih._less_than_or_equal({'a': 1}, 'abc')
        assert not ih._less_than_or_equal('abc', {'a': 1})

    def test_greater_num(self):
        assert ih._greater_than(7, 6)
        assert ih._greater_than(7, 6.6)
        assert ih._greater_than('7', 6)
        assert ih._greater_than(7, '6.6')
        assert not ih._greater_than(7, 7)
        assert not ih._greater_than(7, None)
        assert not ih._greater_than(None, 7)

    def test_greater_str(self):
        assert ih._greater_than('Z', '5')
        assert ih._greater_than('a', 'A')
        assert ih._greater_than('a', 'Z')
        assert ih._greater_than('aaa', 'aa')
        assert not ih._greater_than('aa', 'aa')
        assert not ih._greater_than('aAa', 'aa')
        assert not ih._greater_than('a', None)
        assert not ih._greater_than(None, 'a')

    def test_greater_mixed(self):
        assert ih._greater_than([1, 3], [1, 2])
        assert not ih._greater_than([1, 2], [1, 2])
        assert not ih._greater_than(1, [1, 3])
        assert not ih._greater_than([1, 3], 1)
        assert not ih._less_than({'a': 1}, 'abc')
        assert not ih._less_than('abc', {'a': 1})

    def test_greaterequal_num(self):
        assert ih._greater_than_or_equal(7, 6)
        assert ih._greater_than_or_equal(7, 6.6)
        assert ih._greater_than_or_equal('7', 6)
        assert ih._greater_than_or_equal(7, '6.6')
        assert ih._greater_than_or_equal(7, 7)
        assert not ih._greater_than_or_equal(7, None)
        assert not ih._greater_than_or_equal(None, 7)

    def test_greaterequal_str(self):
        assert ih._greater_than_or_equal('Z', '5')
        assert ih._greater_than_or_equal('a', 'A')
        assert ih._greater_than_or_equal('a', 'Z')
        assert ih._greater_than_or_equal('aaa', 'aa')
        assert ih._greater_than_or_equal('aa', 'aa')
        assert not ih._greater_than_or_equal('aAa', 'aa')
        assert not ih._greater_than_or_equal('a', None)
        assert not ih._greater_than_or_equal(None, 'a')

    def test_greaterequal_mixed(self):
        assert ih._greater_than_or_equal([1, 3], [1, 2])
        assert ih._greater_than_or_equal([1, 2], [1, 2])
        assert not ih._greater_than_or_equal(1, [1, 3])
        assert not ih._greater_than_or_equal([1, 3], 1)
        assert not ih._less_than_or_equal({'a': 1}, 'abc')
        assert not ih._less_than_or_equal('abc', {'a': 1})

    def test_sloppyequal_num(self):
        assert ih._sloppy_equal(12, 123)
        assert ih._sloppy_equal(123, 12)
        assert ih._sloppy_equal('123', 12)
        assert not ih._sloppy_equal(12, 23)
        assert not ih._sloppy_equal(12, None)
        assert not ih._sloppy_equal(None, 12)

    def test_sloppyequal_str(self):
        assert ih._sloppy_equal('aa', 'aaa')
        assert ih._sloppy_equal('Counter-clockwise', 'clock')
        assert ih._sloppy_equal('clock', 'Counter-clockwise')

    def test_sloppyequal_mixed(self):
        assert ih._sloppy_equal('goat', {'animal': 'Goat'})
        assert ih._sloppy_equal({'animal': 'Goat'}, 'goat')
        assert ih._sloppy_equal(50, [1, 40, '500'])
        assert not ih._sloppy_equal({'animal': 'Goat'}, 'goats')

    def test_sloppynotequal_num(self):
        assert ih._sloppy_not_equal(12, 23)
        assert ih._sloppy_not_equal(12, None)
        assert ih._sloppy_not_equal(None, 12)
        assert not ih._sloppy_not_equal(12, 123)
        assert not ih._sloppy_not_equal(123, 12)
        assert not ih._sloppy_not_equal('123', 12)

    def test_sloppynotequal_str(self):
        assert ih._sloppy_not_equal('aba', 'aca')
        assert ih._sloppy_not_equal('dog', 'cat')
        assert ih._sloppy_not_equal('dog', None)

    def test_sloppynotequal_mixed(self):
        assert ih._sloppy_not_equal(5000, [1, 40, '500'])
        assert ih._sloppy_not_equal({'animal': 'Goat'}, 'goats')
        assert not ih._sloppy_not_equal('goat', {'animal': 'Goat'})


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

    def test_flatten_and_ignore_keys__flatten_only(self, some_dict):
        result = ih.flatten_and_ignore_keys(some_dict)
        assert sorted(result.keys()) == [
            'Birds', 'Cats', 'Dogs', 'Mice.a', 'Mice.b', 'Mice.c', 'Thing'
        ]
        assert result['Birds'][-1]['Value'] == 'Another bird'

    def test_flatten_and_ignore_keys__with_ignore_keys(self, some_dict):
        result = ih.flatten_and_ignore_keys(some_dict, 'Thing, Birds, Mice.c, Fake')
        assert sorted(result.keys()) == ['Cats', 'Dogs', 'Mice.a', 'Mice.b']

    def test_flatten_and_ignore_keys__with_ignore_patterns(self, some_dict2):
        assert sorted(ih.flatten_and_ignore_keys(some_dict2).keys()) == [
            'order.details.price', 'order.details.productDescription',
            'order.details.productID', 'order.details.productName',
            'order.details.productType', 'order.details.promoCode',
            'order.details.quantity', 'order.id', 'user.address.city',
            'user.address.zipcode', 'user.name', 'user_ok'
        ]

        result = ih.flatten_and_ignore_keys(some_dict2, 'order.details.prod*')
        assert sorted(result.keys()) == [
            'order.details.price', 'order.details.promoCode',
            'order.details.quantity', 'order.id', 'user.address.city',
            'user.address.zipcode', 'user.name', 'user_ok'
        ]

        result2 = ih.flatten_and_ignore_keys(some_dict2, 'order.details.product[TI]*, user.add*')
        assert sorted(result2.keys()) == [
            'order.details.price', 'order.details.productDescription',
            'order.details.productName', 'order.details.promoCode',
            'order.details.quantity', 'order.id', 'user.name', 'user_ok'
        ]

        result3 = ih.flatten_and_ignore_keys(some_dict2, 'order.details.product[TI]*, user.*')
        assert sorted(result3.keys()) == [
            'order.details.price', 'order.details.productDescription',
            'order.details.productName', 'order.details.promoCode',
            'order.details.quantity', 'order.id', 'user_ok'
        ]

        result4 = ih.flatten_and_ignore_keys(some_dict2, 'order.details.product[TI]*, order.*product???e, us*')
        assert sorted(result4.keys()) == [
            'order.details.price', 'order.details.productDescription',
            'order.details.promoCode', 'order.details.quantity', 'order.id'
        ]

        result5 = ih.flatten_and_ignore_keys(some_dict2, 'order.details.product[J-Z]*, user*')
        assert sorted(result5.keys()) == [
            'order.details.price', 'order.details.productDescription',
            'order.details.productID', 'order.details.promoCode',
            'order.details.quantity', 'order.id'
        ]

    def test_unflatten_keys(self, some_dict2):
        flattened = ih.flatten_and_ignore_keys(some_dict2, 'order.details.product[TI]*, user.add*')
        result = ih.unflatten_keys(flattened)
        assert result == {
            'order': {
                'details': {
                    'price': 99.99,
                    'productDescription': 'Latest model smartphone with advanced features',
                    'productName': 'Smartphone',
                    'promoCode': 'DISCOUNT20',
                    'quantity': 1
                },
                'id': 12345
            },
            'user': {
                'name': 'John Doe'
            },
            'user_ok': True
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
        assert result == [
            {
                'status': None,
                'name': 'sixth',
                'thing': {
                    'a': 15,
                    'b': 21
                }
            }
        ]

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
            {
                'status': None,
                'name': 'sixth',
                'thing': {
                    'a': 15,
                    'b': 21
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
            {
                'status': None,
                'name': 'sixth',
                'thing': {
                    'a': 15,
                    'b': 21
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
            {
                'status': None,
                'name': 'sixth',
                'thing': {
                    'a': 15,
                    'b': 21
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
            {
                'status': None,
                'name': 'sixth',
                'thing': {
                    'a': 15,
                    'b': 21
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
            {
                'status': None,
                'name': 'sixth',
                'thing': {
                    'a': 15,
                    'b': 21
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
            {
                'status': None,
                'name': 'sixth',
                'thing': {
                    'a': 15,
                    'b': 21
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


class TestTimestamps(object):
    def test_seconds_to_timestamps1(self):
        timestamps = ih.seconds_to_timestamps(10)
        assert timestamps == {
            'colon': '00:00:10',
            'hms': '10s',
            'pretty': '10 seconds'
        }

    def test_seconds_to_timestamps2(self):
        timestamps = ih.seconds_to_timestamps(100)
        assert timestamps == {
            'colon': '00:01:40',
            'hms': '1m40s',
            'pretty': '1 minute, 40 seconds'
        }

    def test_seconds_to_timestamps3(self):
        timestamps = ih.seconds_to_timestamps(10000)
        assert timestamps == {
            'colon': '02:46:40',
            'hms': '2h46m40s',
            'pretty': '2 hours, 46 minutes, 40 seconds'
        }

    def test_seconds_to_timestamps4(self):
        timestamps = ih.seconds_to_timestamps(1000000)
        assert timestamps == {
            'colon': '277:46:40',
            'hms': '277h46m40s',
            'pretty': '1 week, 4 days, 13 hours, 46 minutes, 40 seconds'
        }

    def test_seconds_to_timestamps5(self):
        timestamps = ih.seconds_to_timestamps(12345.6789)
        assert timestamps == {
            'colon': '03:25:46',
            'hms': '3h25m46s',
            'pretty': '3 hours, 25 minutes, 45.679 seconds'
        }
