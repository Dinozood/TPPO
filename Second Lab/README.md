# Лабораторная работа №2 
В данной директории находятся 2 файла, tppo_server2232.py, tppo_client2232.py, представляющие собой скрипт сервера и 
клиента соответственно. Для того, что бы запустить сервер, необходимо установить зависимости с помощью команды  
~~~ 
python3 -m pip install -r requirements.txt.
~~~   


Изначально запускается сервер, затем, запускается какое-то количество клиентов

По сути данная работа не сильно отличается от предыдущей, теперь после запуска сервера, с ним можно взаимодействовать с
помощью приложений, поддерживающих REST API. Примеры использования:
~~~
curl http://127.0.0.1:1337/device/whole_info - Получить всю информацию об устройстве  
curl http://127.0.0.1:1337/device/regime  - Получить информацию о установленном режиме устройства
curl http://127.0.0.1:1337/device\?regime\=5  - Установить режим устройства
curl http://127.0.0.1:1337/device\?regime\=5\&target_temp\=25  - Установить режим устройства и целевую температуру
curl http://127.0.0.1:1337/device/check - Простой пинг, перешедший из предыдущей лабораторной
~~~

### Запуск сервера
python3 tppo_server_2232.py **[addr]** **[port]** - Опции необязательны, дефолтные
параметры addr - 127.0.0.1 и port - 1337

### Запуск клиента
python3 tppo_client_2232.py **[addr]** **[port]** - Опции необязательны, дефолтные
параметры addr - 127.0.0.1 и port - 1337

Работа со стороны клиента, описана в справочном сообщении, которое можно вызвать с помощью команды TIP

Так же для каждого скрипта существует возможность вызова справочного сообщения.

#### P.S.

Файлы [First_tppo_server_2232.py](First_tppo_server_2232.py) и [First_tppo_client_2232.py](First_tppo_client_2232.py)
это просто скопированные скрипты первой лабораторной работы, т.к. хотелось максимально
использовать во второй лабораторной уже написанное в первой.
