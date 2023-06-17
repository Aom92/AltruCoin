
"""
    Utilizing our admin class to implement a simple command line interface client 
    for our Algorand Blockchain application - AltruCoin.

    The client will allow users to activate accounts for altrucoin, and perform transactions
    it provides simple authentication and authorization for users and managers.
    on the Algorand Blockchain.

    @Authors: Ricardo Peña Cuevas, Hugo Juárez Pérez, Armando Ponce Soriano, Kevin López González, Isaac López Aniceto.
    @Version: 1.0
    @Date: 16/06/2023
    
    *** To be improved: mnemonics should be sent encrypted and decrypted on the client side
"""

from adminCharity import admin
import json
import base64
import algosdk
from algosdk.v2client import algod
from algosdk import account, mnemonic, encoding
from algosdk.transaction import *
from algosdk import transaction
from algosdk import constants
import json
import base64

adminCharity = admin()

def transfer(addressUsuario, mnemonicUsuario):
    global adminCharity
    sk = adminCharity.getPrivateKey(mnemonicUsuario)

    addressReceiver = input("Ingresa la dirección a la que deseas transferir: ")
    amount = int(input("Ingresa el monto que deseas transferir: "))
    note = input("Concepto de la transferencia: ")
    adminCharity.transferAsset(addressUsuario,sk,addressReceiver,amount, note)

#Función de utilidad para imprimir la tenencia de activos para la cuenta y assetid
def print_asset_holding(algodclient, account, assetid):
    account_info = algodclient.account_info(account)
    idx = 0
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx = idx + 1
        if (scrutinized_asset['asset-id'] == assetid):
            print("Asset ID: {}".format(scrutinized_asset['asset-id']))
            print(json.dumps(scrutinized_asset, indent=4))
            break
        
def createAccount():

    # Generate a fresh private key and associated account address
    private_key, account_address = algosdk.account.generate_account()

    # Convert the private key into a mnemonic which is easier to use
    mnemonic = algosdk.mnemonic.from_private_key(private_key)

    print("Private key mnemonic: " + mnemonic)
    print("Account address: " + account_address)

def accountOpening(mnemonic):
    
    account_address = adminCharity.getAddress(mnemonic)

    adminCharity.optIn(str(account_address), str(mnemonic))

def userMenu(mnemonicUsr, addressUsuario):
    print(f"\n¡Bienvenido, {addressUsuario}!")
    
    while(True):
        print("==== USUARIO ====")
        print("1. Donativo / Transferencia")
        print("2. Consulta de balance")
        print("3. Cerrar", end='\n')

        opcion = input("Ingrese una opcion: ")
        opcion = int(opcion) if opcion.isdigit() else -1

        if opcion == 1:
            transfer(addressUsuario,mnemonicUsr)

        elif opcion == 2:
            adminCharity.getBalance(addressUsuario)
                
        elif opcion == 3:
            break
        else:
            print("Opcion invalida\n")



def managerMenu(mnemonicUsr, addressUsuario):
    global adminCharity
    
    print(f"\n¡Bienvenido, {addressUsuario}!")

    while(True):
        print("==== MANAGER ====")
        print("1. Transferir")
        print("2. Consulta de balance")
        print("3. Destruir asset")
        print("4. Actualizar asset")
        print("5. Congelar asset")
        print("6. Descongelar asset")
        print("7. Revocar asset")
        print("8. Cerrar", end='\n')
        
        opcion = input("Ingrese una opcion: ")
        opcion = int(opcion) if opcion.isdigit() else -1

        if opcion == 1:
            transfer(addressUsuario, mnemonicUsr)

        elif opcion == 2:
            adminCharity.getBalance(addressUsuario)

        elif opcion == 3:
            assetId = input("Ingrese el ID: ")
            adminCharity.destroyAsset(mnemonicUsr,assetId)
        
        elif opcion == 4:
            newManager = input("Ingrese el adress del nuevo manager: ")
            assetId = input("Ingrese el ID: ")
            adminCharity.updateAsset(mnemonicUsr, assetId, newManager)

        elif opcion == 5:
            address = input("Ingrese el adress a congelar: ")
            assetId = input("Ingrese el ID: ")
            adminCharity.freezeAsset(mnemonicUsr, address, assetId)

        elif opcion == 6:
            address = input("Ingrese el adress a descongelar: ")
            assetId = input("Ingrese el ID: ")
            adminCharity.unFreezeAsset(mnemonicUsr, address, assetId)

        elif opcion == 7:
            address = input("Ingrese el adress a revocar: ")
            amount = int(input("Ingrese el monto a revocar: "))
            assetId = input("Ingrese el ID: ")
            adminCharity.revokeAsset(mnemonicUsr, address, amount, assetId )
        
        elif opcion == 8:
                break
        
        else:
            print("Opcion invalida\n")

def adminMenu(mnemonicUsr, addressUsuario):
    global adminCharity
    
    print(f"\n¡Bienvenido, {addressUsuario}!")

    while(True):
        print("==== ADMINISTRADOR ====")
        print("1. Transferir")
        print("2. Consulta de balance")
        print("3. Crear asset")
        print("4. Cerrar", end='\n')
        
        opcion = input("Ingrese una opcion: ")
        opcion = int(opcion) if opcion.isdigit() else -1

        if opcion == 1:
            transfer(addressUsuario, mnemonicUsr)

        elif opcion == 2:
            adminCharity.getBalance(addressUsuario)

        elif opcion == 3:
            asset_name = input("Ingresa el nombre del asset:")
            unit_name = asset_name.upper()
            adminCharity.createAsset(unit_name, asset_name, mnemonicUsr)
          
        elif opcion == 4:
                break
        else:
            print("Opcion invalida\n")
             


def login():
    global adminCharity
    mnemonicUsr = input("Ingresa tu Mnemonic: ")

    addressUsuario = adminCharity.getAddress(mnemonicUsr)
    
    if addressUsuario == adminCharity.accounts['admin']:
        adminMenu(mnemonicUsr, addressUsuario)

    elif addressUsuario == adminCharity.accounts['manager']:
        managerMenu(mnemonicUsr, addressUsuario)

    else:
        userMenu(mnemonicUsr, addressUsuario)



def main():
    while(True):
        print("\nBienvenido al Cliente de AltruCoin")
        print("==== MENÚ PRINCIPAL ====")
        print("1. Crear cuenta")
        print("2. Ingresar")
        print("3. Activar AltruC")
        print("4. Salir", end='\n')
        
        opcion = input("Ingrese una opcion: ")
        opcion = int(opcion) if opcion.isdigit() else -1

        if opcion == 1:
            createAccount()
        elif opcion == 2:
            login()
        elif opcion == 3:
            mnemonicUsr = input("Ingresa tu Mnemonic: ")
            accountOpening(mnemonicUsr)
        elif opcion == 4:
            break
        else:
            print("Opcion invalida\n")
            



if __name__ == '__main__': 
    main()