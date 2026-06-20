Estas indicaciones estan con nodejs, pero mejor hazlas con FastAPI (Python) + React + PostgreSQL, no Dockerices

Quiero que desarrolles un programa contable, que tambien genere facturas electronicas para que se envien al SRI, el nombre del programa es: ContaEC, el autor o desarrollado por: T\&M Technology Ec, telefono de contaco: 0960068866, correo de soporte: info@tymtechnology.shop, el DNS para la pagina es: conta.tymtechnology.shop El servidor donde se va a montaar es una LXC de proxmox, tiene la ip: 10.0.1.20:80 ya esta creado en NPM la salida a internet y la difusion DNS, con su respectivo certificado Let's Encrypt Te comparto las características de mi servidor:

\*\* CPU(s)\*\*: 8 x Intel(R) Xeon(R) CPU E5-1620 v2 @ 3.70GHz (1 Zócalo) (3Nucleos Usados) -RAM: 10GB. (Libres 6GB)
\*\*Almacenamiento\*\*: 205 GB HDD (Libres).
\*\*Red\*\*: Interfaz (vmbr0) salida a internet con mi ISP Interfaz puente (vmbr1) asignada con IP estática 10.0.1.20/24 Haz la aplicacion lo más ligera posible tomando en cuneta los recursos disponibles. Además, el programa debe incluir las siguientes características:

1. No dejar las API KEY expuestas.
2. Sanitizar todas las entradas.
3. Añadir limitación de tasa a las rutas de la API.
4. Manejar inventario.
5. Permitir un flujo contable y otras funcionalidades.
6. Ser multiempresa, permitiendo que un mismo usuario maneje múltiples empresas por separado y gestión de clientes.
7. Guardar automáticamente los datos en un archivo exportable a medianoche, que solo el sistema reconozca.
8. ermitir la recarga de dicha configuración de respaldo y datos en caso de fallo de la máquina.
9. Incluir dashboards interactivos.
10. Exportar todas las funcionalidades contables, incluyendo inventario.
11. Permitir la importación y exportación de archivos en formatos Excel, CSV, PDF y ZIP.
12. Operar en línea, permitiendo acceso y ejecución tras el despliegue en el servidor.
13. Permitir al usuario seleccionar entre modo claro y oscuro.
14. El modo claro debe ser un color suave que no canse la vista.
15. Permitir al usuario seleccionar su idioma de preferencia.
16. El idioma de preferencia debe ser español de Ecuador y que tenga la opción de cambiar de idioma.
17. Incluir una opción avanzada de correo para configuración con proveedores externos (Gmail, Zoho, Microsoft, etc.) mediante IMAP, POP y SMTP.
18. Manejar seguridad mediante ClamAV y VirusTotal para escanear archivos subidos en busca de malware. 
Te detallo la estructura del punto 18 Objetivo: cada vez que el usuario suba un Excel (o ZIP, CSV, etc.), lo escanee antes de guardar y, si contiene malware, lo rechaces o lo marque como sospechoso. 
Arquitectura típica: 
    • Servidor Linux donde corre tu sistema contable (Apache/Nginx + PHP, Node.js, Python, Java, etc. acorde al lenguaje que escojas). 
    • Instalas ClamAV y el daemon clamd (mejor rendimiento que llamar a clamscan cada vez). 
    • Tu backend envía temporalmente el archivo subido al servidor y llama al socket de clamd para verificarlo. Flujo recomendado: 
    • El usuario sube el archivo (por ejemplo, inventario.xlsx). 
    • El servidor lo guarda en una carpeta temporal (ej. /tmp/uploads/...). 
    • Tu backend (PHP, Python, Node.js, etc.) llama a ClamAV sobre ese path. Si ClamAV devuelve: 
    • Limpio: mueves el archivo a la ubicación definitiva, procesas el Excel y lo importas. 
    • Malware: borras el archivo, registras el intento en el log y avisas al usuario (“El archivo contiene malware o no pasa el escaneo”). Usa ClamAV como escaneo por defecto para todos los archivos subidos. Usa VirusTotal solo: 
    • Como opción que el usuario activa (“escanear también con VirusTotal”), 
    • solo para archivos muy grandes o sospechosos (por ejemplo, si ClamAV da mucha “falsos positivos”)
Ejemplo de enfoque: Usuario sube archivo → sistema:
    - Guarda temporalmente.
    - Pregunta: ¿se habilitó ClamAV? → SÍ → ejecuta clamdscan/clamscan.
    - Si malware: • Borrar/temporal. • Log + alerta al usuario.
    - Si limpio: • Guardar definitivo. • Procesar Excel (inventario, clientes, productos).
    - Si el usuario marcó “analizar con VT”: • Enviar el hash (o el archivo) a VirusTotal API (sin bloquear el flujo principal).
19. en la interfaz visual al momento de llenar los datos para cada empresa debe existir campos para:
        - firma electronica
        - clave de la firma electrónica estos dos puntos deben guardarse netamente en el archivo .env
        - una vez cargada la firma debe indicar el tiempo de validez que tiene dicha firma
        - colocar logotipo de la empresa
        - el ruc de la empresa al momento de colocar el RUC de la empresa debe automaticamente llenar los campos de la empresa, esto debe realizarse mediante la consulta al SRI
        - El usuario debe colocar la clave para encriptar los backups (debe solicitarse una sola vez) y esta calve automaticamente debe guardarse en el archivo .env
        - El programa una vez desplegado en el servidor al momento de que se cree un nuevo usuario debe crear automaticamente todo lo ecesario para que el sistema le funcione correctamente, si el nombre del usuario o correo del usuario a registrar coincide con alguno ya existente no permitir crear otro usuario.
20. Toda la configuracion que se cree de cada usuario debe manejar sus respectivos aislamientos, eso quiere decir que cada usuario debe tener su propio .env para evitar problemas
21. Para (.env por usuario) En una aplicación web tradicional, cargar múltiples .env concurrentemente en un mismo proceso de Node.js no es posible sin que colisionen las variables de entorno. 
22. Implementa un sistema de configuración donde la "configuración de entorno" de cada usuario (firma, clave, SMTP, clave de backup) se guarde de forma encriptada en la base de datos central o en archivos JSON/Vault individuales seguros (config\_{userId}.json) dentro de una carpeta protegida en el servidor. El archivo .env principal solo contendrá las credenciales maestras de la base de datos y llaves de encriptación general. 
23. Si es posible configura para cada usuario un entorno de pruebas (un boton o una opción) para que pueda configurar adecuadamente, hasta el envío de correos, etc. y posterior pasar a producción. 
24. Genera un licenciamineto anual, mensual, trimenstral, semestral, el cual solo el adminsitrador pueda manipular y dar esas credenciales a los usuarios.
25. Genera un panel de administrador que solo se pueda acceder con credenciales predeterminadas como admin para validar:
    - un dashboard general que contenga un resumen de todo lo solicitado a continuación.
    - una pestaña para un dashboard detallado que indique el estado del sistema (salud del sistema)
    - una pestaña para un dashboard detallado que indique todos los usuarios y tiempo de vigencia de sus licencias, con opcion para modificar el tiempo del licenciamineto de cada usuario (mensual, trimestral, semestral y anual)
    - una pestaña para un dashboard detallado que indique problemas de seguridad de cada usuario las credenciales para acceder a este panel de administrador son: • User: 'steve.mejia@tymtechnology.shop' • Pass: 'Vitaestcum21..'
    - Que genere una alerta a cada usuario en el dashboard principal indicando que su licenciamiento esta proximo a caducar.
26. Para los pagos, haz que al momento que el usuario seleccione la opcion se conecte con whatsapp y que llegue con el mensaje de quiero renovar mi licencia por x meses seleccionados
27. Las opciones de licenciamiento dentro de la pasarela de pagos debe ser mensual, trimestral, semestral, anual
28. Crea una opción de recursos humanos (nómina) donde se pueda hacer: 
    • Registro de empleados: Datos personales, contratos, cargos, salario base, cargas familiares, historial laboral y valuarizaciones de puestos. 
    • Cálculo automatizado: Sueldos quincenales/mensuales, horas extras, décimo tercero (mensualizado/anual), décimo cuarto (sierra/costa), vacaciones, utilidades, fondos de reserva y liquidaciones laborales. 
    • Rubros personalizables: Bonificaciones, comisiones, anticipos, alimentación, seguros, descuentos (préstamos, embargos) con impacto contable y tributario. 
    • Cumplimiento y Reportes: Incluye generación de roles de pago detallados (bruto, deducciones, neto), RDEP, anexos IESS (Batch), SUT XIII-XIV, IR y archivos XML para SRI/nómina electrónica. 
    • Sincronización con asistencia (biométricos, turnos rotativos), bancos para pagos masivos, contabilidad (asientos automáticos) y multiempresa para contadores. 
    • Reportes analíticos: Costos por departamento, proyecciones y exportación a Excel/PDF. 
    • Exportación de archivos para pago de sueldos en Excel, CSV, PDF.
29. Añade almacenamiento volátil para la creación de archivos de exportación/importación una vez cargada la data o descargada automaticamente debe eliminarse dicho archivo del sistema para evitar ocupar almacenamiento.
30. El resultado final debe ser un programa claro, funcional y que cumpla con todos los requisitos mencionados, detalla el cómo debe montarse en el servidor, instalación y configuración de la base de datos, detalla que se debe crear en el archivo .env todo esto es para que se pueda entender y ejecutar el proyecto sin ambigüedades. En el documento @upload/FICHA_TECNICA.md encontrarás toda la guia oficial del SRI, como son la creación de reportes, facturación electrónica, régimen, etc. Revisa el documento para que quede todo alineado a las peticiones del SRI ten en cuenta esto para la fase 3: debes completar todos los IVA que existe (0%, 5%, 8%, 12%, 13%, 14%, 15%, No objeto de impuesto, Exento de IVA, IVA diferenciado) dejando por defecto el 15%, manejar las tarifas de ICE, de igual forma manejar las tarifas de Retenciones (10%, 20%, 30%, 50%, 70%, 100%, 0%), manejando tambien los estados del comprobante electronico, todos estos debes hacerlo con sus respectivos códigos. Completa todos los contribuyentes (no obligado a llevar contabilidad, obligado a llevar contabilidad, etc) y todos los régimen (rimpe emprendedor, rimpe negocio popular, general, etc), consumidor final (cliente por defecto), ya que cada uno de ellos trabaja de forma diferente.


Trabajaremos a modo de fases para aligerar la carga y que sea más fácil la creación

Fase 1 Servidor, BD, Balanceador de carga Infraestructura base: Node.js, PostgreSQL, configuración de servidor y proxy reverso
Fase 2 Auth, Multiempresa, Admin, Licencias, ClamAV Autenticación JWT, gestión de usuarios, licenciamiento por tiempo, seguridad con antivirus
Fase 3 Facturación Electrónica SRI completa, Facturas, notas de crédito/débito, retenciones, guías de remisión, firma XML, webservices SRI. Debes completar todos los IVA que existe (0%, 5%, 8%, 12%, 13%, 14%, 15%, No objeto de impuesto, Exento de IVA, IVA diferenciado) dejando por defecto el 15%, manejar las tarifas de ICE, de igual forma manejar las tarifas de Retenciones (10%, 20%, 30%, 50%, 70%, 100%, 0%), manejando tambien los estados del comprobante electronico, todos estos debes hacerlo con sus respectivos códigos. Completa todos los contribuyentes (no obligado a llevar contabilidad, obligado a llevar contabilidad, etc) y todos los régimen (rimpe emprendedor, rimpe negocio popular, general, etc), consumidor final (cliente por defecto), ya que cada uno de ellos trabaja de forma diferente, y añade también proformas.
Fase 4 Inventario, Kardex, Importación/Exportación Control de productos, stock, movimientos, códigos de barras, importación/exportación de datos
Fase 5 Nómina RRHH Empleados, contratos, roles de pago, IESS, décimos, fondos de reserva, asistencia, valuación de puestos
Fase 6 Frontend Next.js completo Interfaz de usuario web con Next.js, React, dashboard, formularios, reportes visuales
Fase 7 SMTP avanzado + Sandbox Múltiples configuraciones SMTP, plantillas de email, modo pruebas sin envío real al SRI, logs de auditoría
Fase 8 Gestión de Compras y Proveedores Catálogo de proveedores, órdenes de compra, recepción de mercadería, cuentas por pagar, retenciones
Fase 9 Multi-Almacén y Logística Múltiples bodegas, transferencias entre almacenes, ubicaciones físicas (rack/estante), kardex detallado
Fase 10 Punto de Venta (POS) Retail Terminal de venta táctil, escáner de códigos de barras, impresión de tickets, arqueo de caja
Fase 11 Business Intelligence y Dashboards KPIs en tiempo real, reportes visuales gráficos, alertas inteligentes, cuadro de mando, exportación a Power BI
Fase 12 Presupuestos y Control Presupuestario Presupuesto anual por cuenta, ejecución presupuestaria mensual, alertas de sobregiro, comparativo vs real
Fase 13 CRM Avanzado Pipeline de ventas, cotizaciones, oportunidades, seguimiento comercial, segmentación de clientes, automatización
Fase 14 Proyectos y Servicios Gestión de proyectos, asignación de recursos, control de tiempos/timesheet, rentabilidad por proyecto
Fase 15 Integraciones Integración bancaria (extractos), conectores e-commerce (Shopify, WooCommerce, Opencart, Prestashop, Magento, etc)
Fase 16 Machine Learning / IA Predicción de ventas, detección de fraude, categorización automática, chatbot de soporte, recomendaciones

toma en cuenta que ya esta levantado el servicio de lets encrypt, y ya esta hecho el proxy reverse, solo es necesario que el aplicativo en la maquina lxc apunte al puerto 80 y automaticamente funciona en linea, lee el repositorio ahí encontraras el archivo @upload/FICHA_TECNICA.md.