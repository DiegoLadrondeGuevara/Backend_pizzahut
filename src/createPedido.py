import json
import boto3
import uuid
from datetime import datetime
import os

# Lee el nombre de la tabla de las variables de entorno
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_PEDIDOS', 'PedidosTable')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

# Servicio de API Gateway para enviar mensajes a través de WebSocket
apigatewaymanagementapi = boto3.client('apigatewaymanagementapi', endpoint_url=os.environ['WEBSOCKET_API_ENDPOINT'])

def lambda_handler(event, context):
    cors_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'  # Habilitado por el API Gateway, pero se incluye por seguridad
    }
    
    try:
        # Parse del body
        body = json.loads(event['body'])
        
        tenant_id = body.get('tenant_id')  # Restaurante (tenant)
        user_id = body.get('user_id')  # Cliente que hace el pedido
        productos = body.get('productos')
        
        if not tenant_id or not user_id or not productos:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Faltan datos obligatorios (tenant_id, user_id, productos).'})
            }
        
        pedido_id = str(uuid.uuid4())
        fecha_pedido = datetime.utcnow().isoformat()
        total = sum([producto['cantidad'] * producto['precio'] for producto in productos])
        
        # Crear un nuevo pedido en DynamoDB
        table.put_item(
            Item={
                'tenant_id': tenant_id,
                'pedido_id': pedido_id,
                'user_id': user_id,
                'productos': productos,
                'total': total,
                'estado': 'PENDIENTE',
                'fecha_pedido': fecha_pedido
            }
        )
        
        # Enviar mensaje a los clientes conectados sobre el nuevo pedido
        message = {
            'type': 'nuevo_pedido',
            'pedido': {
                'pedido_id': pedido_id,
                'user_id': user_id,
                'total': total,
                'estado': 'PENDIENTE',
                'fecha_pedido': fecha_pedido
            }
        }
        
        # Llamada para enviar el mensaje a través del WebSocket
        try:
            # Aquí asumimos que los clientes conectados a WebSocket se identifican por el `user_id`
            response = apigatewaymanagementapi.post_to_connection(
                ConnectionId=user_id,  # Esto debe ser un ID de conexión WebSocket, se obtiene del WebSocket
                Data=json.dumps(message)
            )
        except Exception as e:
            print(f"Error enviando mensaje a WebSocket: {str(e)}")
        
        return {
            'statusCode': 201,
            'headers': cors_headers,
            'body': json.dumps({
                'message': 'Pedido creado exitosamente.',
                'pedido_id': pedido_id
            })
        }
        
    except Exception as e:
        print(f"Error en createPedido: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({
                'error': 'Error interno del servidor',
                'details': str(e)
            })
        }
