from web3 import Web3, HTTPProvider # сама библа веб3
import time # необходимо для задержки
import contracts # импортируем файлик с abi контракта (пояснение в contracts.py)
import random # необходим для рандомной комсы (иногда ругается что одинаковые транзакции с одинаковой комсой)
import os # работа с папками

pvkey = '03778f2f9afe551354ae9f9b002ccd37c238b91022abe57aa6659b8e55fbb817' # приватный ключ (я не доделал обработку его из файла, потому-что проект кончился и я не сделал получение тест токенов)
w3 = Web3(Web3.HTTPProvider("https://kovan.infura.io/v3/3f1bd555eaa14207af96828688cb7a03")) # подключаемся к ноде которую предоставляет infura, бесплатно
account = w3.eth.account.privateKeyToAccount(pvkey) # подключаем приватки, в ином случае создаем аккаунт .create

def approve(): # функция для аппрува трат на токен в отношение к контракту
    pre_txn = contracts.ovl_token_contract.functions.approve(w3.toChecksumAddress('0x7de9bec6702ec18955f822edcc85c88ec9bd99f6'),w3.toWei('1234567891011121314','gwei')) # формируем транзакцию, после functions.*, где * - функция контракта, в скобках параметры запроса
    tx = pre_txn.buildTransaction({                             # строим транзакцию, указывая от кого, указываем nonce - кол-во транзакций на аккаунте, и цену газа
    'from': account.address,
    'nonce': w3.eth.getTransactionCount(account.address),           # тут может возникнуть проблема, что вы отправите транзакцию с неправильным значением, потому-что прошлая транзакция еще обрабатывается
    'gasPrice': Web3.toWei('3', 'gwei'), # тут переводим eth --> gwei
    })
    signed_tx = w3.eth.account.signTransaction(tx, account.key) # подписываем транзакцию
    emitted = w3.eth.sendRawTransaction(signed_tx.rawTransaction) # отправляем транзакцию
def deposit_on_short(): # функция для депозита на шорт
    isLong = False                          # указываем значение для контракта
    collateral = w3.toWei('0.001','Ether')  # указываем значение для контракта
    leverage = w3.toWei('1','Ether')        # указываем значение для контракта
    price_limit = w3.toWei('16','Ether')    # указываем значение для контракта
    pre_txn = contracts.ovl_pr_contract.functions.build( # строим транзу
        collateral, # сколько олв закидывать в пул | все эти данные берутся с отправленной/расшифрованной(неотправленной) транзакции
        leverage, # плечо фьча
        isLong, # long/short
        price_limit #цена токена типо на площадке???????
    )
    tx = pre_txn.buildTransaction({ # указываем от кого, газ, и нонс
        'from': account.address,
        'nonce': w3.eth.getTransactionCount(account.address),
        'gasPrice': Web3.toWei(2+random.random(), 'gwei'),
        })
    signed_tx = w3.eth.account.signTransaction(tx, account.key) # подписываем
    emitted = w3.eth.sendRawTransaction(signed_tx.rawTransaction) # отправляем в блокчейн
    return emitted
try:
    os.mkdir(account.address) # создаем дирректорию с аккаунтов
except:
    pass
for i in range(5):
    try:
        txnhash = deposit_on_short() # отправляем 5 транзакций для установки позиции на шорт
        txnHashHex = txnhash.hex() # расшифровываем и получаем хеш/ссылку на транзакцию
        with open(account.address+'/'+'positions.txt','a') as file:
            file.write(txnHashHex+'\n') # закидываем в папку все хеши с позициями
        with open(account.address+'/'+'pvkey.txt','a') as file:
            file.write(pvkey) # закидываем в папку файл с приватключом
        time.sleep(3)
    except:
        print('Транзакция не прошла')
