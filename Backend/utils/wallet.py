from web3 import Web3, exceptions

def create_wallet(w3):
    """
    Crea una nueva wallet Ethereum y devuelve su dirección y clave privada.
    """
    account = w3.eth.account.create()
    return {
        "address": account.address,
        "private_key": account._private_key.hex()
    }


def send_transaction(from_private_key, to_address, amount, w3):
    """
    Envía una transacción de Ethereum y devuelve el hash de la transacción.
    
    Parámetros:
        from_private_key (str): Clave privada del remitente.
        to_address (str): Dirección del destinatario.
        amount (float): Cantidad de ether a enviar.
        w3 (Web3): Instancia de Web3.
    """
    try:
        # Crear una instancia de la cuenta con la clave privada
        account = w3.eth.account.from_key(from_private_key)
        
        # Obtener el nonce de la cuenta
        nonce = w3.eth.get_transaction_count(account.address)
        tx = {
            'nonce': nonce,
            'to': to_address,
            'value': w3.to_wei(amount, 'ether'),
            'gasPrice': w3.eth.gas_price
        }
        # Estimamos el gas necesario para la transacción
        tx['gas'] = w3.eth.estimate_gas({
            'from': account.address,
            'to': to_address,
            'value': tx['value'],
            'data': b''
        })

        # Firmamos la transacción
        signed_tx = account.sign_transaction(tx)

        # Enviamos la transacción
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        # Devolvemos el hash de la transacción
        return w3.to_hex(tx_hash)
    except exceptions.Web3Exception as e:
        raise Exception(f"Error al enviar la transacción: {str(e)}")

def get_balance(address,w3):
    """
    Consulta el saldo total de una dirección Ethereum y devuelve el saldo en ether.
    """
    if not w3.is_address(address):
        raise ValueError("Invalid Ethereum address")
    balance = w3.eth.get_balance(address)
    return w3.from_wei(balance, 'ether')

# Funcion para obtener el saldo de un token ERC-20 (PENDIENTE DE HACER BIEN Y CONFIGURAR EL ENDPOINT)

def get_token_balance(token_address, wallet_address, w3):
    """
    Consulta el saldo de un token ERC-20 para una dirección específica.

    Parámetros:
        token_address (str): La dirección del contrato del token ERC-20.
        wallet_address (str): La dirección de la cartera cuyo saldo de token se está consultando.
        w3 (Web3): Instancia de Web3.
    """
    # ABI mínimo requerido para consultar el saldo de un token ERC-20
    token_abi = [
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function",
        }
    ]
    
    if not w3.is_address(wallet_address) or not w3.is_address(token_address):
        raise ValueError("Invalid Ethereum or token address")
    
    # Crea el contrato en web3
    token_contract = w3.eth.contract(address=token_address, abi=token_abi)
    
    # Consulta el saldo
    balance = token_contract.functions.balanceOf(wallet_address).call()
    
    # Convierte el saldo a un formato legible (si el token tiene 18 decimales)
    return balance / 10**18

# Ejemplo de uso
# w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/your_infura_project_id'))
# print(get_token_balance('token_contract_address_here', 'your_wallet_address_here', w3))