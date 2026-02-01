# 🐝 El Enjambre IA - Agente Virtual de Cobranzas

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![LangChain](https://img.shields.io/badge/LangChain-Orchestration-green?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-orange?style=for-the-badge)

Este repositorio contiene el código fuente y documentación de un Agente Inteligente diseñado para automatizar la gestión de cartera vencida, permitiendo la negociación de deudas y el registro de promesas de pago mediante lenguaje natural.

---

## 👥 Integrantes

| Rol | Nombre Completo | Cédula | GitHub |
| :--- | :--- | :--- | :--- |
| **Líder** | **Jhon Andres Espinoza Vargas** | 0950958728 | [@jhonelel-lang](https://github.com/jhonelel-lang) |
| Integrante | Elvis Anthony Ayala Yagual | 0924951585 | [@usuario](https://github.com/) |
| Integrante | José Francisco Lucas Zambrano | 0957617319 | [@usuario](https://github.com/) |
| Integrante | Steven Andrés Vargas Arias | 0951971761 | [@usuario](https://github.com/) |
| Integrante | Bryan David Villa Jara | 0950021717 | [@usuario](https://github.com/) |
| Integrante | Jhon Jairo Chalen Baquerizo | 0955784327 | [@usuario](https://github.com/) |

---

## 🎥 Video Demostrativo

> **[HAZ CLIC AQUÍ PARA VER EL VIDEO DEL PROYECTO EN YOUTUBE]**
> *(https://youtu.be/RnAjwD7POwk)*

---

## 📄 Descripción del Agente

"El Enjambre IA" es un asistente virtual conversacional basado en el modelo **Google Gemini 1.5 Flash**. Su objetivo es resolver la ineficiencia en los procesos tradicionales de cobranza, ofreciendo una alternativa empática, disponible 24/7 y segura.

El agente no solo conversa, sino que actúa: tiene capacidad para acceder a bases de datos simuladas, realizar cálculos financieros y escribir registros de compromiso de pago, todo respetando reglas de negocio estrictas (como montos mínimos de negociación).

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

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/jhonelel-lang/semillero-ia-netlife.git
   cd semillero-ia-netlife
   cd src

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
