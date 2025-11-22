import json
import boto3
import os

# Inicializamos el cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')
# Tabla de conexiones WebSocket
CONNECTIONS_TABLE = os.environ.get('DYNAMODB_TABLE_CONNECTIONS')

# Referencia a la tabla DynamoDB que almacena las conexiones activas de WebSocket
connections_table = dynamodb.Table(CONNECTIONS_TABLE)

def lambda_handler(event, context):
    # Definición de encabezados CORS
    cors_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'  # Asegura que la API es accesible desde cualquier dominio
    }
    
    # Obtenemos el 'connectionId' de los detalles del evento
    connection_id = event['requestContext']['connectionId']
    
    try:
        # Eliminar el registro de la conexión activa de DynamoDB
        # Esto es importante para eliminar las conexiones "muertas" que ya no están activas
        response = connections_table.delete_item(
            Key={
                'connection_id': connection_id  # El 'connection_id' es la clave primaria
            }
        )
        
        # Loguear que la desconexión se completó (puedes agregar más información si es necesario)
        print(f"Conexión {connection_id} desconectada exitosamente.")
        
        # Responder con un mensaje de éxito
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'message': f"Conexión {connection_id} desconectada exitosamente."
            })
        }
    
    except Exception as e:
        print(f"Error al desconectar la conexión {connection_id}: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({
                'error': f"Error interno al desconectar la conexión {connection_id}.",
                'details': str(e)
            })
        }
