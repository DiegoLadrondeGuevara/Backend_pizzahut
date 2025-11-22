import json
import boto3
import os
from datetime import datetime

# Inicializamos el cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')

# Obtener la tabla de conexiones de WebSocket desde las variables de entorno
CONNECTIONS_TABLE = os.environ.get('DYNAMODB_TABLE_CONNECTIONS')

# Referencia a la tabla DynamoDB para guardar las conexiones
connections_table = dynamodb.Table(CONNECTIONS_TABLE)

def lambda_handler(event, context):
    # Definimos los encabezados para las respuestas CORS
    cors_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'  # Permite el acceso desde cualquier origen
    }

    # Obtenemos el 'connectionId' de la conexión WebSocket
    connection_id = event['requestContext']['connectionId']
    
    # Intentamos obtener el `user_id` de los parámetros de la query string (puede venir de un JWT o parámetros de registro/login)
    user_id = event.get('queryStringParameters', {}).get('user_id')  # El `user_id` puede venir del login o registro
    
    # Validación: Si no tenemos `user_id`, respondemos con un error
    if not user_id:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps({
                'error': 'El usuario no está autenticado. Por favor inicie sesión o registrese.'
            })
        }

    try:
        # Almacenamos la conexión en la tabla de DynamoDB, asociando el `connection_id` con el `user_id`
        response = connections_table.put_item(
            Item={
                'connection_id': connection_id,  # Clave primaria de la tabla
                'user_id': user_id,               # Asociamos al usuario logueado o registrado
                'timestamp': str(datetime.utcnow()),  # Timestamp de la conexión
            }
        )

        # Log para registrar la conexión
        print(f"Conexión establecida para el usuario {user_id} con connectionId {connection_id}.")

        # Respuesta exitosa
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'message': f"Conexión {connection_id} establecida exitosamente para el usuario {user_id}."
            })
        }
    
    except Exception as e:
        # Error en caso de que algo falle al guardar la conexión
        print(f"Error al manejar la conexión de WebSocket: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({
                'error': 'Hubo un error al manejar la conexión.',
                'details': str(e)
            })
        }
