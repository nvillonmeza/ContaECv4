tengo varios puntos a resolver, todos los cambios que vayas a realizar hazlos sin ningún problema en el código de este directorio, dado que por todos los cambios va a ser necesario volver a crear una nueva maquina con los nuevos ajustes, por ende elimina los archivos que creaste 1. parasubir.py, 2. la carpeta scripts y su archivo interno, si lo que creaste es necesario cambiar a algún archivo o modificar a aalguna rchivo hazlo directo en el archivo y usa la skill de token-efficiency en todo momento:

1. en la opción de contabilidad
1.1 en la pestaña de Plan de cuentas, necesito tres cambios: primero que exista un buscador de códigos, dos que cuando se seleccione el plan de cuentas se auto rellene los campos y crea un campo nuevo de notas donde escriban las cosas que crean necesarias y por ultimo al momento de crear una cuenta contable no se crea, no genera un código de error visible pero en consola aparece este error: /api/v1/accounting/c…938f-d3060988872f:1 
 Failed to load resource: the server responded with a status of 404 ()
page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/accounting/cuentas-contables?company_id=72c8754f-4109-48f6-938f-d3060988872f 404 (Not Found)
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
aK	@	page-177de2c95b3846c3.js:1
E	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
1.2. en la pestaña de asientos, apenas se abre aparece este código que se repite dos veces: page-177de2c95b3846c3.js:1 
 GET https://conta.tymtechnology.shop/api/v1/accounting/cuentas-contables?company_id=72c8754f-4109-48f6-938f-d3060988872f 404 (Not Found)
$	@	page-177de2c95b3846c3.js:1
B	@	page-177de2c95b3846c3.js:1
aX	@	page-177de2c95b3846c3.js:1
(anonymous)	@	page-177de2c95b3846c3.js:1
(anonymous)	@	page-177de2c95b3846c3.js:1
o1	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
i_	@	4bd1b696-c023c6e3521b1417.js:1
iT	@	4bd1b696-c023c6e3521b1417.js:1
iN	@	4bd1b696-c023c6e3521b1417.js:1
iz	@	4bd1b696-c023c6e3521b1417.js:1
ii	@	4bd1b696-c023c6e3521b1417.js:1
iu	@	4bd1b696-c023c6e3521b1417.js:1
iG	@	4bd1b696-c023c6e3521b1417.js:1
iW	@	4bd1b696-c023c6e3521b1417.js:1
iK	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
de igual manera no permite crear el asiento, no sé si es porque no hay creada un plan de cuentas o porque pero en la opción de selección de cuenta no me aparece opciones y creo que por eso no permite crear el asiento
1.3. en la ventana de cuentas por cobrar CxC, al momento de crear una CxC no me deja crear de igual forma no aparece errores visibles pero si en consola del navegador: page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/accounting/cuentas-por-cobrar?company_id=72c8754f-4109-48f6-938f-d3060988872f 404 (Not Found)
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
a5	@	page-177de2c95b3846c3.js:1
A	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
1.4. en la ventana de pagos no me deja crear de igual forma no aparece errores visibles pero si en consola del navegador:
POST https://conta.tymtechnology.shop/api/v1/accounting/pagos?company_id=72c8754f-4109-48f6-938f-d3060988872f 404 (Not Found)
page-177de2c95b3846c3.js:1 
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
a9	@	page-177de2c95b3846c3.js:1
C	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
1.5. en la ventana de periodos no me deja crear de igual forma no aparece errores visibles pero si en consola del navegador:
page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/accounting/periodos-fiscales?company_id=72c8754f-4109-48f6-938f-d3060988872f 404 (Not Found)
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
ra	@	page-177de2c95b3846c3.js:1
_	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
1.6. para las ventanas de balance y cartera debo entender como no se han creado ningún dato no muestra nada.

2. en la opción de IA/ML
2.1. en la ventana de predicciones no permite crear una nueva predicción creo se debe a que no hay datos para que los haga.
2.2. en la ventana de fraude se más especifico de que se hace ahí dado que no se entinde.
2.3. en la ventana de chatbot al momento de tratar de crear una nueva sesión de chat me aparece un mensaje de: error al crear sesión de chat y en consola aparece este mensaje de error: page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/ml-ai/chatbot/sessions 500 (Internal Server Error)
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
rh	@	page-177de2c95b3846c3.js:1
eM	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
de igual manera al momento de tratar de escribir un mensaje en el chat existente aparece un mensaje de error: error al enviar mensaje, y en consola aparece este mensaje de error:
page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/ml-ai/chatbot/chat 422 (Unprocessable Content)
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
rj	@	page-177de2c95b3846c3.js:1
eU	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
2.4. en la ventana de recomendaciones al momento de dar clic en nueva rpediccion no hace nada supongo es porque no hay datos
2.5. en la ventana de categorización al momento de tratar de crear una nueva regla no sé que es eso de patron regex, prioridad como se sabe cual es la escala de prioridad, igual al momento de crear una regla me aparece un mensaje de error: error al crear regla y en consola aparece esto:
page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/ml-ai/categorize/rules 400 (Bad Request)
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
r_	@	page-177de2c95b3846c3.js:1
eH	@	page-177de2c95b3846c3.js:1
onClick	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
3. en la opción de integraciones
3.1. en la pestaña de cuenta bancaria, cuando se crea una nueva cuenta bancaria, donde dice iban cámbialo por SWIFT/BIC dado que en ecuador la mayoría de bancos maneja ese código, ejemplo: banco pichincha: PICHECEQXXX, banco Produbanco: PRODECEQXXX, banco bolivariano: BBOLECEQXXX, busca los códigos para los bancos pichincha, bolivariano, internacional, Rumiñahui, Produbanco, banco del austro, guayaquil, banco del pacifico, para automatizar genera una lista para nombre de banco y coloca los que te acabe de mencionar para que el cliente cuando seleccione esos bancos automaticamente se llene el código SWIFT/BIC y una opción de otro banco en donde el cliente coloque manualmente todos los datos. Cuando se guarda la cuenta aparece un mensaje de creada cuenta con éxito pero no aparece la cuenta y en consola aparece este mensaje de error: page-177de2c95b3846c3.js:1 
 GET https://conta.tymtechnology.shop/api/v1/integrations/bank/accounts?company_id=72c8754f-4109-48f6-938f-d3060988872f 500 (Internal Server Error)
$	@	page-177de2c95b3846c3.js:1
B	@	page-177de2c95b3846c3.js:1
aF	@	page-177de2c95b3846c3.js:1
(anonymous)	@	page-177de2c95b3846c3.js:1
ed	@	page-177de2c95b3846c3.js:1
await in ed		
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
indica no hay cuentas registradas pero en la parte superior si aparece que esta 1 cuenta creada con el valor ingresado.
3.2. en la pestaña de e-commerce, cuando ingreso los datos de ejemplo woocommerce me da un error que es: error interno del servidor intente nuevamente y en consola aparece este mensaje: page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/integrations/ecommerce/connectors 500 (Internal Server Error)
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
aB	@	page-177de2c95b3846c3.js:1
ej	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
usa estas credenciales para que hagas prueba de conectividad:
Clave del cliente:
ck_a50ac07f3ae591f066c26e41eeea58e5feffeac5
Clave secreta de cliente:
cs_2389c7388dcc645b91829404532913fa0d06a9e7
4. en la opción de Proyectos
4.1 cuando se da clic en proyectos aparece una pantalla en blanco con este mensaje: Application error: a client-side exception has occurred while loading conta.tymtechnology.shop (see the browser console for more information). y este error en consola: 
page-177de2c95b3846c3.js:1 Uncaught TypeError: (intermediate value)(intermediate value)(intermediate value).toFixed is not a function
    at c3 (page-177de2c95b3846c3.js:1:485829)
    at l9 (4bd1b696-c023c6e3521b1417.js:1:51124)
    at o_ (4bd1b696-c023c6e3521b1417.js:1:70984)
    at oq (4bd1b696-c023c6e3521b1417.js:1:82014)
    at ik (4bd1b696-c023c6e3521b1417.js:1:114676)
    at 4bd1b696-c023c6e3521b1417.js:1:114521
    at ib (4bd1b696-c023c6e3521b1417.js:1:114529)
    at iu (4bd1b696-c023c6e3521b1417.js:1:111612)
    at iX (4bd1b696-c023c6e3521b1417.js:1:132928)
    at MessagePort.w (255-98a0bdaa30757bda.js:1:114714)
5. en la opción de CRM
5.1. en la ventan de Leads explica un poco mejor que es un lead yo supongo que son los clientes potenciales, si es así, agrega un botón de cargar para poder importar todos los clientes que se tenga, cuando se crea un nuevo lead, en la opción de fuente ya se selecciona pero no aparece lo que se selcciona y cuando se quiere crear el lead aparece este mensaje: Fuente inválida: llamado. Debe ser uno de: other, ad, social, event, referral, website y en consola este mensaje de error: page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/crm/leads 400 (Bad Request)
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
rE	@	page-177de2c95b3846c3.js:1
k	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
2
content.js:1 Uncaught (in promise) The message port closed before a response was received.
(anonymous)	@	content.js:1
﻿5.2 cuando se da clic en oportunidades automáticamente aparece un error en consola: 
page-177de2c95b3846c3.js:1 
 GET https://conta.tymtechnology.shop/api/v1/clients?company_id=72c8754f-4109-48f6-938f-d3060988872f 500 (Internal Server Error)
$	@	page-177de2c95b3846c3.js:1
B	@	page-177de2c95b3846c3.js:1
eU	@	page-177de2c95b3846c3.js:1
(anonymous)	@	page-177de2c95b3846c3.js:1
(anonymous)	@	page-177de2c95b3846c3.js:1
o1	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
ux	@	4bd1b696-c023c6e3521b1417.js:1
uE	@	4bd1b696-c023c6e3521b1417.js:1
i_	@	4bd1b696-c023c6e3521b1417.js:1
iT	@	4bd1b696-c023c6e3521b1417.js:1
iN	@	4bd1b696-c023c6e3521b1417.js:1
iz	@	4bd1b696-c023c6e3521b1417.js:1
ii	@	4bd1b696-c023c6e3521b1417.js:1
iu	@	4bd1b696-c023c6e3521b1417.js:1
iG	@	4bd1b696-c023c6e3521b1417.js:1
iW	@	4bd1b696-c023c6e3521b1417.js:1
iK	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
de igual forma cuando se crea una nueva oportunidad, al momento de seleccionar una etapa no se muestra la etapa seleccionada ni la fuente selccionada, cuando se trata de crear una nueva oportunidad aparece este mensaje: Field required, Field required, Field required y en consola este mensaje de error: page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/crm/opportunities 422 (Unprocessable Content)
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
s7	@	page-177de2c95b3846c3.js:1
z	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
5.3. en la ventana de actividades cuando se trata de crear una nueva actividad y guardarla aparece este mensaje: Field required, Field required, y en consola aparece este mensaje: 
content.js:1 Uncaught (in promise) The message port closed before a response was received.
(anonymous)	@	content.js:1
page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/crm/activities 422 (Unprocessable Content)
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
an	@	page-177de2c95b3846c3.js:1
_	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
5.4. en la ventana de segmento cuando se crea un nuevo segmento en la venta que se abre en tipo no se puede seleccionar algo diferente a normal, en las regrlas json solo dice {"campo":"valor"}, de preferencia escribe un código de ejemplo para que vean y sepan que es lo que se debe colocar ahí, nuevamente en tipo cuando coloque el valor: {"campo":"valor"} cambio a dinamico para ese punto deberías colocar un signo de interrogación con más información sobre los tipos que van a haber, a pesar de que se llene todos los campos indica un mensaje: Field requiredy en consola el mensaje de error: 
page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/crm/segments 422 (Unprocessable Content)
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
ac	@	page-177de2c95b3846c3.js:1
N	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
5.5. en la ventana automatizaciones en el campo condiciones json y acciones json de igual forma indica para que sirve cada uno y un ejemplo practico de que es lo que se debe colocar ahí, si se escribe un texto largo en ambos campos se pierde los botones paracrear automatizaciones dado que no existe un scrollbar para eso, cuando se trata de guardar aparece este mensaje: Field required, Field required
 y en consola:
content.js:1 Uncaught (in promise) The message port closed before a response was received.
(anonymous)	@	content.js:1
page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/crm/automations 422 (Unprocessable Content)
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
ad	@	page-177de2c95b3846c3.js:1
b	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:19
6. en la opción de presupuestos
6.1 en la ventana de presupuestos igual que en plan de cuentas porfavor agrega la lista de plan de cuentas para que el usuario solo busque el código y automatico se llene el nombre, igual coloca un buscador para que sea más fácil la búsqueda del código del plan de cuentas, cuando se da clic en guardar aparece un mensaje:Error interno del servidor. Intente nuevamente. y en consola aparece este error: 
page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/budgets 500 (Internal Server Error)
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
sX	@	page-177de2c95b3846c3.js:1
w	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
cuando se da cancelar no cambia el conteo de borrador, total, aprobados, cerrados, sobregiros, o explícame como funciona eso dado que no existe el como.
7. en la opción de compras
7.1. funciona todo atado a proveedor lo cual esta bien, el problema que no se puede crear en proveedor eso lo veremos en el siguiente punto
8. en la opción de proveedores
8.1. en la opción de plantillas email no existen plantillas pre configuradas, cuando se da clic en nueva plantilla, en el tipo, no aparece el tipo seleccionado así se seleccione diferentes tipos no muestra en pantalla, en cuerpo HTML coloca un ejemplo de como es lo que debe ser el HTML que se coloque en ese campo, cuando se trata de guardar aparece este mensaje: Error interno del servidor. Intente nuevamente., y en consola aparece este error: page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/email-templates 500 (Internal Server Error)
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
sv	@	page-177de2c95b3846c3.js:1
U	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
al momento de tratar de crear un nuevo proveedor aparece dos mensajes uno de: proveedor creado y al mismo tiempo otro de: Error al cargar proveedores y en consola aparece este mensaje de error: page-177de2c95b3846c3.js:1 
 GET https://conta.tymtechnology.shop/api/v1/suppliers?company_id=72c8754f-4109-48f6-938f-d3060988872f 500 (Internal Server Error)
$	@	page-177de2c95b3846c3.js:1
B	@	page-177de2c95b3846c3.js:1
sn	@	page-177de2c95b3846c3.js:1
(anonymous)	@	page-177de2c95b3846c3.js:1
V	@	page-177de2c95b3846c3.js:1
await in V		
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
9. en la opción de recursos humanos
9.1. en la ventana de empleados crear nuevo empleado en el campo de tipo de contrato no aparece en pantalla el tipo seleccionado, de igual forma el tipo de pago no aparece en pantalla el tipo pago seleccionado. Cuando se guarda el empleado aparece este mensaje: Not Found, y en consola este error: page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/employees 404 (Not Found)
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
e3	@	page-177de2c95b3846c3.js:1
b	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
9.2. en la ventana de generar rol cuando se selecciona el mes no aparece en pantalla el mes seleccionado, cuando se guarda aparece un mensaje de: Not Found y en consola aparece el error: page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/payroll/generate 404 (Not Found)
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
e6	@	page-177de2c95b3846c3.js:1
b	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
9.3. en la ventana de IESS cambia totalmente el flujo tu colocas consultar pero no hay que hacer eso debes hacer el calculo tu mismo (por favor busca en internet el porcentaje de una empresa privada de cuanto es lo que debe ser asumida por empresa y cuanto por el trabajador, busca el porcentaje valido para junio 2026)
9.4. en la ventana de liquidaciones en la opción para seleccionar a los empleados a liquidar, permite que sea de elección multiple para poder seleccionar a varios empleadoa a la vez y poder hacer los cálculos, en el campo motivo, cuando se selecciona un motivo no aparece en pantalla dicha elección.
9.5. en la ventana de impuesto a la renta, revisa la tabla dado que el texto de la tabla sobresale del recuadro que lo contiene, cuando se intenta calcular aparece un mensaje de error: Not Found y en consola aparece: page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/payroll/calcular-ir 404 (Not Found)
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
r$	@	page-177de2c95b3846c3.js:1
d	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
10. en la opción de punta de venta
10.1 al momento de abrir caja aparece un mensaje: Error interno del servidor. Intente nuevamente. y en consola aparece el mensaje de error: page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/pos/sessions 500 (Internal Server Error)
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
sO	@	page-177de2c95b3846c3.js:1
ef	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
11. en la opción de almacenes
11.1 en la ventana de bodegas, al momento de crear una nueva bodega aparece dos mensajes uno que dice bodega creara y otro que dice error al crear bodegas, y aparece un mensaje de error en consola: page-177de2c95b3846c3.js:1 
 GET https://conta.tymtechnology.shop/api/v1/warehouses?company_id=72c8754f-4109-48f6-938f-d3060988872f 500 (Internal Server Error)
$	@	page-177de2c95b3846c3.js:1
B	@	page-177de2c95b3846c3.js:1
s_	@	page-177de2c95b3846c3.js:1
(anonymous)	@	page-177de2c95b3846c3.js:1
C	@	page-177de2c95b3846c3.js:1
await in C		
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
11.2. en la ventana de Kardex detallado, los estilos están mal configurados dado que no se puede visualizar bien los campos, si se da clic en el botón de descargar aparece un mensaje de: Funcionalidad de exportacion próximamente.

12. en la opción de Inventario

13. en la opción de productos
13.1. al momento de crear un nuevo producto, porfavor reestructura todo el formulario dado que los datos solicitados son la mitad de lo que debería existir, los datos que deben existir (incluido en la base de datos) son: categoría de producto, imagen de producto, código de producto (este debe ser principal para que no exista duplicado de productos), código auxiliar, nombre, precio unitario, iva incluido en el precio (chackbox), subsidio, seleccione iva, seleccione ice, valor ice unitario (se debe activar si se selecciona alguna de las opciones de ice), valor IRBPNR, detalle, descripción. (para los valores del iva y del ice, consultar el documento que se encuentra en @upload/FICHA_TECNICA.md), también agrega un botón para importar productos, un botón para exportar los productos y un botón donde se descargue el archivo muestra de como deben subirse los productos dado de que se importe. actualmente presenta estos mensajes de error en la creacion de productos: el primer mensaje es: producto creado y el segundo mensaje es error al cargar productos, en consola aparece el siguiente error:
page-177de2c95b3846c3.js:1 
 GET https://conta.tymtechnology.shop/api/v1/products?company_id=72c8754f-4109-48f6-938f-d3060988872f 500 (Internal Server Error)
$	@	page-177de2c95b3846c3.js:1
B	@	page-177de2c95b3846c3.js:1
eO	@	page-177de2c95b3846c3.js:1
(anonymous)	@	page-177de2c95b3846c3.js:1
S	@	page-177de2c95b3846c3.js:1
await in S		
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
13.2. en la ventana de clientes, en el campo de identificación y teléfono permite letras lo cual no es valido ya que solo debe ser numero, cuando se guarda el cliente aparecen dos mensajes: el primero es cleinte creado y el segundo mensaje es error al cargar cleintes, en consola aparece el siguiente error:
page-177de2c95b3846c3.js:1 
 GET https://conta.tymtechnology.shop/api/v1/clients?company_id=72c8754f-4109-48f6-938f-d3060988872f 500 (Internal Server Error)
$	@	page-177de2c95b3846c3.js:1
B	@	page-177de2c95b3846c3.js:1
eU	@	page-177de2c95b3846c3.js:1
(anonymous)	@	page-177de2c95b3846c3.js:1
S	@	page-177de2c95b3846c3.js:1
await in S		
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
13.3. en la ventana de factura al momento de crear un nuevo cliente apareció este mensaje: [object Object] y en consola apareció estos errores: 
page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/clients 401 (Unauthorized)
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
e$	@	page-177de2c95b3846c3.js:1
C	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/clients 422 (Unprocessable Content)
$	@	page-177de2c95b3846c3.js:1
await in $		
q	@	page-177de2c95b3846c3.js:1
e$	@	page-177de2c95b3846c3.js:1
C	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
adicional, en las faturas también debe existir el cliente consumidor final al igual que en proformas
14. en la opción de proformas
14.1. en la ventana de proformas, cuando se esta creando una proforma al momento de agregar ítems y colocar en ingreso manual, si permite registrar dicho producto, pero al igual que en el punto 13.1. el formulario a llenar debe ser el mismo, en la ventana "3 resumen" agrega mas formas de pago que sean "otro con utilización del sistema financiero - transferencia", "otro con utilización del sistema financiero - efectivo" (todos estos datos se encuentran en el archivo @upload/FICHA_TECNICA.md), al momento de crear la proforma aparece este mensaje: Error interno del servidor. Intente nuevamente. y en consola aparece este error: page-177de2c95b3846c3.js:1 
 POST https://conta.tymtechnology.shop/api/v1/proformas 500 (Internal Server Error)
$	@	page-177de2c95b3846c3.js:1
q	@	page-177de2c95b3846c3.js:1
eJ	@	page-177de2c95b3846c3.js:1
L	@	page-177de2c95b3846c3.js:1
i8	@	4bd1b696-c023c6e3521b1417.js:1
(anonymous)	@	4bd1b696-c023c6e3521b1417.js:1
nz	@	4bd1b696-c023c6e3521b1417.js:1
sn	@	4bd1b696-c023c6e3521b1417.js:1
cc	@	4bd1b696-c023c6e3521b1417.js:1
ci	@	4bd1b696-c023c6e3521b1417.js:1
15. en la opción de licencia
15.1 en la ventana de licencia me indica dos recuadros el uno indica el detalle de licencia y el otro el detalle de licencia, lo curioso aquí es que no he comprado ninguna licencia y tampoco tengo las opciones de compra de licencias, otro punto, en detalles de licencia: me indica que el estado es activa, tipo mensual, fecha de expiración: sinlimite, fecha de activación: no disponible, eso quiere decir que no se esta gestionando adecuadamente mi requerimiento de licencias, de igual manera en estado de licencia: me indica que días restantes: si limite. todo esto esta mal ya que vuelvo a repetir se están gestionando mal el licenciamiento. a esto hay que solicitarte dos puntos claves: primero todos los nuevos usuarios deben tener un periodo de prueba del sistema de 15 días, segundo este punto de periodo de prueba también debe agregarse ene le dashboard del panel administrativo para validar que usuarios están en periodo de prueba, también a este periodo en el dashboard permite modificar la cantidad de días. te voy a compartir nuevamente mi solicitud inicial para este punto de licenciamiento para que me ayudes a la creación correcta, tomando encuenta los cambios que te acabo de mencionar:

Genera un licenciamineto anual, mensual, trimenstral, semestral, el cual solo el adminsitrador pueda manipular y dar esas credenciales a los usuarios, una pestaña para un dashboard detallado que indique todos los usuarios y tiempo de vigencia de sus licencias, con opcion para modificar el tiempo del licenciamineto de cada usuario (mensual, trimestral, semestral y anual), Que genere una alerta a cada usuario en el dashboard principal indicando que su licenciamiento esta proximo a caducar, Para los pagos, haz que al momento que el usuario seleccione la opcion se conecte con whatsapp y que llegue con el mensaje de quiero renovar mi licencia por x meses seleccionados, Las opciones de licenciamiento dentro de la pasarela de pagos debe ser mensual, trimestral, semestral, anual. 
16. en la opción de catalogos SRI
16.1 en la ventana de tasas de iva añade también los valores de ice, forma de pago.
16.2 en la ventana de tipo de identificación, completa esa tabla dado que no indica nada en descripción, debo entender por el texto en pantalla que se refiere a: tipo de contribuyente
16.3 añade una nueva ventana llamada: plan de cuentas, donde este también los: códigos de cuentas contables



un error que comparte en general todos los modales que se generan es que cuando los textos que se colocan en los textarea que existen se pierden los botones inferiores dado que no existe un scrollbar aplicado para poder visualizar o no existe algún efecto para que cuando se quite el focus de textarea vuelva al tamaño origial y así no se pierda la información inferior.
para todo lo que tenga que ver con el SRI revisar el documento @upload/FICHA_TECNICA.md, ahí esta detallado todo sobre los valores que deben ir, ruc, iva, ice, adicional cabe recalcar que el iva actual es de el 15% por tal motivo deja esa opción por defecto en todos los campos que se encuentre IVA
si necesitas ver todo el requerimeinto inicial para validar cual era la idea principal del proyecto puedes revisar el archivo @req_ini.md  ​