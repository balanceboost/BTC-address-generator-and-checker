![btc checker](https://github.com/user-attachments/assets/03bc3630-9c96-4567-94b4-6abf9518fd13)
Эта программа предназначена для максимально быстрой генерации Bitcoin-адресов и проверки их на наличие в списке. Программа поддерживает многопоточную обработку и два метода генерации адресов: с высокой энтропией и с низкой энтропией. 

Требования:
Для работы программы необходимы следующие зависимости:
Python 3.8+

Модули Python:

    pip install ecdsa base58 aiofiles pyfiglet termcolor

Файлы:

    RichBTC.txt — файл, содержащий список BTC-адресов (по одному на строку).
    FoundBTC.txt — файл для записи найденных совпадений адресов с приватными ключами.
    state.txt — файл для хранения текущего состояния программы (счетчик сгенерированных адресов).

Запуск программы:

    Скачайте или клонируйте репозиторий с программой.
    git clone https://github.com/yourusername/repository-name.git
    
Подготовьте файл RichBTC.txt, содержащий список Bitcoin-адресов.

Запустите программу:

    python script_name.py

Вам будет предложено выбрать метод генерации:

    1 — Высокая энтропия (32 байта для генерации ключа).
    2 — Низкая энтропия (16 байт для генерации ключа).
    
Программа автоматически запустит многопоточную генерацию адресов и начнет проверку каждого из них.

Примечания:
Программа сохраняет состояние (количество сгенерированных адресов) каждые 100,000 адресов. В случае прерывания работы, программа продолжит генерацию с того места, где остановилась.
Выводится статистика о количестве сгенерированных адресов и скорости генерации в реальном времени.
Файл FoundBTC.txt будет содержать адреса, найденные в списке, и соответствующие им приватные ключи в WIF-формате.

    Для поддержки автора: TFbR9gXb5r6pcALasjX1FKBArbKc4xBjY8
--------------------------------------------------------------------------------------------------------------------------
![btc checker](https://github.com/user-attachments/assets/03bc3630-9c96-4567-94b4-6abf9518fd13)
This program is designed to fasters generate Bitcoin addresses and check them against a list. The program supports multi-threaded processing and offers two address generation methods: high entropy and low entropy.

Requirements:
The following dependencies are required for the program to run:
Python 3.8+

Python modules:

    pip install ecdsa base58 aiofiles pyfiglet termcolor

Files:

    RichBTC.txt — a file containing a list of rich BTC addresses (one per line).
    FoundBTC.txt — a file where found matches of addresses and private keys will be written.
    state.txt — a file to store the program's current state (the number of generated addresses).

How to Run:

    Download or clone the repository with the program.
    git clone https://github.com/yourusername/repository-name.git
    
Prepare the RichBTC.txt file containing a list of Bitcoin addresses.

Run the program:

    python script_name.py
    
You will be prompted to select the generation method:

    1 — High entropy (32 bytes for key generation).
    2 — Low entropy (16 bytes for key generation).
    
The program will automatically start multi-threaded address generation and checking for each address.

Notes:
The program saves the state (number of generated addresses) every 100,000 addresses. If interrupted, it will resume from where it left off.
Real-time statistics are shown, including the total number of generated addresses and generation speed.
The FoundBTC.txt file will contain addresses found in the list and their corresponding private keys in WIF format.

    To support the author: TFbR9gXb5r6pcALasjX1FKBArbKc4xBjY8

