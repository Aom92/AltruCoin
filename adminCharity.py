"""
    Implementation for the Algorand SDK.
    This class manages the asset functions.
    It allows to create, modify, transfer, freeze, unfreeze, revoke and destroy an asset.
    It also allows to get the balance of an account and the asset holding of an account.
    
    *API Keys and addresses are not included for security reasons.

    @Authors: Ricardo Peña Cuevas, Hugo Juárez Pérez, Armando Ponce Soriano, Kevin López González, Isaac López Aniceto.
    @Version: 1.0
    @Date: 16/06/2023
"""

import json
import base64
from algosdk.v2client import algod
from algosdk import account, mnemonic, encoding
from algosdk.transaction import *

API_KEY = "<TYPE YOUR API KEY>"
MANAGER_ADDRESS = "<TYPE YOUR MANAGER ACCOUNT ADDRESS>"
ADMIN_ADDRESS = "<TYPE YOUR ADMIN ACCOUNT ADDRESS>"

class admin:
    """
        Class that manages the asset functions.
    """
    def __init__(self, admin=None, manager=None):
        
        self.algod_client = algod.AlgodClient(
            algod_token="",
            algod_address="https://testnet-algorand.api.purestake.io/ps2",
            headers={"X-API-Key": API_KEY}
        )
        
        self.asset_id = "237848969"

        self.accounts = {
            'manager': MANAGER_ADDRESS,
            'admin': ADMIN_ADDRESS,
        }

    def getBalance(self, address):
        account_info = self.algod_client.account_info(address)
        print("Account balance: {} microAlgos".format(account_info.get('amount')) + "\n")
        self.printAssetHolding(address, self.asset_id)
    
    def getPrivateKey(self, mnemo):
        return "{}".format(mnemonic.to_private_key(mnemo))
    
    def getAddress(self, mnemo):
        return account.address_from_private_key(self.getPrivateKey(mnemo))

    def printInfoAsset(self, account, assetid):
        """
            Auxiliary functions that prints the created asset for the account and it's asset id.
            
            Args:
                account (str): Account that contains the created asset.
                assetid (int): ID of the asset to be printed. 
        """
        account_info = self.algod_client.account_info(account)
        idx = 0#;
        for my_account_info in account_info['created-assets']:
            scrutinized_asset = account_info['created-assets'][idx]
            idx = idx + 1
            if (scrutinized_asset['index'] == assetid):
                print("Asset ID: {}".format(scrutinized_asset['index']))
                print(json.dumps(my_account_info['params'], indent=4))
                break


    def printAssetHolding(self, account, assetid):
        """
            Auxiliary function that prints the asset holded by and accounts and it's assetid
            
            Args:
                account (str): Account that holds the assets specified in <assetid>. 
                assetid (int): ID of the asset to be printed.  
        """
        account_info = self.algod_client.account_info(account)
        idx = 0
        for my_account_info in account_info['assets']:
            scrutinized_asset = my_account_info
            idx = idx + 1
            if (scrutinized_asset['asset-id'] == int(assetid)):
                print("Balance de AltruCoins: {}".format(scrutinized_asset['amount']))
                print(json.dumps(scrutinized_asset, indent=4))
                break


    def createAsset(self, unit_name, asset_name, mnemoAdmin):
        """
            Method to create an asset.
    
            Args:
                unit_name (str): Unit name that will be assigned.
                asset_name (str): Asset name that will be assigne.
                mnemoAdmin (str): Admin mnemonic private key.
        """
        params = self.algod_client.suggested_params()
        params.fee = 1000
        params.flat_fee = True

        txn = AssetConfigTxn(
            sender=self.accounts['admin'],
            sp=params,
            total=10000,
            default_frozen=False,
            unit_name=unit_name, 
            asset_name=asset_name,
            manager=self.accounts['manager'],
            reserve=self.accounts['manager'],
            freeze=self.accounts['manager'],
            clawback=self.accounts['manager'],
            url="https://i.imgur.com/F2AwlB2.png",
            decimals=0)
        
        sk = self.getPrivateKey(mnemoAdmin)
        stxn = txn.sign("{}".format(sk))

        try:
            txid = self.algod_client.send_transaction(stxn)
            print("Signed transaction with txID: {}".format(txid))
            confirmed_txn = wait_for_confirmation(self.algod_client, txid, 4)
            print("TXID: ", txid)
            print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))
            print("Transaction information: {}".format(json.dumps(confirmed_txn, indent=4)))
        
        except Exception as err:
            print("Error: ", err)
            
        try:
            ptx = self.algod_client.pending_transaction_info(txid)
            self.asset_id = ptx["asset-index"]
            self.printInfoAsset(self.accounts['admin'], self.asset_id)
            self.printAssetHolding(self.accounts['admin'], self.asset_id)
        
        except Exception as e:
            print("Error:", e)


    def updateAsset(self, mnemoManager, assetId, newManager):
        """
            Method to modify an asset.

            Args:
                mnemoManager (str): Manager mnemonic.
                assetId (str): Asset id to update.
                newManager (str): New manager address.
        """
        params = self.algod_client.suggested_params()
        
        txn = AssetConfigTxn(
            sender= self.accounts['manager'],
            sp= params,
            index= assetId,
            manager= newManager,
            reserve= newManager,
            freeze= newManager,
            clawback= newManager)
        
        sk = self.getPrivateKey(mnemoManager)
        stxn = txn.sign(sk)

        try:
            txid = self.algod_client.send_transaction(stxn)
            print("Signed transaction with txID: {}".format(txid))
            confirmed_txn = wait_for_confirmation(self.algod_client, txid, 4)
            print("TXID: ", txid)
            print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))

        except Exception as err:
            print("Error:", err)


    def optIn(self, address, mnemo):
        """
            Method that allows (Opts in) an asset.
            
            Params:
                address (str): Address of who will be Opted In.
                mnemo (str): Account Mnemonic.
        """
        params = self.algod_client.suggested_params()

        account_info = self.algod_client.account_info(address)
        holding = None
        idx = 0
        for my_account_info in account_info['assets']:
            scrutinized_asset = account_info['assets'][idx]
            idx = idx + 1
            if (scrutinized_asset['asset-id'] == self.asset_id):
                holding = True
                break

        if not holding:

            txn = AssetTransferTxn(
                sender=address,
                sp=params,
                receiver=address,
                amt=0,
                index=self.asset_id)
            
            sk = self.getPrivateKey(mnemo)
            stxn = txn.sign(sk)

            try:
                txid = self.algod_client.send_transaction(stxn)
                print("Signed transaction with txID: {}".format(txid))
                confirmed_txn = wait_for_confirmation(self.algod_client, txid, 4)
                print("TXID: ", txid)
                print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))

            except Exception as err:
                print(err)
            self.printAssetHolding(address, self.asset_id)


    def transferAsset(self, sender_address, sender_sk, receiver_address, amount, note):
        """
            Method to transfer an asset.

            Params:
                sender_address (str): Sender address.
                sender_sk (str): Sender private key.
                receiver_address (str): Receiver address.
                amount (int): Mounto to transfer.
        """
        params = self.algod_client.suggested_params()

        txn = AssetTransferTxn(
            sender=sender_address,
            sp=params,
            receiver=receiver_address,
            amt=amount,
            index=self.asset_id,
            note = note)
        stxn = txn.sign(sender_sk)

        try:
            txid = self.algod_client.send_transaction(stxn)
            print("Signed transaction with txID: {}".format(txid))
            confirmed_txn = wait_for_confirmation(self.algod_client, txid, 4)
            print("TXID: ", txid)
            print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))

        except Exception as err:
            print(err)

    def freezeAsset(self, mnemoManager, address, assetId):
        """
            Method that freezes an Account's Asset.

            Args:
                mnemoManager (str): Manager mnemonic.
                address (str): Addres to revoke.
                assetId (str): Asset id to revoke.
        """
        params = self.algod_client.suggested_params()

        txn = AssetFreezeTxn(
            sender=self.accounts['manager'],
            sp=params,
            index=assetId,
            target=address,
            new_freeze_state=True
        )
        sk = self.getPrivateKey(mnemoManager)
        stxn = txn.sign(sk)

        try:
            txid = self.algod_client.send_transaction(stxn)
            print("Signed transaction with txID: {}".format(txid))
            confirmed_txn = wait_for_confirmation(self.algod_client, txid, 4)
            print("TXID: ", txid)
            print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))
        except Exception as err:
            print(err)

        self.printAssetHolding(address, self.asset_id)

    def unFreezeAsset(self, mnemoManager, address, assetId):
        """
            Method that unfreezes an Account's Asset

            Args:
                mnemoManager (str): Manager mnemonic.
                address (str): Addres to revoke.
                assetId (str): Asset id to revoke.
        """
        params = self.algod_client.suggested_params()

        txn = AssetFreezeTxn(
            sender=self.accounts['manager'],
            sp=params,
            index=assetId,
            target=address,
            new_freeze_state=False
        )
        sk = self.getPrivateKey(mnemoManager)
        stxn = txn.sign(sk)

        try:
            txid = self.algod_client.send_transaction(stxn)
            print("Signed transaction with txID: {}".format(txid))
            confirmed_txn = wait_for_confirmation(self.algod_client, txid, 4)
            print("TXID: ", txid)
            print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))
        except Exception as err:
            print(err)

        self.printAssetHolding(address, self.asset_id)


    def revokeAsset(self, mnemoManager, address, amt, assetId):
        """
            Method to revoke an asset.

            Args:
                mnemoManager (str): Manager mnemonic.
                address (str): Receiver address to revoke.
                amt (int): Amount to revoke.
                assetId (str): Asset id to revoke.
        """
        params = self.algod_client.suggested_params()

        txn = AssetTransferTxn(
            sender=self.accounts['manager'],
            sp=params,
            receiver=self.accounts['admin'],
            amt=amt,
            index=assetId,
            revocation_target=address
        )
        sk = self.getPrivateKey(mnemoManager)
        stxn = txn.sign(sk)

        try:
            txid = self.algod_client.send_transaction(stxn)
            print("Signed transaction with txID: {}".format(txid))
            confirmed_txn = wait_for_confirmation(self.algod_client, txid, 4)
            print("TXID: ", txid)
            print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))
        except Exception as err:
            print(err)


    def destroyAsset(self, mnemoManager, assetId):
        """
            Method to destroy an asset.
            
            Args:
                mnemoManager (str): Manager mnemonic.
                assetId (str): Asset id to destroy.
        """
        params = self.algod_client.suggested_params()

        txn = AssetConfigTxn(
            sender=self.accounts['manager'],
            sp=params,
            index=assetId,
            strict_empty_address_check=False
            )

        sk = self.getPrivateKey(mnemoManager)
        stxn = txn.sign(sk)

        try:
            txid = self.algod_client.send_transaction(stxn)
            print("Signed transaction with txID: {}".format(txid))
            confirmed_txn = wait_for_confirmation(self.algod_client, txid, 4)
            print("TXID: ", txid)
            print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))
        except Exception as err:
            print(err)
        try:
            self.printAssetHolding(self.accounts['manager'], assetId)
            self.printInfoAsset(self.accounts['manager'], assetId)

        except Exception as e:
            print(e)
