Buenas equipo, para empezar con el despliegue de la red en AWS y asegurar que todo encaje,
propongo lo siguiente. Revisad y confirmad vuestros puntos:

1. Direccionamiento IP y Subnetting (VPC: 10.0.0.0/16)
He diseñado este esquema para evitar solapamientos y permitir el aislamiento:

- Subred Pública (10.0.1.0/24): Para el Bastion Host y NAT Gateway.

- Subred IoT - "Production" (10.0.2.0/24): Donde vivirán los dispositivos a vigilar.

- Subred de Cuarentena/Honeypots (10.0.3.0/24): Zona estanca para el desvío de atacantes.

- Subred de Seguridad (10.0.4.0/24): Para la instancia de análisis (Suricata/IDS).

¿Algún conflicto con los rangos que teníais en mente?

2. Diccionario de "Tags" (Para Python/Boto3)
Para que el script de Python encuentre los recursos sin errores, usaremos estas etiquetas obligatorias:

Project: SentinelCloud

SecurityStatus: Healthy | Infected | Quarantined

Type: IoT-Device | Honeypot | IDS

Programador: ¿Necesitas algún Tag extra para que la lógica de filtrado en Boto3 sea más sencilla? o tenias otra cosa en mente

3. Requerimientos de Puertos y Tráfico (Para Ciberseguridad)
Necesito que me confirmes los "agujeros" que debo abrir en los Security Groups:

- Honeypot (Cowrie): ¿Qué puertos queréis abiertos al mundo en la zona de señuelo? (Propongo TCP 22, 23, 2222).

- IDS (Suricata/Falco): Voy a configurar VPC Traffic Mirroring. ¿Vuestra instancia recibirá el tráfico por el puerto estándar VXLAN (UDP 4789)?

4. Permisos de Ejecución (IAM Policy)
He preparado una política de "Mínimo Privilegio" para la Lambda de automatización. El script solo podrá:

- ec2:DescribeInstances (Para buscar víctimas).

- ec2:ModifyInstanceAttribute (Para cambiar el Security Group de la víctima).

- ec2:CreateSnapshot (Para el análisis forense previo al aislamiento).

Programador: ¿Vas a necesitar permisos de S3 para guardar logs o CloudWatch para métricas personalizadas?

5. Con todo OK
Una vez todo aclarado, desplegaré la VPC y los Security Groups base. A partir de ahí, la red estará lista para recibir vuestros contenedores y scripts.
