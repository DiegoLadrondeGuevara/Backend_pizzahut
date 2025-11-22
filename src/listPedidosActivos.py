import json
import boto3
import os

# Lee el nombre de la tabla de las variables de entorno
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_PEDIDOS', 'PedidosTable')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

def lambda_handler(event, context):
    cors_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'  # Habilitado por el API Gateway, pero se incluye por seguridad
    }

    try:
        # Parsear el user_id de la solicitud
        body = json.loads(event['body'])
        user_id = body.get('user_id')

        if not user_id:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'El user_id es requerido.'})
            }

        # Consultar los pedidos activos del usuario
        response = table.query(
            IndexName='user_id-index',  # GSI que debe existir para consultar por user_id
            KeyConditionExpression='user_id = :user_id',
            ExpressionAttributeValues={':user_id': user_id},
            FilterExpression='estado IN (:pendiente, :en_preparacion)',  # Filtrar por estado
            ExpressionAttributeValues={':pendiente': 'PENDIENTE', ':en_preparacion': 'EN_PREPARACION'}
        )

        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'message': 'Pedidos activos obtenidos correctamente.',
                'pedidos': response.get('Items', [])
            })
        }
        
    except Exception as e:
        print(f"Error al listar pedidos activos: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({
                'error': 'Error interno del servidor',
                'details': str(e)
            })
        }
