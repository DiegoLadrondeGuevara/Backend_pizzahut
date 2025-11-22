import json
import boto3
import os

# Lee la tabla de conexiones de WebSocket de las variables de entorno
DYNAMODB_TABLE_CONEXIONES = os.environ.get('DYNAMODB_TABLE_CONEXIONES', 'ConexionesTable')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE_CONEXIONES)

def lambda_handler(event, context):
    cors_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'  # Permitir acceso desde cualquier origen
    }

    try:
        connection_id = event['requestContext']['connectionId']
        user_id = event['requestContext']['authorizer']['user_id']  # Asegúrate de pasar el user_id en la autorización
        
        # Guardar conexión del restaurante en DynamoDB
        table.put_item(
            Item={
                'connection_id': connection_id,
                'user_id': user_id,
                'timestamp': event['requestContext']['time']
            }
        )
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'message': 'Conexión exitosa'})
        }
    
    except Exception as e:
        print(f"Error al guardar conexión: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Error interno del servidor', 'details': str(e)})
        }
