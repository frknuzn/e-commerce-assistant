from fastapi import FastAPI, HTTPException  # FastAPI framework'ü ve HTTP hataları için exception sınıfı
from pydantic import BaseModel  # Veri doğrulama ve serialization için model sınıfı
from typing import List, Optional  # Liste ve opsiyonel parametreler için typing modülü

# FastAPI uygulamasını başlatıyoruz, Swagger'da gözükecek başlık bilgisi
app = FastAPI(title="Dummy E-Ticaret API")


# --------- Veri Modelleri ve Sahte Veriler (Mock Data) ----------

# Ürün varyantı: renk, beden ve stok bilgisi
class Variant(BaseModel):
    color: str
    size: str
    inventory: int
    image_url: str


# Ürün modeli: id, başlık ve varyantların listesi
class Product(BaseModel):
    id: int
    title: str
    variants: List[Variant]


# Sipariş modeli: sipariş numarası, durumu ve tahmini teslim tarihi (ETA)
class Order(BaseModel):
    number: str
    status: str
    eta: str


# Sahte ürün verileri: Bellekte tutulan sabit bir envanter
INVENTORY: List[Product] = [
    Product(
        id=1,
        title="Sneaker X",
        variants=[
            Variant(color="beyaz", size="41", inventory=12,
                    image_url="https://d5e14a.a-cdn.akinoncloud.com/products/2024/01/05/1133958/6fa3a676-de6c-4d81-9eff-951d9a893656.jpg"),
            Variant(color="beyaz", size="42", inventory=5,
                    image_url="https://d5e14a.a-cdn.akinoncloud.com/products/2024/01/05/1133958/6fa3a676-de6c-4d81-9eff-951d9a893656.jpg"),
            Variant(color="siyah", size="42", inventory=7,
                    image_url="https://d5e14a.a-cdn.akinoncloud.com/products/2024/06/13/839241/d99bc743-65e8-4c4a-bc6b-8e11f9ee9385.jpg"),
        ],
    ),
    Product(
        id=2,
        title="Classic T-Shirt",
        variants=[
            Variant(color="siyah", size="M", inventory=24,
                    image_url="https://witcdn.sarar.com/o-yaka-eiffel-takim-tasarim-siyah-tisort-16432-robin-yayla-x-sarar-kapsul-koleksiyonu-sarar-42887-16-B.jpg"),
            Variant(color="beyaz", size="L", inventory=0,
                    image_url="https://silkandcashmere.com/cdn/shop/files/Beyaz-Saf-Pamuk-Marc-Yuvarlak-Yaka-Erkek-Basic-Tiort-Silk-and-Cashmere-1690528021940.jpg?v=1741181393"),
        ],
    ),
]

# Sahte sipariş verileri: Sipariş numarası, durum ve tahmini teslimat tarihi
ORDERS: List[Order] = [
    Order(number="1007", status="Kargoya verildi", eta="2025-06-12"),
    Order(number="1012", status="Hazırlanıyor", eta="2025-06-15"),
]


# ---------------------------------------------------------------

# Belirli bir siparişi sipariş numarası ile sorgulama
@app.get("/orders/{order_number}", response_model=Order)
def get_order(order_number: str):
    # Sipariş listesinde eşleşen numara aranır
    for o in ORDERS:
        if o.number == order_number:
            return o  # Eşleşme varsa sipariş bilgisi döner

    # Hiçbir sipariş bulunamazsa 404 hatası fırlatılır
    raise HTTPException(status_code=404, detail="Sipariş bulunamadı")


# Envanterde ürün arama endpoint'i
@app.get("/inventory", response_model=List[Product])
def search_inventory(q: str, color: Optional[str] = None, size: Optional[str] = None):
    results = []  # Sonuç listesi

    for p in INVENTORY:
        # Ürün başlığı küçük harfe çevrilir ve "-" karakterleri boşlukla değiştirilir
        title = p.title.lower().replace("-", " ")

        # Arama sorgusu kelimelere bölünür
        query_words = q.lower().replace("-", " ").split()

        # Eğer başlık içinde aranan kelimelerden hiçbiri yoksa devam et (ürünü atla)
        if not any(word in title for word in query_words):
            continue

        # Renk ve beden filtrelemesi yapılır (None olanlar filtreye dahil edilmez)
        filtered_variants = [
            v for v in p.variants
            if (color is None or v.color.lower() == color.lower())
               and (size is None or v.size == size)
        ]

        # Eğer eşleşen varyant varsa, bu varyantlarla birlikte ürünü sonuca ekle
        # variants'ları dict'e çevirerek image_url dahil her şeyi garanti et
        p_dict = p.dict()
        p_dict["variants"] = [v.dict() for v in filtered_variants]  # Bu satırı değiştir
        results.append(Product(**p_dict))
    # Tekrar Product objesi olarak ekle

    # Hiçbir ürün bulunamazsa 404 hatası dön
    if not results:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    # Eşleşen ürünler JSON olarak döndürülür
    return results
