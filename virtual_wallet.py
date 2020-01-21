from decimal import Decimal, isdecimal
# 钱包数据代码,主要提供对wallet的一个标准正常普通的CURD接口
import walletRepo
# 交易数据代码,提供记录交易信息的接口
import transactionRepo
# 一个交易数据的模型
import transactionEntity


class VirtualWallet(object):
    def __init__(self, walletRepo):
        self.__walletId = walletRepo['walletId']
        self.__createTime = walletRepo['createTime']
        self.__balance = Decimal(walletRepo['balance'])

    def getBalance(self):
        return str(self.__balance)

    def credit(self, amount):
        if (Decimal(str(amount)) < Decimal(0)) or (not isdecimal(amount)):
            raise InvalidAmountException('错误的交易额输入')
        self.__balance += Decimal(str(amount))

    def debit(self, amount):
        if not isdecimal(amount):
            raise InvalidAmountException('错误的交易额输入')
        if Decimal(str(amount)) > self.__balance:
            raise InsufficientBalanceException('余额不足')
        self.__balance -= Decimal(str(amount))


class VirtualWalletServer(object):
    def __init__(self):
        self.__VirtualWalletRepo = walletRepo
        self.__TransactionRepo = transactionRepo
        return

    def getVirtualWallet(self, walletId):
        return VirtualWallet(self.__VirtualWalletRepo.getWalletEntity(walletId))

    def transfer(self, fromWalletId, toWalletId, amount):
        _fromWallet = self.getVirtualWallet(fromWalletId)
        _toWallet = self.getVirtualWallet(toWalletId)
        transaction = transactionEntity()
        transaction.setAmount(amount)
        transaction.setFromWaleetId(fromWalletId)
        transaction.setToWalletId(toWalletId)
        transaction.setStatus(transaction.TO_BE_EXECUTED)
        _transactionId = transactionRepo.saveTransaction(transaction.getTransaction())
        try:
            _fromWallet.debit(amount)
            _toWallet.debit(amount)
        except InsufficientBalanceException:
            # 余额不足代码
            transactionRepo.updateStatus(_transactionId, transaction.CLOSE)
        except:
            # 其他错误
            transactionRepo.updateStatus(_transactionId, transaction.FAILED)
        else:
            # 没有出现错误则更新余额
            walletRepo.updateBalance(fromWalletId, _fromWallet.getBalance())
            walletRepo.updateBalance(toWalletId, _toWallet.getBalance())
        finally:
            # 更改交易状态
            transactionRepo.updateStatus(_transactionId, transaction.SUCCESS)
        return
