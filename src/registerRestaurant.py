import json
import boto3
import hashlib
import uuid
from datetime import datetime
import secrets
import os

# Lee el nombre de la tabla de DynamoDB de las variables de entorno
DYNAMODB_TABLE_RESTAURANTES = os.environ.get('DYNAMODB_TABLE_RESTAURANTES', 'RestaurantesTable')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE_RESTAURANTES)

def hash_password(password):
    """Hashea la contraseña usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_simple_token():
    """Genera un token simple sin dependencias externas"""
    return secrets.token_urlsafe(32)

def lambda_handler(event, context):
    cors_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'  # Permitir acceso desde cualquier origen
    }

    try:
        # Parseo del body
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})

        email = body.get('email')
        nombre_restaurante = body.get('nombre_restaurante')
        password = body.get('password')
        direccion = body.get('direccion')
        distrito = body.get('distrito')
        departamento = body.get('departamento')
        telefono = body.get('telefono')

        # Validación de campos requeridos
        if not email or not nombre_restaurante or not password or not direccion or not distrito or not departamento or not telefono:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Todos los campos son requeridos'})
            }

        # Verificar si el restaurante ya está registrado usando 'email' directamente
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('email').eq(email)
        )

        if response['Items']:  # Si hay elementos en la respuesta, significa que el restaurante ya está registrado
            return {
                'statusCode': 409,
                'headers': cors_headers,
                'body': json.dumps({'error': 'El restaurante ya está registrado'})
            }

        # Crear un nuevo restaurante
        restaurant_id = str(uuid.uuid4())  # Generamos un ID único para el restaurante
        hashed_password = hash_password(password)  # Hasheamos la contraseña
        token = generate_simple_token()  # Generamos un token único

        # Guardar el restaurante en la tabla de DynamoDB
        table.put_item(
            Item={
                'restaurant_id': restaurant_id,  # Usamos 'restaurant_id' como clave primaria
                'email': email,
                'nombre_restaurante': nombre_restaurante,
                'direccion': direccion,
                'distrito': distrito,
                'departamento': departamento,
                'telefono': telefono,
                'password': hashed_password,
                'token': token,
                'created_at': datetime.utcnow().isoformat()
            }
        )

        # Responder con el éxito de la operación
        return {
            'statusCode': 201,
            'headers': cors_headers,
            'body': json.dumps({
                'message': 'Restaurante registrado exitosamente',
                'token': token,
                'restaurant': {
                    'restaurant_id': restaurant_id,
                    'email': email,
                    'nombre_restaurante': nombre_restaurante
                }
            })
        }

    except Exception as e:
        print(f"Error en Registro: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Error interno del servidor', 'details': str(e)})
        }
