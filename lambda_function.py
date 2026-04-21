import boto3    # Librería AWS para Python
import json     # Para manejar los datos del ataque y el reporte
import os       # Para leer variables del entorno que configuramos
from datetime import datetime 

# --- Inicialización de Clientes --- #
# Objetos que nos permiten dar órdenes a los servicios de AWS

ec2 = boto3.client('ec2')
s3 = boto3.client('s3')

def lambda_handler(event, context): 
    # Punto de Entrada de Lambda.
    # Se ejecuta cada vez Amazon EventBridge detecta un ataque en GuardDuty
    try: 
        # 1. Extraccion de Datos
        # Sacamos la info del JSON que nos envía GuardDuty de forma automática
        detail = event.get('detail', {})
        instance_id = detail.get('resource', {}).get('instanceResource', {}).get('instanceId')
        attack_type = detail.get('type', 'Ataque Desconocido')
        attacker_ip = detail.get('service', {}).get('action', {}).get('networkConnectionAction', {}).get('remoteIpDetails', {}).get('ipAddressV4', '0.0.0.0')

        # Verificación de seguridad: Si no hay ID de instancia, no podemos hacer nada
        if not instance_id:
            print("❌ Error: No se ha detectado el InstanceId en el hallazgo.")
            return {'statusCode': 400, 'body': 'InstanceId no encontrado'}

        print(f"🚨 [SENTINEL] Amenaza detectada: {attack_type} contra {instance_id}")

        # 2. Acción de Respuesta (Aislamiento de red)
        # Leemos el ID del SG de Cuarentena de las variables de entorno (el de Iván)
        target_sg = os.environ.get('QUARANTINE_SG')
        
        # Esta es la ejecución SOAR: Cambiamos el "muro" de la máquina en caliente
        ec2.modify_instance_attribute(
            InstanceId=instance_id,
            Groups=[target_sg]
        )
        print(f"🔒 [SENTINEL] Instancia {instance_id} movida a zona de CUARENTENA.")

        # 3. Generación del Report (Pintado del panel)
        # Creamos un pequeño objeto con la información de lo que acaba de pasar
        panel_data = {
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "🔴 CRITICAL - ISOLATED",
            "victim_id": instance_id,
            "threat": attack_type,
            "attacker": attacker_ip,
            "applied_policy": "Quarantine_SG_Enforced"
        }

        # Subimos este JSON a tu Bucket de S3 
        # Nombre: sentinelcloud-dashboard-python-bucket
        s3.put_object(
            Bucket=os.environ.get('DASHBOARD_BUCKET'),
            Key='live_status.json',
            Body=json.dumps(panel_data, indent=4), # indent=4 para que se lea bien
            ContentType='application/json'
        )
        print("📊 [SENTINEL] Información del incidente enviada al Dashboard de S3.")

        return {
            'statusCode': 200,
            'body': json.dumps(f"Amenaza neutralizada con éxito en {instance_id}")
        }

    except Exception as e:
        # Si algo falla (permisos, IDs mal puestos...), lo capturamos aquí
        error_msg = f"❌ [ERROR] Fallo en la automatización: {str(e)}"
        print(error_msg)
        return {'statusCode': 500, 'body': json.dumps(error_msg)}
