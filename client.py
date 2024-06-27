import requests
import json

headers = {'Content-Type': 'application/json'}
body = {
    'client_name': "Arthur",
    'product_id': 1,
    'quantity': 1,
    'amount': 1000,
    'address': 'Rua Sete de Setembro 100, Curitiba, PR'
}

body_json = json.dumps(body)
url = 'http://localhost:6000/create_order'
response = requests.post(url, headers=headers, data=body_json)

if response.status_code == 200:
    print('Ordem criada com sucesso!')
    print('Resposta do servidor: ID do Pedido:', response.json().get('order_id'), " Status do pedido: ", response.json().get('status'))
else:
    print('Erro ao criar a ordem. Código de status:', response.status_code)
    print('Detalhes do erro:', response.json().get('error'))