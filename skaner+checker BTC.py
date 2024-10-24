import os
import time
import ecdsa
import hashlib
import base58
import aiofiles
import asyncio
from multiprocessing import Manager, Process
import pyfiglet
from termcolor import colored

# Файлы для работы
RICH_FILE = 'RichBTC.txt'
FOUND_FILE = 'FoundBTC.txt'
STATE_FILE = 'state.txt'

# Чтение состояния
async def read_state():
    if os.path.exists(STATE_FILE):
        async with aiofiles.open(STATE_FILE, 'r') as f:
            state = await f.read()  # Читаем содержимое
            try:
                return int(state.strip()) if state.strip() else 0  # Убираем пробелы и проверяем
            except ValueError:
                print("Ошибка: состояние не является целым числом. Устанавливаем состояние в 0.")
                return 0  # Возвращаем 0, если возникла ошибка
    return 0  # Возвращаем 0, если файл пуст или не существует

# Сохранение состояния
async def save_state(state):
    async with aiofiles.open(STATE_FILE, 'w') as f:
        await f.write(str(state))

# Генерация приватного ключа и адресов BTC с высокой энтропией
def generate_btc_address_high_entropy():
    private_key = os.urandom(32)
    sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    public_key = b'\x04' + vk.to_string()

    # P2PKH (Legacy)
    hash160 = hashlib.new('ripemd160', hashlib.sha256(public_key).digest()).digest()
    address_legacy = base58.b58encode_check(b'\x00' + hash160).decode()

    # P2SH (Segwit)
    redeem_script = hashlib.new('ripemd160', hashlib.sha256(public_key).digest()).digest()
    address_p2sh = base58.b58encode_check(b'\x05' + redeem_script).decode()

    # Bech32 (Segwit)
    sha256_pk = hashlib.sha256(public_key).digest()
    ripemd160_pk = hashlib.new('ripemd160', sha256_pk).digest()
    address_bech32 = 'bc1' + base58.b58encode_check(ripemd160_pk).decode()[1:]

    return private_key, [address_legacy, address_p2sh, address_bech32]

# Генерация приватного ключа и адресов BTC с низкой энтропией
def generate_btc_address_low_entropy():
    # Генерация безопасного низкоэнтропийного ключа (допустимый диапазон)
    private_key = os.urandom(16) # Замените значение для изменения уровня энтропии (По умолчанию 16)
    private_key_int = int.from_bytes(private_key, 'big') % (ecdsa.SECP256k1.order - 1) + 1
    sk = ecdsa.SigningKey.from_secret_exponent(private_key_int, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    public_key = b'\x04' + vk.to_string()

    # P2PKH (Legacy)
    hash160 = hashlib.new('ripemd160', hashlib.sha256(public_key).digest()).digest()
    address_legacy = base58.b58encode_check(b'\x00' + hash160).decode()

    # P2SH (Segwit)
    redeem_script = hashlib.new('ripemd160', hashlib.sha256(public_key).digest()).digest()
    address_p2sh = base58.b58encode_check(b'\x05' + redeem_script).decode()

    # Bech32 (Segwit)
    sha256_pk = hashlib.sha256(public_key).digest()
    ripemd160_pk = hashlib.new('ripemd160', sha256_pk).digest()
    address_bech32 = 'bc1' + base58.b58encode_check(ripemd160_pk).decode()[1:]

    return private_key, [address_legacy, address_p2sh, address_bech32]

# Функция для генерации адресов в зависимости от выбора метода
def generate_btc_address(method='high'):
    if method == 'low':
        return generate_btc_address_low_entropy()
    else:
        return generate_btc_address_high_entropy()

# Асинхронная функция для записи найденных адресов в файл
async def write_found_address(address, private_key_wif):
    async with aiofiles.open(FOUND_FILE, 'a') as f:
        await f.write(f'{address}, {private_key_wif}\n')

# Функция для проверки адресов
async def check_addresses(worker_id, start_state, progress_dict, rich_addresses, method):
    found = 0
    generated = 0
    state = start_state

    while True:  # Бесконечный цикл генерации и проверки адресов
        private_key, addresses = generate_btc_address(method)

        for address in addresses:
            generated += 1
            if address in rich_addresses:  # Проверка на наличие адреса в rich_addresses
                private_key_wif = base58.b58encode_check(b'\x80' + private_key).decode()  # Кодируем только найденные адреса
                await write_found_address(address, private_key_wif)  # Асинхронная запись
                found += 1

        # Обновление прогресса для текущего потока
        progress_dict[worker_id] = (generated, found)

        # Периодическое сохранение прогресса в файл
        if generated % 100 == 0:
            await save_state(state)
        state += 1

# Процесс вывода статистики
def print_progress(progress_dict):
    start_time = time.time()
    total_generated = 0
    total_found = 0

    while True:
        time.sleep(1)  # Обновление каждые 1 секунду
        total_generated = sum([val[0] for val in progress_dict.values()])
        total_found = sum([val[1] for val in progress_dict.values()])
        elapsed_time = time.time() - start_time
        speed = total_generated / elapsed_time if elapsed_time > 0 else 0

        # Формируем весь вывод с окрашиванием
        output_text = (
            f'Всего сгенерировано: {total_generated}, '
            f'Скорость: {speed:.2f} адр./сек, '
            f'Время работы: {elapsed_time:.2f} секунд, '
            f'Найдено совпадений: {colored(total_found, "green" if total_found > 0 else "red")}'
        )
        # Окрашиваем всю строку
        print(f'\r{colored(output_text, "cyan")}', end='', flush=True)

# Функция для создания и запуска процессов
def start_worker(worker_id, start_state, progress_dict, rich_addresses, method):
    asyncio.run(check_addresses(worker_id, start_state, progress_dict, rich_addresses, method))

# Основная функция для многопроцессорного запуска
async def main(num_workers, method):
    start_state = await read_state()
    # Загрузка rich адресов в память
    with open(RICH_FILE, 'r') as rich_file:
        rich_addresses = set(line.strip() for line in rich_file)  # Хранение адресов в памяти

    # Общий словарь для хранения прогресса каждого потока
    with Manager() as manager:
        progress_dict = manager.dict({i: (0, 0) for i in range(num_workers)})

        # Запускаем процесс, который будет выводить прогресс
        progress_printer = Process(target=print_progress, args=(progress_dict,))
        progress_printer.start()

        # Запускаем процессы для генерации адресов
        processes = []
        for i in range(num_workers):
            p = Process(target=start_worker, args=(i, start_state, progress_dict, rich_addresses, method))
            processes.append(p)
            p.start()
        for p in processes:
            p.join()  # Ожидаем завершения всех процессов
        progress_printer.join()  # Ожидаем завершения процесса вывода статистики

if __name__ == '__main__':

    # Выводим ASCII-арт только в основном процессе
    ascii_art = pyfiglet.figlet_format("BTC keys generator and checker", font="standard")
    colored_art = colored(ascii_art, 'cyan') 
    print(colored_art)

    # Вывод описания методов генерации с окрашиванием
    description_text = (
        "Выберите метод генерации:\n"
        "1. Высокая энтропия: Генерация приватного ключа с использованием случайных байтов (32 байта).\n"
        "2. Низкая энтропия: Генерация приватного ключа с использованием случайных байтов (16 байт).\n"
    )
    print(colored(description_text, 'cyan'))
    # Выбор метода генерации через ввод цифры
    choice = input(colored("Введите номер метода (1 или 2): ", 'cyan')).strip()
    method = 'high' if choice == '1' else 'low' if choice == '2' else 'high'

    # Указываем количество рабочих процессов (по умолчанию 6)
    num_workers = os.cpu_count() or 6

    # Запускаем главную асинхронную функцию
    asyncio.run(main(num_workers, method))