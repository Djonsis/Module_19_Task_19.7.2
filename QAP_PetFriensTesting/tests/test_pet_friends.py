import requests

from api import PetFriends
from settings import valid_email, valid_password
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Барбоскин', animal_type='двортерьер',
                                     age='4', pet_photo='images/cat1.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")

def test_set_photo_with_valid_data():
    """Проверяем возможность установки фото питомца"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список своих питомцев не пустой, то попробуем установить фото первому питомцу
    if len(my_pets['pets']) > 0:
        pet_id = my_pets['pets'][0]['id']
        pet_photo = os.path.join(os.path.dirname(__file__), "images/cat1.jpg")
        status, result = pf.set_photo(auth_key, pet_id, pet_photo)

        # Проверяем что статус ответа = 200 и есть ключ "photo" в результате
        assert status == 200
        assert 'photo' in result
    else:
        # Если список своих питомцев пустой, выбрасываем исключение
        raise Exception("There is no my pets")

def test_set_photo_with_invalid_pet_id():
    """Проверяем, что установка фото с некорректным ID питомца возвращает ошибку"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    invalid_pet_id = "invalid_id"
    pet_photo = os.path.join(os.path.dirname(__file__), "images/p1040103.jpg")
    status, result = pf.set_photo(auth_key, invalid_pet_id, pet_photo)

    # Проверяем что статус ответа = 400 и есть ключ "error" в результате
    assert status == 400
    assert 'error' in result

def test_create_pet_simple_with_valid_data():
    """Проверяем возможность создания простого питомца"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    name = "Мурзик"
    animal_type = "Кот"
    age = 3
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
    assert status == 200
    assert result['name'] == name

def test_create_pet_simple_with_invalid_age():
    """Проверяем, что создание питомца с некорректным возрастом возвращает ошибку. В этом тесте выявил баг:
    можно в поле возраст указать буквенное значение"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    name = "Мурзик"
    animal_type = "Кот"
    age = "abc"
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    # Проверяем что статус ответа = 400 и есть ключ "error" в результате
    assert status == 400
    assert 'error' in result

if __name__ == '__main__':
    import pytest
    pytest.main(['-v', '-s', 'test_pet_friends.py'])
