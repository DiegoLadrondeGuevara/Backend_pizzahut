import json
import boto3
from datetime import datetime
import os

# Inicializa DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE_ESTADOS'))

def lambda_handler(event, context):
    # Parámetros de la solicitud
    pedido_id = event['pathParameters']['pedido_id']

    # Consulta el estado del pedido en la base de datos
    try:
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('pedido_id').eq(pedido_id),
            ScanIndexForward=False,  # Orden descendente por timestamp
            Limit=1  # Obtener solo el último estado
        )

        # Si encontramos un estado, lo devolvemos
        if response['Items']:
            return {
                'statusCode': 200,
                'body': json.dumps(response['Items'][0])
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Pedido no encontrado'})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error interno del servidor', 'details': str(e)})
        }
