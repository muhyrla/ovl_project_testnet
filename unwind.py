from web3 import Web3, HTTPProvider # сама библа веб3
import time                         # необходимо для задержки
import contracts                    # импортируем файлик с abi контракта (пояснение в contracts.py)
import random                       # необходим для рандомной комсы (иногда ругается что одинаковые транзакции с одинаковой комсой)
import os                           # работа с папками

with open('private_addresses.txt','r') as f: # открываем файлик со всеми адресами
    data = f.readlines()                     # берем все строки
    for account in data:                     # перебираем каждый аккаунт
        (address,pvkey) = account.split(':') # разделяем на адрес и приватный ключ
        w3 = Web3(Web3.HTTPProvider("https://kovan.infura.io/v3/3f1bd555eaa14207af96828688cb7a03")) # подключаемся к ноде (пояснение в index.py)
        pvkey = pvkey.replace('\n','')                                                              # нормальный вид файлу приводим
        admin_account = w3.eth.account.privateKeyToAccount(pvkey)                                   # импортим аккаунт по приватке
        if os.path.exists(address):                                                                 # проверяем наличие папки чтобы перебирать позиции
            with open(address+'/'+'positions.txt','r') as file:                                     # берем файл с хешем позиций
                pos_data = file.readlines()                                                         # берем все хеши позиций
            good_hashes = []
            for line in pos_data:                                                                   # перебираем хеши
                pos_hash = line.replace('\n','')                                                    # нормальный вид файлу приводим
                try:
                    receipt = w3.eth.getTransactionReceipt(pos_hash)                                # берем "чек" по транзакции, можно сказать и логи, по простому - то, что нам ответил контракт на нашу транзу
                    if w3.toInt(receipt['logsBloom']) != 0:                                         # проверяем прошла ли транзакция
                        good_hashes.append(pos_hash)                                                # если прошла, добавляем её в список к прошедшим транзам
                    else:
                        pass
                except:
                    pass
                for hash in good_hashes:                                                            # перебираем хорошие хеши
                    receipt = w3.eth.getTransactionReceipt(hash)                                    # берем "чек" хорошей транзы (пояснение на 21 строке)
                    logs_data = receipt['logs'][0]['data']                                          # берем первые данные в "чеке", они представлены в hex формате
                    logs_data = logs_data[:80]                                                      # обрезаем до нужной части
                    logs_data = logs_data.replace('0','')                                           # убираем ненужные нули
                    
                    
                    pos_id = w3.toInt(hexstr='0'+logs_data)                                         # переводим hex --> int, что является айдишником позиции необходимым чтобы убрать позицию
                    fraction = w3.toWei('1','Ether')                                                # переводим 1 eth --> wei 
                    priceLimit = w3.toWei('10000000','Ether')                                       # переводим eth --> wei    
                    pre_txn = contracts.ovl_pr_contract.functions.unwind(                           # строим функцию
                        pos_id,                                                                     # айди позиции
                        fraction,                                                                   # бог знает, что, но всегда статичный
                        priceLimit,                                                                 # бог знает, что, но всегда статичный    
                    )
                    tx = pre_txn.buildTransaction({                                                 # строим транзу (пояснение в index.py)
                        'from': admin_account.address,
                        'nonce': w3.eth.getTransactionCount(admin_account.address),
                        'gasPrice': Web3.toWei(1+random.random(), 'gwei'),
                        })
                    signed_tx = w3.eth.account.signTransaction(tx, pvkey)                           # подписываем
                    emitted = w3.eth.sendRawTransaction(signed_tx.rawTransaction)                   # отправляем в блокчейн
                    time.sleep(8)