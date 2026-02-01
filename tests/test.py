import os
import warnings
from datetime import datetime

# Librerías de IA
from langchain.agents import initialize_agent, AgentType, Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory

# --- 1. CONFIGURACIÓN INICIAL ---
# Silenciar advertencias rojas
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ⚠️ PON TU API KEY AQUÍ PARA EMPEZAR
# (Si se quema, podrás cambiarla escribiendo "cambiar key" en el chat)
os.environ["GOOGLE_API_KEY"] = "AIzaSyCWWYwz_SDgwZxiVm7ddH5Pj02eKbZ0-qU"

# --- 2. BASE DE DATOS SIMULADA (TU FUENTE DE VERDAD) ---
CLIENTES_DB = {
    "0912345678": {"nombre": "Carlos Mendieta", "deuda": 4500.50, "dias_mora": 120, "producto": "Tarjeta Black", "ciudad": "Guayaquil"},
    "1712345678": {"nombre": "Andrea Castillo", "deuda": 1200.00, "dias_mora": 45, "producto": "Préstamo Personal", "ciudad": "Quito"},
    "0705432109": {"nombre": "Roberto Noboa",   "deuda": 200.00,  "dias_mora": 15,  "producto": "Plan Celular",     "ciudad": "Machala"},
    "1309876543": {"nombre": "Luisa Parraga",   "deuda": 350.25,  "dias_mora": 90,  "producto": "Crédito Directo",  "ciudad": "Manta"}
}

PROMESAS_DB = {}   # Aquí se guardarán los acuerdos
PROMESA_COUNTER = 2000

# --- 3. LAS HERRAMIENTAS (TUS 7 FUNCIONES) ---

def consultar_estado_cuenta(cedula: str):
    """Consulta saldo, mora y producto dado un número de cédula."""
    cedula = cedula.strip()
    cliente = CLIENTES_DB.get(cedula)
    if cliente:
        return f"✅ CLIENTE ENCONTRADO:\n- Nombre: {cliente['nombre']}\n- Deuda Total: ${cliente['deuda']}\n- Días Mora: {cliente['dias_mora']}\n- Producto: {cliente['producto']}"
    return "❌ Cliente no encontrado en la base de datos."

def verificar_identidad(input_str: str):
    """Valida identidad. Input formato: 'CEDULA|CIUDAD_CONFIRMACION'."""
    try:
        parts = input_str.split("|")
        if len(parts) != 2: return "⚠️ Error: Formato debe ser 'CEDULA|CIUDAD'"
        cedula, ciudad_input = parts[0].strip(), parts[1].strip().lower()
        
        cliente = CLIENTES_DB.get(cedula)
        if not cliente: return "❌ Cédula no existe."
        
        if cliente["ciudad"].lower() == ciudad_input:
            return f"✅ IDENTIDAD VERIFICADA. El cliente reside en {cliente['ciudad']}. Acceso concedido."
        else:
            return f"⛔ ACCESO DENEGADO. La ciudad '{ciudad_input}' no coincide con nuestros registros."
    except Exception as e:
        return f"Error de validación: {e}"

def validar_oferta(input_str: str):
    """Valida si una oferta es aceptable. Input: 'CEDULA|MONTO_OFERTADO'."""
    try:
        parts = input_str.split("|")
        cedula, oferta = parts[0].strip(), float(parts[1].strip())
        
        cliente = CLIENTES_DB.get(cedula)
        if not cliente: return "❌ Cliente no encontrado."
        
        deuda = cliente['deuda']
        minimo = deuda * 0.10  # Política: Mínimo 10%
        
        if oferta >= deuda:
            return "🌟 EXCELENTE: La oferta cubre el total de la deuda."
        elif oferta >= minimo:
            return f"✅ ACEPTABLE: La oferta de ${oferta} es válida para un abono (Mínimo requerido: ${minimo:.2f})."
        else:
            return f"❌ INSUFICIENTE: La oferta es muy baja. El mínimo para negociar es ${minimo:.2f} (10% de la deuda)."
    except:
        return "⚠️ Error: Formato debe ser 'CEDULA|MONTO'"

def calcular_cuotas(input_str: str):
    """Calcula tabla de amortización. Input: 'CEDULA|MESES' (3, 6, 12)."""
    try:
        parts = input_str.split("|")
        cedula, meses = parts[0].strip(), int(parts[1].strip())
        
        cliente = CLIENTES_DB.get(cedula)
        if not cliente: return "❌ Cliente no encontrado."
        
        tasa_mensual = 0.015 # 1.5% mensual
        deuda = cliente['deuda']
        recargo = deuda * tasa_mensual * meses
        total_final = deuda + recargo
        cuota = total_final / meses
        
        return (f"📊 SIMULACIÓN A {meses} MESES:\n"
                f"- Deuda Inicial: ${deuda}\n"
                f"- Recargo Financiero: ${recargo:.2f}\n"
                f"- Total a Pagar: ${total_final:.2f}\n"
                f"- CUOTA MENSUAL: ${cuota:.2f}")
    except:
        return "⚠️ Error: Formato 'CEDULA|MESES'"

def registrar_promesa(input_str: str):
    """Guarda el acuerdo. Input: 'CEDULA|FECHA|MONTO'."""
    global PROMESA_COUNTER
    try:
        parts = input_str.split("|")
        if len(parts) < 3: return "⚠️ Faltan datos. Requerido: CEDULA|FECHA|MONTO"
        
        cedula, fecha, monto = parts[0].strip(), parts[1].strip(), parts[2].strip()
        
        PROMESA_COUNTER += 1
        ticket = f"T-{PROMESA_COUNTER}"
        
        PROMESAS_DB[ticket] = {
            "cedula": cedula,
            "fecha_pago": fecha,
            "monto": monto,
            "estado": "PENDIENTE",
            "timestamp": str(datetime.now())
        }
        return f"✅ TRANSACCIÓN EXITOSA. Ticket generado: {ticket}. Cliente se compromete a pagar ${monto} el {fecha}."
    except Exception as e:
        return f"Error al guardar: {e}"

def consultar_historial(cedula: str):
    """Busca promesas previas de un cliente."""
    encontradas = []
    for ticket, datos in PROMESAS_DB.items():
        if datos["cedula"] == cedula:
            encontradas.append(f"{ticket}: ${datos['monto']} para el {datos['fecha_pago']} ({datos['estado']})")
    
    if encontradas:
        return "📂 HISTORIAL ENCONTRADO:\n" + "\n".join(encontradas)
    return "ℹ️ Este cliente no tiene promesas de pago registradas aún."

def consultar_medios_pago(cedula: str):
    """Indica dónde pagar según el producto."""
    cliente = CLIENTES_DB.get(cedula)
    if not cliente: return "❌ Cliente no encontrado."
    
    producto = cliente['producto'].lower()
    if "tarjeta" in producto:
        return "💳 MEDIOS PARA TARJETA: App Banca Móvil, Web Bancaria (Opción 'Pagar Tarjeta'), Débito Automático."
    elif "vehículo" in producto or "auto" in producto:
        return "🚗 MEDIOS PARA AUTO: Ventanilla Banco, Transferencia Interbancaria con referencia PLACA."
    else:
        return "💰 MEDIOS GENERALES: Western Union, Red Activa, Ventanilla de Servicio al Cliente."

# Definición de Tools para LangChain
mis_tools = [
    Tool(name="ConsultarEstadoCuenta", func=consultar_estado_cuenta, description="Usa esta herramienta cuando necesites saber la deuda, mora o datos generales. Input: Cédula."),
    Tool(name="VerificarIdentidadCliente", func=verificar_identidad, description="OBLIGATORIO si el usuario pide datos sensibles. Valida la ciudad. Input: 'CEDULA|CIUDAD'."),
    Tool(name="ValidarOfertaNegociacion", func=validar_oferta, description="Úsala cuando el cliente ofrezca un monto para pagar. Input: 'CEDULA|MONTO'."),
    Tool(name="CalcularProyeccionCuotas", func=calcular_cuotas, description="Úsala si piden diferir, plazos o cuotas. Input: 'CEDULA|MESES' (ej: 3, 6, 12)."),
    Tool(name="RegistrarPromesaPago", func=registrar_promesa, description="Úsala AL FINAL, cuando el cliente confirme fecha y monto. Input: 'CEDULA|FECHA|MONTO'."),
    Tool(name="ConsultarHistorialPromesas", func=consultar_historial, description="Úsala si preguntan si ya está registrado su pago o promesas anteriores. Input: Cédula."),
    Tool(name="ConsultarMediosPago", func=consultar_medios_pago, description="Úsala cuando pregunten DÓNDE o CÓMO pagar. Input: Cédula.")
]

# --- 4. CEREBRO Y MEMORIA ---
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Inicializamos el LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    convert_system_message_to_human=True
)


# Inicializamos el Agente
agent = initialize_agent(
    tools=mis_tools,
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True, # Muestra el pensamiento en colores
    handle_parsing_errors=True,
    agent_kwargs={
        "system_message": """
        Eres 'El Enjambre IA', un experto en cobranzas empático pero firme.
        TU OBJETIVO: Negociar el pago de deudas.
        
        REGLAS ORO:
        1. Siempre identifica al cliente primero (ConsultarEstadoCuenta).
        2. Si pide datos privados, valida su ciudad (VerificarIdentidadCliente).
        3. Para registrar pagos, necesitas SIEMPRE fecha y monto.
        4. Si una herramienta pide input compuesto ('|'), constrúyelo correctamente.
        """
    }
)

# --- 5. INTERFAZ DE CONSOLA (MAIN LOOP) ---
def iniciar_chat():
    print("\n" + "="*60)
    print("      🐝 EL ENJAMBRE IA - SISTEMA DE COBRANZAS v1.0      ")
    print("      (Escribe 'salir' para cerrar)")
    print("      (Escribe 'cambiar key' si tienes error de cuota)")
    print("="*60)
    
    # Saludo inicial automático
    print("\n🤖 Agente: ¡Hola! Soy tu asistente virtual de cobranzas. Por favor indícame tu número de cédula para comenzar.")

    while True:
        try:
            user_input = input("\n👤 Tú: ").strip()

            if user_input.lower() in ["salir", "exit", "chau"]:
                print("👋 ¡Hasta luego!")
                break
            
            # --- TRUCO: CAMBIAR API KEY EN CALIENTE ---
            if user_input.lower() == "cambiar key":
                nueva_key = input("🔑 Ingresa la NUEVA API Key: ").strip()
                os.environ["GOOGLE_API_KEY"] = nueva_key
                # Reconstruimos el agente con la nueva llave pero la MISMA memoria
                print("🔄 Actualizando credenciales...")
                nuevo_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, convert_system_message_to_human=True)
                global agent # Usamos la variable global
                agent = initialize_agent(
                    tools=mis_tools,
                    llm=nuevo_llm,
                    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                    memory=memory, # ¡Memoria intacta!
                    verbose=True,
                    handle_parsing_errors=True,
                    agent_kwargs={"system_message": "Eres 'El Enjambre IA'..."}
                )
                print("✅ Key Actualizada. Puedes continuar hablando.")
                continue
            # ------------------------------------------

            if not user_input: continue

            # Ejecución del Agente
            response = agent.invoke({"input": user_input})
            print(f"\n🤖 Agente: {response['output']}")
            print("-" * 60)

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            if "429" in str(e) or "quota" in str(e).lower():
                print("⚠️ PARECE QUE TU API KEY SE QUEMÓ.")
                print("   👉 Escribe 'cambiar key' para poner una nueva sin cerrar el programa.")

if __name__ == "__main__":
    iniciar_chat()