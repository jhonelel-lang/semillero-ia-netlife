import os
import sys
import warnings
from datetime import datetime

# --- IMPORTACIÓN DE LIBRERÍAS ---
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.agents import initialize_agent, AgentType, Tool
    from langchain.memory import ConversationBufferMemory
except ImportError:
    print("❌ ERROR: Faltan librerías.")
    print("Ejecuta: pip install langchain langchain-google-genai google-generativeai langchain-community")
    sys.exit()

# Silenciar advertencias de depreciación de LangChain para limpiar la consola
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ==========================================
# 1. BASE DE DATOS SIMULADA
# ==========================================

CLIENTES = {
    "0912345678": {"nombre": "Carlos Mendieta", "ciudad": "Guayaquil", "region": "Costa"},
    "1712345678": {"nombre": "Andrea Castillo", "ciudad": "Quito", "region": "Sierra"},
    "0102030405": {"nombre": "Jorge Viteri", "ciudad": "Cuenca", "region": "Sierra"},
    "1309876543": {"nombre": "Luisa Parraga", "ciudad": "Manta", "region": "Costa"},
    "0705432109": {"nombre": "Roberto Noboa", "ciudad": "Machala", "region": "Costa"},
}

ESTADO_FINANCIERO = {
    "0912345678": {"producto": "Tarjeta de Crédito Black", "deuda_total": 4500.50, "dias_mora": 45, "limite_credito": 5000},
    "1712345678": {"producto": "Préstamo Personal", "deuda_total": 1200.00, "dias_mora": 15, "limite_credito": 3000},
    "0102030405": {"producto": "Crédito Automotriz", "deuda_total": 8500.75, "dias_mora": 90, "limite_credito": 15000},
    "1309876543": {"producto": "Microcrédito", "deuda_total": 350.25, "dias_mora": 5, "limite_credito": 1000},
    "0705432109": {"producto": "Tarjeta Clásica", "deuda_total": 980.00, "dias_mora": 60, "limite_credito": 1200}
}

CANALES_PAGO = {
    "Tarjeta de Crédito": ["App Móvil", "Web Bancaria", "Débito Automático"],
    "Préstamo Personal": ["Ventanilla Banco", "Corresponsales No Bancarios", "Transferencia"],
    "Crédito Automotriz": ["Ventanilla Banco", "Transferencia Interbancaria"]
}

PROMESAS_DB = {}
PROMESA_COUNTER = 2000

# ==========================================
# 2. FUNCIONES DE NEGOCIO (TOOLS)
# ==========================================

def consultar_estado_cuenta(cedula: str = "") -> str:
    """Consulta el estado financiero detallado."""
    if cedula not in CLIENTES:
        return f"❌ No se encontró ningún cliente con la cédula: {cedula}"
    
    info_personal = CLIENTES[cedula]
    info_financiera = ESTADO_FINANCIERO.get(cedula, {})
    
    return (f"📊 ESTADO DE CUENTA - {cedula}:\n"
            f"👤 Cliente: {info_personal['nombre']}\n"
            f"📍 Ubicación: {info_personal['ciudad']}, {info_personal['region']}\n"
            f"💳 Producto: {info_financiera['producto']}\n"
            f"💰 Deuda Total: ${info_financiera['deuda_total']}\n"
            f"📅 Días en Mora: {info_financiera['dias_mora']} días\n"
            f"📉 Límite Crédito: ${info_financiera['limite_credito']}")

def registrar_promesa_pago(cedula: str, fecha: str, monto: float) -> str:
    """Registra una promesa de pago."""
    global PROMESA_COUNTER
    if cedula not in CLIENTES:
        return f"❌ Error: La cédula {cedula} no existe."

    id_transaccion = str(PROMESA_COUNTER)
    PROMESAS_DB[id_transaccion] = {
        "cedula_cliente": cedula,
        "nombre": CLIENTES[cedula]['nombre'],
        "fecha_compromiso": fecha,
        "monto_acordado": monto,
        "estado": "PENDIENTE"
    }
    PROMESA_COUNTER += 1
    
    saldo = ESTADO_FINANCIERO[cedula]['deuda_total']
    return (f"📝 CONFIRMACIÓN EXITOSA (Ticket {id_transaccion}):\n"
            f"✅ Cliente: {CLIENTES[cedula]['nombre']} se compromete a pagar ${monto} el {fecha}.\n"
            f"📉 Saldo Deuda: ${saldo}\n"
            f"ℹ️ El pago se reflejará en 24 horas.")

def consultar_historial_promesas(cedula: str = "") -> str:
    """Consulta promesas previas."""
    if cedula not in CLIENTES: return "❌ Cliente no encontrado."
    
    encontradas = []
    for ticket, datos in PROMESAS_DB.items():
        if datos["cedula_cliente"] == cedula:
            encontradas.append(f"🔖 #{ticket}: ${datos['monto_acordado']} para el {datos['fecha_compromiso']} ({datos['estado']})")
    
    if encontradas:
        return f"📜 HISTORIAL DE {CLIENTES[cedula]['nombre']}:\n" + "\n".join(encontradas)
    return "ℹ️ No tiene promesas registradas."

def validar_oferta_negociacion(cedula: str, oferta: float) -> str:
    """Valida reglas de negocio (Mínimo 10%)."""
    if cedula not in ESTADO_FINANCIERO: return "❌ Cliente no encontrado."
    
    deuda = ESTADO_FINANCIERO[cedula]['deuda_total']
    minimo = deuda * 0.10
    
    res = f"🧮 ANÁLISIS (${oferta} vs Deuda ${deuda}):\n"
    if oferta >= deuda:
        return res + "✅ ACEPTADO: Cancelación Total. ¡Proceder!"
    elif oferta >= minimo:
        return res + "✅ ACEPTADO: Abono Parcial válido."
    else:
        faltante = minimo - oferta
        return res + f"⚠️ INSUFICIENTE: El mínimo es ${minimo:.2f} (10%). Faltan ${faltante:.2f}."

def consultar_medios_pago(cedula: str) -> str:
    """Muestra dónde pagar según el producto."""
    if cedula not in ESTADO_FINANCIERO: return "❌ Cliente no encontrado."
    
    producto = ESTADO_FINANCIERO[cedula]['producto']
    canales = ["Ventanilla", "App"] # Default
    
    for k, v in CANALES_PAGO.items():
        if k in producto:
            canales = v
            break
            
    lista = "\n".join([f"- {c}" for c in canales])
    return f"💳 PAGOS PARA {producto}:\n{lista}\nℹ️ Referencia: Cédula {cedula}"

def verificar_identidad_cliente(cedula: str, ciudad_input: str) -> str:
    """Valida identidad por ciudad."""
    if cedula not in CLIENTES: return "❌ Cédula no existe."
    
    real = CLIENTES[cedula]['ciudad'].lower()
    if ciudad_input.strip().lower() == real:
        return "✅ IDENTIDAD VERIFICADA. Acceso a datos sensible AUTORIZADO."
    return f"⛔ ACCESO DENEGADO. La ciudad '{ciudad_input}' no coincide."

def calcular_proyeccion_cuotas(cedula: str, meses: int) -> str:
    """Tabla de amortización simple."""
    if cedula not in ESTADO_FINANCIERO: return "❌ Cliente no encontrado."
    if meses not in [3, 6, 12, 24]: return "⚠️ Solo plazos de 3, 6, 12 o 24 meses."
    
    deuda = ESTADO_FINANCIERO[cedula]['deuda_total']
    recargo = deuda * 0.05 # 5% recargo
    total = deuda + recargo
    cuota = total / meses
    
    return (f"🧮 SIMULACIÓN {meses} MESES:\n"
            f"💰 Deuda Base: ${deuda}\n"
            f"📈 Recargo: ${recargo:.2f}\n"
            f"💵 CUOTA MENSUAL: ${cuota:.2f}\n"
            f"¿Desea activar este plan?")

# --- ADAPTADORES PARA LANGCHAIN (STRING A ARGUMENTOS) ---
def adapter_registrar(inp):
    try: c, f, m = inp.split("|"); return registrar_promesa_pago(c.strip(), f.strip(), float(m))
    except: return "❌ Error formato. Usa: cedula|fecha|monto"

def adapter_validar(inp):
    try: c, m = inp.split("|"); return validar_oferta_negociacion(c.strip(), float(m))
    except: return "❌ Error formato. Usa: cedula|monto"

def adapter_identidad(inp):
    try: c, ci = inp.split("|"); return verificar_identidad_cliente(c.strip(), ci.strip())
    except: return "❌ Error formato. Usa: cedula|ciudad"

def adapter_cuotas(inp):
    try: c, m = inp.split("|"); return calcular_proyeccion_cuotas(c.strip(), int(m))
    except: return "❌ Error formato. Usa: cedula|meses"

# LISTA DE HERRAMIENTAS
mis_tools = [
    Tool(name="ConsultarEstadoCuenta", func=consultar_estado_cuenta, description="Consulta deuda y datos. Input: cedula"),
    Tool(name="RegistrarPromesaPago", func=adapter_registrar, description="Registra acuerdo. Input: cedula|fecha|monto"),
    Tool(name="ConsultarHistorialPromesas", func=consultar_historial_promesas, description="Ver historial. Input: cedula"),
    Tool(name="ValidarOfertaNegociacion", func=adapter_validar, description="Evaluar oferta. Input: cedula|monto"),
    Tool(name="ConsultarMediosPago", func=consultar_medios_pago, description="Donde pagar. Input: cedula"),
    Tool(name="VerificarIdentidadCliente", func=adapter_identidad, description="Seguridad ciudad. Input: cedula|ciudad"),
    Tool(name="CalcularProyeccionCuotas", func=adapter_cuotas, description="Refinanciar. Input: cedula|meses")
]

# ==========================================
# 3. CONFIGURACIÓN DEL AGENTE Y BUCLE PRINCIPAL
# ==========================================

# Memoria Global
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
agent_executor = None

def inicializar_agente_con_key(api_key):
    """Crea o recrea el agente con una nueva API Key, preservando la memoria."""
    global agent_executor, memory
    
    os.environ["GOOGLE_API_KEY"] = api_key
    
    # Configuramos LLM 
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0,
        convert_system_message_to_human=True # <--- ¡IMPORTANTE PARA EVITAR ERRORES!
    )
    
    agent_executor = initialize_agent(
        tools=mis_tools,
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory, # Se pasa la memoria existente
        verbose=True,
        handle_parsing_errors=True,
        agent_kwargs={
            "system_message": """
            Eres 'El Enjambre IA', experto en cobranzas. 
            Identifica al cliente, valida seguridad si pide datos sensibles (VerificarIdentidadCliente),
            negocia empáticamente (ValidarOfertaNegociacion) y cierra acuerdos (RegistrarPromesaPago).
            Si te faltan datos, pídelos.
            """
        }
    )
    return True

def main():
    print("\n" + "="*60)
    print("      🐝 EL ENJAMBRE IA - SISTEMA DE COBRANZAS v2.0      ")
    print("      Comandos: 'salir' para cerrar | 'cambiar key' para rotar API")
    print("="*60)

    # 1. Solicitar API Key inicial
    while True:
        key = input("\n🔑 Ingresa tu GOOGLE API KEY para iniciar: ").strip()
        if key:
            try:
                inicializar_agente_con_key(key)
                print("✅ Sistema Iniciado. ¡Hola! Soy tu asistente de cobranzas.")
                break
            except Exception as e:
                print(f"❌ Error al iniciar: {e}")
        else:
            print("⚠️ La API Key no puede estar vacía.")

    # 2. Bucle de Conversación
    while True:
        try:
            user_input = input("\n👤 Tú: ").strip()
            
            if not user_input: continue
            
            # --- COMANDO DE SALIDA ---
            if user_input.lower() in ["salir", "exit", "chao"]:
                print("👋 ¡Hasta luego!")
                break
            
            # --- COMANDO DE CAMBIO DE KEY EN CALIENTE ---
            if user_input.lower() == "cambiar key":
                nueva_key = input("🔑 NUEVA API Key: ").strip()
                if nueva_key:
                    inicializar_agente_con_key(nueva_key)
                    print("🔄 Credenciales actualizadas. Memoria intacta. Continúa hablando...")
                continue

            # --- EJECUCIÓN DEL AGENTE ---
            response = agent_executor.invoke({"input": user_input})
            print(f"\n🤖 Agente: {response['output']}")
            print("-" * 60)

        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ OCURRIÓ UN ERROR: {error_msg}")
            
            # Detección automática de error de cuota
            if "429" in error_msg or "ResourceExhausted" in error_msg or "quota" in error_msg.lower():
                print("\n⚠️ ¡ALERTA! Tu API Key se ha quedado sin cuota.")
                print("👉 Escribe 'cambiar key' y presiona Enter para poner una nueva sin cerrar.")

if __name__ == "__main__":
    main()