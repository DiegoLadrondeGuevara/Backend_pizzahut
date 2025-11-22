import json
import boto3
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
        pedido_id = event['pathParameters'].get('pedido_id')
        body = json.loads(event['body'])
        
        nuevo_estado = body.get('estado')
        
        if not pedido_id or not nuevo_estado:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Faltan datos obligatorios (pedido_id, estado).'})
            }
        
        # Obtener el pedido existente
        response = table.get_item(Key={'pedido_id': pedido_id, 'tenant_id': body.get('tenant_id')})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Pedido no encontrado.'})
            }
        
        pedido = response['Item']
        
        # Actualizar el estado del pedido
        table.update_item(
            Key={'pedido_id': pedido_id, 'tenant_id': pedido['tenant_id']},
            UpdateExpression='SET estado = :estado',
            ExpressionAttributeValues={':estado': nuevo_estado}
        )
        
        # Enviar mensaje a los clientes conectados sobre el cambio de estado
        message = {
            'type': 'estado_actualizado',
            'pedido': {
                'pedido_id': pedido_id,
                'estado': nuevo_estado
            }
        }
        
        # Llamada para enviar el mensaje a través del WebSocket
        try:
            response = apigatewaymanagementapi.post_to_connection(
                ConnectionId=pedido['user_id'],  # Esto debe ser un ID de conexión WebSocket, que se obtiene cuando se conecta
                Data=json.dumps(message)
            )
        except Exception as e:
            print(f"Error enviando mensaje a WebSocket: {str(e)}")
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'message': 'Estado del pedido actualizado.'})
        }
        
    except Exception as e:
        print(f"Error en updateEstadoPedido: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({
                'error': 'Error interno del servidor',
                'details': str(e)
            })
        }
