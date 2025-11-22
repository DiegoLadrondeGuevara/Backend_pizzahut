import json
import boto3
import uuid
from datetime import datetime
import os

# Lee el nombre de la tabla de las variables de entorno
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_LOGS', 'LogsTable')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

def lambda_handler(event, context):
    cors_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'  # Habilitado por el API Gateway, pero se incluye por seguridad
    }
    
    try:
        # Parse del body
        body = json.loads(event['body'])
        
        user_id = body.get('user_id')
        accion = body.get('accion')
        dispositivo = body.get('dispositivo', '')
        ip = body.get('ip', '')
        
        if not user_id or not accion:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Faltan datos obligatorios (user_id, accion).'})
            }
        
        log_id = str(uuid.uuid4())
        horario = datetime.utcnow().isoformat()
        
        # Crear un nuevo log en DynamoDB
        table.put_item(
            Item={
                'log_id': log_id,
                'user_id': user_id,
                'accion': accion,
                'horario': horario,
                'dispositivo': dispositivo,
                'ip': ip
            }
        )
        
        return {
            'statusCode': 201,
            'headers': cors_headers,
            'body': json.dumps({
                'message': 'Log creado exitosamente.',
                'log_id': log_id
            })
        }
        
    except Exception as e:
        print(f"Error en createLog: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({
                'error': 'Error interno del servidor',
                'details': str(e)
            })
        }
