from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configuración de conexión
ODOO_URL = "https://fontanasrl.odoo.com"
ODOO_DB = "marjorie82-fontana-srl-fontana-1087170"
ODOO_USER = "admin"
ODOO_PASS = "@Fontana$2025@"

# Obtener sesión válida
def get_session_id():
    url = f"{ODOO_URL}/web/session/authenticate"
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "db": ODOO_DB,
            "login": ODOO_USER,
            "password": ODOO_PASS
        }
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        session_id = response.cookies.get("session_id")
        if not session_id:
            raise ValueError("No se pudo obtener session_id.")
        return session_id
    except Exception as e:
        raise RuntimeError(f"Error al autenticar en Odoo: {e}")

# Consulta genérica a un modelo
def query_odoo_model(model, offset, limit):
    session_id = get_session_id()
    url = f"{ODOO_URL}/web/dataset/call_kw/{model}/search_read"

    headers = {
        "Content-Type": "application/json",
        "Cookie": f"session_id={session_id}"
    }

    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": model,
            "method": "search_read",
            "args": [[]],
            "kwargs": {
                "offset": offset,
                "limit": limit
            }
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()

    if "error" in data:
        raise RuntimeError(f"Error de Odoo: {data['error']}")

    return data.get("result", [])

# Ruta para stock.warehouse.orderpoint
@app.route("/stock_warehouse_orderpoint", methods=["GET"])
def get_stock_warehouse_orderpoint():
    try:
        offset = int(request.args.get("offset", 0))
        limit = int(request.args.get("limit", 500))

        results = query_odoo_model("stock.warehouse.orderpoint", offset, limit)
        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ejecutar app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)