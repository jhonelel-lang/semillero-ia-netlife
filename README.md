# 🐝 El Enjambre IA - Agente Virtual de Cobranzas

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![LangChain](https://img.shields.io/badge/LangChain-Orchestration-green?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-orange?style=for-the-badge)

> **Sistema inteligente de negociación de deuda y gestión de cartera basado en Modelos de Lenguaje (LLMs).**

Este proyecto implementa un Agente ReAct (Reasoning + Acting) capaz de interactuar con clientes morosos, validar su identidad, negociar acuerdos de pago basándose en reglas de negocio y registrar promesas en tiempo real.

---

## 🚀 Características Principales

* **🧠 Modelo Avanzado:** Utiliza **Google Gemini 2.5 Flash** para respuestas rápidas y razonamiento lógico.
* **🛡️ Validación de Identidad:** Implementa un "Firewall Lógico" que impide revelar datos sensibles (deuda, días de mora) hasta que el usuario confirma su ciudad de residencia.
* **🤝 Negociación Autónoma:** Evalúa ofertas económicas. El agente tiene autonomía para aceptar ofertas si cubren al menos el **10% de la deuda**.
* **🔄 Cambio de API Key en Caliente:** Sistema de resiliencia que permite cambiar la credencial de Google en tiempo de ejecución (runtime) sin perder la memoria de la conversación (ideal para límites de cuota).
* **💾 Persistencia de Memoria:** Mantiene el contexto de la charla usando `ConversationBufferMemory`.

---

## 🛠️ Arquitectura y Herramientas (Tools)

El agente cuenta con las siguientes herramientas conectadas a una base de datos simulada:

1.  `ConsultarEstadoCuenta`: Obtiene saldo, producto y días de mora.
2.  `VerificarIdentidadCliente`: Valida (MFA simulado) ciudad vs. cédula.
3.  `ValidarOfertaNegociacion`: Lógica financiera para aprobar/rechazar montos.
4.  `CalcularProyeccionCuotas`: Genera tablas de amortización simples.
5.  `RegistrarPromesaPago`: Guarda el acuerdo final (Fecha + Monto).
6.  `ConsultarHistorialPromesas`: Verifica acuerdos previos.

---

## 📋 Requisitos de Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/TU_USUARIO/TU_REPO.git](https://github.com/TU_USUARIO/TU_REPO.git)
    cd TU_REPO
    ```

2.  **Crear un entorno virtual (Opcional pero recomendado):**
    ```bash
    python -m venv venv
    # En Windows:
    venv\Scripts\activate
    # En Mac/Linux:
    source venv/bin/activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar API Key:**
    Necesitarás una API Key de [Google AI Studio](https://aistudio.google.com/). Al ejecutar el programa, te la solicitará.

---

## ▶️ Ejecución

Para iniciar el agente, ejecuta el script principal desde la consola:

```bash
python main.py
