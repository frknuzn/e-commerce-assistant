import os
import httpx
import logging
import json
from mcp.server.fastmcp import FastMCP  # MCP altyapısı için FastMCP sınıfı

# 🔹 Log yapılandırması yapılır (INFO seviyesinde)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔹 MCP sunucusu başlatılıyor, bu bir agent kaydı anlamına gelir
mcp = FastMCP("E-commerce")
logger.info("🟢 MCP E-commerce agent başlatıldı")

# 🔹 Backend API'nin base URL'i .env.example.example üzerinden alınır, yoksa localhost kullanılır
BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

# 🔹 Sipariş durumu sorgulama aracı (tool)
@mcp.tool()
def get_order_status(order_number: str) -> str:
    logger.info(f"📥 get_order_status çağrıldı: {order_number}")

    # Sipariş detayını REST API üzerinden çeker
    r = httpx.get(f"{BASE}/orders/{order_number}", timeout=5)

    # Sipariş bulunamazsa özel mesaj dön
    if r.status_code == 404:
        return "🚫 Sipariş bulunamadı."

    # Diğer hatalarda exception fırlatılır
    r.raise_for_status()

    # JSON olarak yanıt alınır
    o = r.json()

    # Yanıt metni hazırlanır
    msg = f"Sipariş #{o['number']} durumu: {o['status']}. Tahmini teslim: {o['eta']}."
    logger.info(f"📤 Yanıt: {msg}")

    return msg

# 🔹 Ürün arama aracı (tool)
@mcp.tool()
def search_inventory(query: str,
                     color: str | None = None,
                     size: str | None = None) -> list[dict]:
    logger.info(f"📥 search_inventory çağrıldı: query={query}, color={color}, size={size}")

    params = {"q": query}
    if color:
        params["color"] = color
    if size:
        params["size"] = size

    r = httpx.get(f"{BASE}/inventory", params=params, timeout=5)

    if r.status_code == 404:
        return []

    r.raise_for_status()
    prods = r.json()

    logger.info(f"📤 JSON olarak {len(prods)} ürün döndürüldü")
    return prods


# 🔹 Uygulama terminal üzerinden stdio ile başlatılır
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("🟢 MCP E-commerce agent başlatıldı")
    mcp.run(transport='stdio')  # Claude ya da başka bir ortamla stdio üzerinden çalışmak için
