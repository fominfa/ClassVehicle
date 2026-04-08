import pytest
from simple_library_01.functions import add

@pytest.mark.parametrize("first, second, third", [
    (1, 2, 3),
    (-2, -3, -5),
    (0, 0 , 0)
])
def test_add(first, second, third):
    assert add(first, second) == third
----------------------------------------------------------------------------------------------------------
test_get_month_days.py
import pytest
from simple_library_01.functions import get_month_days

@pytest.mark.parametrize("year, month, expected", [
    (1930, 2, 30),
    (1930, 20, 30),
    (2024, 2, 29),
    (2023, 2, 28),
    (2021, 4, 30),
    (2019, 6, 30),
    (2017, 9, 30),
    (2013, 11, 30),
    (2023, 1, 31),
    (2023, 3, 31)
])
def test_get_month_days(year, month, expected):
    assert get_month_days(year, month) == expected

@pytest.mark.parametrize("month", [0, 100, -1])
def test_get_month_days_is_invalid_month(month):
    with pytest.raises(AttributeError):
        get_month_days(2023, month)
----------------------------------------------------------------------------------------------------------
test_leap.py
import pytest
from simple_library_01.functions import is_leap


@pytest.mark.parametrize("year, expected", [
    (2023, False),
    (2024, True),
    (100, False),
    (400, True),
])
def test_is_leap(year, expected):
    assert is_leap(year) is expected


@pytest.mark.parametrize("year", [0, -1, -100])
def test_is_leap_invalid_year(year):
    with pytest.raises(AttributeError):
        is_leap(year)

----------------------------------------------------------------------------------------------------------
tree_size_tree.py
import os
import tempfile

import pytest

from tree_utils_02.size_tree import SizeTree, BLOCK_SIZE
from tree_utils_02.size_node import FileSizeNode


@pytest.fixture
def temp_fs():
    with tempfile.TemporaryDirectory() as RootPath:
        APath = os.path.join(RootPath, "a.txt")
        with open(APath, "w") as File:
            File.write("abc")

        BPath = os.path.join(RootPath, "b.txt")
        with open(BPath, "w") as File:
            File.write("hello")

        DirPath = os.path.join(RootPath, "dir")
        os.mkdir(DirPath)

        CPath = os.path.join(DirPath, "c.txt")
        with open(CPath, "w") as File:
            File.write("xx")

        yield {
            "root": RootPath,
            "a": APath,
            "b": BPath,
            "dir": DirPath,
            "c": CPath,
        }


def test_file_size(temp_fs):
    Result = SizeTree().get(temp_fs["a"], dirs_only=False)

    assert isinstance(Result, FileSizeNode)
    assert Result.name == "a.txt"
    assert Result.is_dir is False
    assert Result.children == []
    assert Result.size == 3


def test_empty_dir_size():
    with tempfile.TemporaryDirectory() as RootPath:
        Result = SizeTree().get(RootPath, dirs_only=False)

        assert isinstance(Result, FileSizeNode)
        assert Result.name == os.path.basename(RootPath)
        assert Result.is_dir is True
        assert Result.children == []
        assert Result.size == BLOCK_SIZE


def test_dir_with_files_size(temp_fs):
    Result = SizeTree().get(temp_fs["root"], dirs_only=False)

    ChildrenByName = {Child.name: Child for Child in Result.children}

    assert ChildrenByName["a.txt"].size == 3
    assert ChildrenByName["b.txt"].size == 5


def test_nested_dir_size(temp_fs):
    Result = SizeTree().get(temp_fs["root"], dirs_only=False)

    DirNode = [Child for Child in Result.children if Child.name == "dir"][0]
    CNode = DirNode.children[0]

    assert CNode.name == "c.txt"
    assert CNode.is_dir is False
    assert CNode.size == 2

    assert DirNode.name == "dir"
    assert DirNode.is_dir is True
    assert DirNode.size == BLOCK_SIZE + 2


def test_total_size(temp_fs):
    Result = SizeTree().get(temp_fs["root"], dirs_only=False)

    ChildrenByName = {Child.name: Child for Child in Result.children}
    DirNode = ChildrenByName["dir"]

    ExpectedSize = BLOCK_SIZE + 3 + 5 + DirNode.size

    assert Result.size == ExpectedSize


def test_dirs_only_size(temp_fs):
    Result = SizeTree().get(temp_fs["root"], dirs_only=True)

    assert Result.is_dir is True

    Names = [Child.name for Child in Result.children]
    assert Names == ["dir"]

    DirNode = Result.children[0]
    assert DirNode.name == "dir"
    assert DirNode.is_dir is True
    assert DirNode.size == BLOCK_SIZE

    assert Result.size == BLOCK_SIZE + BLOCK_SIZE
----------------------------------------------------------------------------------------------------------
test_tree.py
import os
import tempfile

import pytest

from tree_utils_02.tree import Tree
from tree_utils_02.node import FileNode


@pytest.fixture
def temp_fs():
    with tempfile.TemporaryDirectory() as RootPath:
        APath = os.path.join(RootPath, "a.txt")
        with open(APath, "w") as File:
            File.write("abc")

        Dir1Path = os.path.join(RootPath, "dir1")
        os.mkdir(Dir1Path)

        BPath = os.path.join(Dir1Path, "b.txt")
        with open(BPath, "w") as File:
            File.write("abc")

        Dir2Path = os.path.join(Dir1Path, "dir2")
        os.mkdir(Dir2Path)

        ZPath = os.path.join(RootPath, "z.txt")
        with open(ZPath, "w") as File:
            File.write("z")

        MPath = os.path.join(RootPath, "m.txt")
        with open(MPath, "w") as File:
            File.write("mm")

        yield {
            "root": RootPath,
            "a": APath,
            "dir1": Dir1Path,
            "b": BPath,
            "dir2": Dir2Path,
            "z": ZPath,
            "m": MPath,
        }


def test_not_existing_path():
    with pytest.raises(AttributeError):
        Tree().get("no_such_path", dirs_only=False)


def test_file_allowed(temp_fs):
    Result = Tree().get(temp_fs["a"], dirs_only=False)

    assert isinstance(Result, FileNode)
    assert Result.name == "a.txt"
    assert Result.is_dir is False
    assert Result.children == []


def test_file_forbidden():
    with tempfile.TemporaryDirectory() as RootPath:
        FilePath = os.path.join(RootPath, "a.txt")
        with open(FilePath, "w") as File:
            File.write("abc")

        with pytest.raises(AttributeError):
            Tree().get(FilePath, dirs_only=True)


def test_full_tree_structure(temp_fs):
    Result = Tree().get(temp_fs["root"], dirs_only=False)

    assert Result.name == os.path.basename(temp_fs["root"])
    assert Result.is_dir is True

    Names = [Child.name for Child in Result.children]
    assert Names == ["a.txt", "dir1", "m.txt", "z.txt"]

    Dir1 = Result.children[1]
    assert Dir1.name == "dir1"
    assert Dir1.is_dir is True

    Dir1Names = [Child.name for Child in Dir1.children]
    assert Dir1Names == ["b.txt", "dir2"]

    BNode = Dir1.children[0]
    assert BNode.name == "b.txt"
    assert BNode.is_dir is False
    assert BNode.children == []

    Dir2 = Dir1.children[1]
    assert Dir2.name == "dir2"
    assert Dir2.is_dir is True
    assert Dir2.children == []


def test_dirs_only(temp_fs):
    Result = Tree().get(temp_fs["root"], dirs_only=True)

    assert Result.name == os.path.basename(temp_fs["root"])
    assert Result.is_dir is True

    Names = [Child.name for Child in Result.children]
    assert Names == ["dir1"]

    Dir1 = Result.children[0]
    assert Dir1.name == "dir1"
    assert Dir1.is_dir is True

    Dir1Names = [Child.name for Child in Dir1.children]
    assert Dir1Names == ["dir2"]


def test_dirs_only_only_files():
    with tempfile.TemporaryDirectory() as RootPath:
        FilePath = os.path.join(RootPath, "a.txt")
        with open(FilePath, "w") as File:
            File.write("abc")

        Result = Tree().get(RootPath, dirs_only=True)

        assert Result.is_dir is True
        assert Result.children == []


def test_filter_file():
    Node = FileNode(
        name="a.txt",
        is_dir=False,
        children=[]
    )

    Tree().filter_empty_nodes(Node)


def test_filter_root_error():
    Node = FileNode(
        name="root",
        is_dir=True,
        children=[]
    )

    with pytest.raises(ValueError):
        Tree().filter_empty_nodes(Node)


def test_remove_empty_dir():
    with tempfile.TemporaryDirectory() as RootPath:
        EmptyDir = os.path.join(RootPath, "empty_dir")
        os.makedirs(EmptyDir)

        Node = FileNode(
            name="empty_dir",
            is_dir=True,
            children=[]
        )

        Tree().filter_empty_nodes(Node, current_path=EmptyDir)

        assert not os.path.exists(EmptyDir)


def test_keep_non_empty_dir():
    with tempfile.TemporaryDirectory() as RootPath:
        DirPath = os.path.join(RootPath, "dir")
        os.makedirs(DirPath)

        FilePath = os.path.join(DirPath, "file.txt")
        with open(FilePath, "w") as File:
            File.write("x")

        Node = FileNode(
            name="dir",
            is_dir=True,
            children=[
                FileNode(
                    name="file.txt",
                    is_dir=False,
                    children=[]
                )
            ]
        )

        Tree().filter_empty_nodes(Node, current_path=DirPath)

        assert os.path.exists(DirPath)
        assert os.path.exists(FilePath)
------------------------------------------------------------------------------------------------------------------------------------------------
import pytest

from weather_03.weather_wrapper import WeatherWrapper, LOCATION_URL, BASE_URL, FORECAST_URL

class FakeResponse():
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self.json_data = json_data

    def json(self):
        return self.json_data

class MockWeatherWrapper(WeatherWrapper):
    def __init__(self, api_key, responses):
        super().__init__(api_key)
        self.responses = responses

    def get(self, city, url):
        key = (city, url)
        return self.responses[key]

def test_init():
    Wrapper = WeatherWrapper("token")

    assert Wrapper.api_key == "token"
    assert Wrapper.location_cache == {}

def test_get_response_city_success():
    Responses = {('Moscow', LOCATION_URL): FakeResponse(200, [{'Key' : '123'}])}

    Wrapper = MockWeatherWrapper('token', Responses)
    Result = Wrapper.get_response_city('Moscow', LOCATION_URL)

    assert Result == [{'Key': '123'}]

def test_get_response_city_error():
    Responses = {('Moscow', LOCATION_URL): FakeResponse(404, [{'Error' : 'Not found'}])}

    Wrapper = MockWeatherWrapper('token', Responses)

    with pytest.raises(AttributeError, match='Incorrect city'):
        Wrapper.get_response_city('Moscow', LOCATION_URL)

def test_get_location_key_from_cache():
    Wrapper = WeatherWrapper('token')
    Wrapper.location_cache['London'] = '404'

    assert Wrapper.get_location_key('London') == '404'

def test_get_location_key_success():
    Responses = {('Moscow', LOCATION_URL): FakeResponse(200, [{'Key' : '123'}])}
    Wrapper = MockWeatherWrapper('token', Responses)

    assert Wrapper.get_location_key('Moscow') == '123'

def test_get_location_key_not_found():
    Responses = {('Moscow', LOCATION_URL): FakeResponse(200, [])}
    Wrapper = MockWeatherWrapper('token', Responses)

    with pytest.raises(ValueError, match='City Moscow not found'):
        Wrapper.get_location_key('Moscow')

def test_get_temperature():
    Responses = {('Moscow', LOCATION_URL): FakeResponse(200, [{'Key' : '123'}]), ('Moscow', BASE_URL + '123'): FakeResponse(200, [{'Temperature': {'Metric': {'Value': 18.5}}}])}
    Wrapper = MockWeatherWrapper('token', Responses)

    assert Wrapper.get_temperature('Moscow') == 18.5

def test_get_tomorrow_temperature():
    Responses = {
        ('Moscow', LOCATION_URL): FakeResponse(200, [{'Key': '123'}]),
        ('Moscow', FORECAST_URL + '123'): FakeResponse(
            200,
            {
                'DailyForecasts': [
                    {'Temperature': {'Maximum': {'Value': 17.0}}},
                    {'Temperature': {'Maximum': {'Value': 21.0}}}
                ]
            }
        )
    }
    Wrapper = MockWeatherWrapper('token', Responses)
    assert Wrapper.get_tomorrow_temperature('Moscow') == 21.0

def test_find_diff_two_cities(monkeypatch):
    Wrapper = MockWeatherWrapper('token', {})

    def MockGetTemperature(city):
        if city == 'London':
            return 10
        return 7

    monkeypatch.setattr(Wrapper, 'get_temperature', MockGetTemperature)

    assert Wrapper.find_diff_two_cities('London', 'Moscow') == 3

def test_get_diff_string_warmer(monkeypatch):
    Wrapper = MockWeatherWrapper('token', {})

    def MockGetTemperature(city):
        if city == 'London':
            return 10
        return 7

    monkeypatch.setattr(Wrapper, 'get_temperature', MockGetTemperature)

    assert Wrapper.get_diff_string('London', 'Moscow') == 'Weather in London is warmer than in Moscow by 3 degrees'

def test_get_diff_string_colder(monkeypatch):
    Wrapper = MockWeatherWrapper('token', {})

    def MockGetTemperature(city):
        if city == 'London':
            return 5
        return 9

    monkeypatch.setattr(Wrapper, 'get_temperature', MockGetTemperature)

    assert Wrapper.get_diff_string('London', 'Moscow') == 'Weather in London is colder than in Moscow by 4 degrees'

def test_get_tomorrow_diff(monkeypatch):
    Wrapper = MockWeatherWrapper('token', {})

    def MockGetTemperature(city):
        return 10

    def MockGetTomorrowTemperature(city):
        return 12

    monkeypatch.setattr(Wrapper, 'get_temperature', MockGetTemperature)
    monkeypatch.setattr(Wrapper, 'get_tomorrow_temperature', MockGetTomorrowTemperature)

    Result = Wrapper.get_tomorrow_diff('London')

    assert Result == 'The weather in London tomorrow will be warmer than today'

def test_get_tomorrow_diff_much_warmer(monkeypatch):
    Wrapper = MockWeatherWrapper('token', {})

    def MockGetTemperature(city):
        return 10

    def MockGetTomorrowTemperature(city):
        return 15

    monkeypatch.setattr(Wrapper, 'get_temperature', MockGetTemperature)
    monkeypatch.setattr(Wrapper, 'get_tomorrow_temperature', MockGetTomorrowTemperature)

    assert Wrapper.get_tomorrow_diff('London') == 'The weather in London tomorrow will be much warmer than today'

def test_get_tomorrow_diff_much_colder(monkeypatch):
    Wrapper = MockWeatherWrapper('token', {})

    def MockGetTemperature(city):
        return 10

    def MockGetTomorrowTemperature(city):
        return 4

    monkeypatch.setattr(Wrapper, 'get_temperature', MockGetTemperature)
    monkeypatch.setattr(Wrapper, 'get_tomorrow_temperature', MockGetTomorrowTemperature)

    assert Wrapper.get_tomorrow_diff('London') == 'The weather in London tomorrow will be much colder than today'
-----------------------------------------------------------------------------------------------------------------------------
test_weather.py
import pytest

from weather_03.weather_wrapper import WeatherWrapper, LOCATION_URL, BASE_URL, FORECAST_URL

class FakeResponse():
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self.json_data = json_data

    def json(self):
        return self.json_data

class MockWeatherWrapper(WeatherWrapper):
    def __init__(self, api_key, responses):
        super().__init__(api_key)
        self.responses = responses

    def get(self, city, url):
        key = (city, url)
        return self.responses[key]

def test_init():
    Wrapper = WeatherWrapper("token")

    assert Wrapper.api_key == "token"
    assert Wrapper.location_cache == {}

def test_get_response_city_success():
    Responses = {('Moscow', LOCATION_URL): FakeResponse(200, [{'Key' : '123'}])}

    Wrapper = MockWeatherWrapper('token', Responses)
    Result = Wrapper.get_response_city('Moscow', LOCATION_URL)

    assert Result == [{'Key': '123'}]

def test_get_response_city_error():
    Responses = {('Moscow', LOCATION_URL): FakeResponse(404, [{'Error' : 'Not found'}])}

    Wrapper = MockWeatherWrapper('token', Responses)

    with pytest.raises(AttributeError, match='Incorrect city'):
        Wrapper.get_response_city('Moscow', LOCATION_URL)

def test_get_location_key_from_cache():
    Wrapper = WeatherWrapper('token')
    Wrapper.location_cache['London'] = '404'

    assert Wrapper.get_location_key('London') == '404'

def test_get_location_key_success():
    Responses = {('Moscow', LOCATION_URL): FakeResponse(200, [{'Key' : '123'}])}
    Wrapper = MockWeatherWrapper('token', Responses)

    assert Wrapper.get_location_key('Moscow') == '123'

def test_get_location_key_not_found():
    Responses = {('Moscow', LOCATION_URL): FakeResponse(200, [])}
    Wrapper = MockWeatherWrapper('token', Responses)

    with pytest.raises(ValueError, match='City Moscow not found'):
        Wrapper.get_location_key('Moscow')

def test_get_temperature():
    Responses = {('Moscow', LOCATION_URL): FakeResponse(200, [{'Key' : '123'}]), ('Moscow', BASE_URL + '123'): FakeResponse(200, [{'Temperature': {'Metric': {'Value': 18.5}}}])}
    Wrapper = MockWeatherWrapper('token', Responses)

    assert Wrapper.get_temperature('Moscow') == 18.5

def test_get_tomorrow_temperature():
    Responses = {
        ('Moscow', LOCATION_URL): FakeResponse(200, [{'Key': '123'}]),
        ('Moscow', FORECAST_URL + '123'): FakeResponse(
            200,
            {
                'DailyForecasts': [
                    {'Temperature': {'Maximum': {'Value': 17.0}}},
                    {'Temperature': {'Maximum': {'Value': 21.0}}}
                ]
            }
        )
    }
    Wrapper = MockWeatherWrapper('token', Responses)
    assert Wrapper.get_tomorrow_temperature('Moscow') == 21.0

def test_find_diff_two_cities(monkeypatch):
    Wrapper = MockWeatherWrapper('token', {})

    def MockGetTemperature(city):
        if city == 'London':
            return 10
        return 7

    monkeypatch.setattr(Wrapper, 'get_temperature', MockGetTemperature)

    assert Wrapper.find_diff_two_cities('London', 'Moscow') == 3

def test_get_diff_string_warmer(monkeypatch):
    Wrapper = MockWeatherWrapper('token', {})

    def MockGetTemperature(city):
        if city == 'London':
            return 10
        return 7

    monkeypatch.setattr(Wrapper, 'get_temperature', MockGetTemperature)

    assert Wrapper.get_diff_string('London', 'Moscow') == 'Weather in London is warmer than in Moscow by 3 degrees'

def test_get_diff_string_colder(monkeypatch):
    Wrapper = MockWeatherWrapper('token', {})

    def MockGetTemperature(city):
        if city == 'London':
            return 5
        return 9

    monkeypatch.setattr(Wrapper, 'get_temperature', MockGetTemperature)

    assert Wrapper.get_diff_string('London', 'Moscow') == 'Weather in London is colder than in Moscow by 4 degrees'

def test_get_tomorrow_diff(monkeypatch):
    Wrapper = MockWeatherWrapper('token', {})

    def MockGetTemperature(city):
        return 10

    def MockGetTomorrowTemperature(city):
        return 12

    monkeypatch.setattr(Wrapper, 'get_temperature', MockGetTemperature)
    monkeypatch.setattr(Wrapper, 'get_tomorrow_temperature', MockGetTomorrowTemperature)

    Result = Wrapper.get_tomorrow_diff('London')

    assert Result == 'The weather in London tomorrow will be warmer than today'

def test_get_tomorrow_diff_much_warmer(monkeypatch):
    Wrapper = MockWeatherWrapper('token', {})

    def MockGetTemperature(city):
        return 10

    def MockGetTomorrowTemperature(city):
        return 15

    monkeypatch.setattr(Wrapper, 'get_temperature', MockGetTemperature)
    monkeypatch.setattr(Wrapper, 'get_tomorrow_temperature', MockGetTomorrowTemperature)

    assert Wrapper.get_tomorrow_diff('London') == 'The weather in London tomorrow will be much warmer than today'

def test_get_tomorrow_diff_much_colder(monkeypatch):
    Wrapper = MockWeatherWrapper('token', {})

    def MockGetTemperature(city):
        return 10

    def MockGetTomorrowTemperature(city):
        return 4

    monkeypatch.setattr(Wrapper, 'get_temperature', MockGetTemperature)
    monkeypatch.setattr(Wrapper, 'get_tomorrow_temperature', MockGetTomorrowTemperature)

    assert Wrapper.get_tomorrow_diff('London') == 'The weather in London tomorrow will be much colder than today'

