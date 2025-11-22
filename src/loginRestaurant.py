import json
import boto3
import hashlib
import os

# Lee el nombre de la tabla de DynamoDB de las variables de entorno
DYNAMODB_TABLE_RESTAURANTES = os.environ.get('DYNAMODB_TABLE_RESTAURANTES', 'RestaurantesTable')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(DYNAMODB_TABLE_RESTAURANTES)

def hash_password(password):
    """Hashea la contraseña usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    cors_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'  # Permitir acceso desde cualquier origen
    }
    
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        
        email = body.get('email')
        password = body.get('password')
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Email y contraseña son requeridos'})
            }
        
        # Buscar restaurante en DynamoDB usando 'email' como clave
        response = table.get_item(Key={'email': email})
        if 'Item' not in response:
            return {
                'statusCode': 401,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Credenciales inválidas'})
            }
        
        restaurant = response['Item']
        
        # Verificar contraseña
        hashed_password = hash_password(password)
        
        if restaurant['password'] != hashed_password:
            return {
                'statusCode': 401,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Credenciales inválidas'})
            }
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'message': 'Login exitoso',
                'restaurant': {
                    'restaurant_id': restaurant.get('restaurant_id'),
                    'email': restaurant.get('email'),
                    'nombre_restaurante': restaurant.get('nombre_restaurante')
                }
            })
        }
    
    except Exception as e:
        print(f"Error en Login: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Error interno del servidor', 'details': str(e)})
        }
