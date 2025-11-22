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
        
        # Eliminar la conexión de la tabla cuando el restaurante se desconecta
        table.delete_item(Key={'connection_id': connection_id})
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({'message': 'Desconexión exitosa'})
        }
    
    except Exception as e:
        print(f"Error al eliminar la conexión: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Error interno del servidor', 'details': str(e)})
        }
