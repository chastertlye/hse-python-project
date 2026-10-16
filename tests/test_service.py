import pytest
from game.protocols import AlreadyActiveGameError, NoActiveGameError
from game.service import GameService, RandomWordPicker


class FakeModel:
    def similarity(self, word1: str, word2: str) -> float:
        return 0.5


class FakePicker:
    def __init__(self, word: str = "папоротник") -> None:
        self.word = word

    def pick(self) -> str:
        return self.word


def test_start_game_and_repeat_fails():
    service = GameService(model=FakeModel(), picker=FakePicker())
    service.start_game(user_id=1)
    assert service.has_active_game(1) is True

    # Повторный запуск вызывает AlreadyActiveGameError и не сбрасывает игру
    with pytest.raises(AlreadyActiveGameError):
        service.start_game(user_id=1)
    assert service.has_active_game(1) is True


def test_make_guess_flow():
    service = GameService(model=FakeModel(), picker=FakePicker("папоротник"))
    service.start_game(user_id=1)

    # Пустая попытка не меняет состояние
    with pytest.raises(ValueError):
        service.make_guess(user_id=1, text="   ")

    # Неверная попытка
    res1 = service.make_guess(user_id=1, text="дерево")
    assert res1.is_correct is False
    assert res1.attempts == 1
    assert res1.similarity == 0.5
    assert service.has_active_game(1) is True

    # Верная попытка (без учета регистра и пробелов)
    res2 = service.make_guess(user_id=1, text="  ПаПоРоТнИк  ")
    assert res2.is_correct is True
    assert res2.attempts == 2
    assert res2.similarity == 1.0
    assert service.has_active_game(1) is False


def test_stop_game():
    service = GameService(model=FakeModel(), picker=FakePicker())
    service.start_game(user_id=1)
    service.stop_game(user_id=1)
    assert service.has_active_game(1) is False

    with pytest.raises(NoActiveGameError):
        service.stop_game(user_id=1)


def test_random_word_picker():
    picker = RandomWordPicker()
    word = picker.pick()
    assert isinstance(word, str)
    assert len(word) > 0
