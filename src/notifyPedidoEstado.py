import json
import boto3
import os

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
        user_id = body.get('user_id')
        estado = body.get('estado')
        pedido_id = body.get('pedido_id')

        if not user_id or not estado or not pedido_id:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Faltan datos necesarios (user_id, estado, pedido_id).'})
            }

        # Consultar la conexión activa para el user_id
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['DYNAMODB_TABLE_CONEXIONES'])
        
        response = table.query(
            IndexName='user_id-index',  # Usamos un GSI si lo tienes configurado para hacer la consulta más eficiente
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        
        if 'Items' not in response or len(response['Items']) == 0:
            return {
                'statusCode': 404,
                'headers': cors_headers,
                'body': json.dumps({'error': 'No se encontraron conexiones activas para este usuario.'})
            }

        # Enviar notificación sobre el cambio de estado del pedido a WebSocket
        connection_id = response['Items'][0]['connection_id']
        message = {
            'type': 'estado_actualizado',
            'pedido_id': pedido_id,
            'estado': estado
        }

        # Enviar el mensaje a través de WebSocket
        apigatewaymanagementapi.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(message)
        )
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'message': 'Notificación enviada exitosamente.'})
        }

    except Exception as e:
        print(f"Error al enviar notificación: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({
                'error': 'Error interno del servidor',
                'details': str(e)
            })
        }
