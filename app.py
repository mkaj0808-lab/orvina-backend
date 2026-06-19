# -*- coding: utf-8 -*-
"""
app.py — الباك إند الرئيسي لموقع أورفينا (ORVINA)
=====================================================
باك إند بسيط جدًا ومرن مبني بـ Flask، مهمته خدمة بيانات الأقسام
والمنتجات لواجهة الموقع، وتوفير نقاط API لإضافة/تعديل/حذف
المواد بسهولة دون الحاجة لتعديل الكود.

تشغيل المشروع:
    pip install -r requirements.txt
    python app.py
سيعمل الخادم على: http://127.0.0.1:5000

جميع البيانات محفوظة في data/categories.json و data/products.json
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import storage

app = Flask(__name__)
CORS(app)  # للسماح للواجهة الأمامية (frontend) بالاتصال بالـ API من أي منفذ


@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "مرحبًا بك في باك إند أورفينا ORVINA 👑",
        "endpoints": [
            "GET  /api/categories",
            "POST /api/categories",
            "DELETE /api/categories/<id>",
            "GET  /api/products",
            "GET  /api/products/<id>",
            "POST /api/products",
            "PUT  /api/products/<id>",
            "DELETE /api/products/<id>",
        ]
    })


# ===================== الأقسام (Categories) =====================

@app.route("/api/categories", methods=["GET"])
def list_categories():
    """إرجاع جميع الأقسام"""
    return jsonify(storage.get_categories())


@app.route("/api/categories", methods=["POST"])
def create_category():
    """
    إضافة قسم جديد. مثال على البيانات المرسلة (JSON):
    { "id": "makeup", "name": "مكياج", "icon": "💋" }
    """
    payload = request.get_json(force=True) or {}
    if not payload.get("id") or not payload.get("name"):
        return jsonify({"error": "الحقول id و name مطلوبة"}), 400

    existing = storage.get_categories()
    if any(c["id"] == payload["id"] for c in existing):
        return jsonify({"error": "هذا القسم موجود مسبقًا"}), 409

    category = {
        "id": payload["id"],
        "name": payload["name"],
        "icon": payload.get("icon", "✦"),
    }
    storage.add_category(category)
    return jsonify(category), 201


@app.route("/api/categories/<category_id>", methods=["DELETE"])
def remove_category(category_id):
    storage.delete_category(category_id)
    return jsonify({"message": "تم حذف القسم بنجاح"})


# ===================== المنتجات (Products) =====================

@app.route("/api/products", methods=["GET"])
def list_products():
    """
    إرجاع جميع المنتجات، مع إمكانية الفلترة:
    /api/products?category=makeup
    /api/products?search=كريم
    """
    products = storage.get_products()

    category = request.args.get("category")
    if category and category != "all":
        products = [p for p in products if p.get("category") == category]

    search = request.args.get("search")
    if search:
        search = search.strip().lower()
        products = [p for p in products if search in p.get("name", "").lower()]

    return jsonify(products)


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    products = storage.get_products()
    product = next((p for p in products if p.get("id") == product_id), None)
    if not product:
        return jsonify({"error": "المنتج غير موجود"}), 404
    return jsonify(product)


@app.route("/api/products", methods=["POST"])
def create_product():
    """
    إضافة منتج جديد بسهولة. مثال على البيانات المرسلة (JSON):
    {
        "name": "كريم أساس فاخر",
        "category": "makeup",
        "price": 35000,
        "old_price": 45000,      (اختياري)
        "rating": 5,             (اختياري، افتراضي 5)
        "image": "https://...",
        "badge": "جديد",         (اختياري)
        "desc": "وصف المنتج"     (اختياري)
    }
    الـ id يُولَّد تلقائيًا، فلا داعي لإرساله.
    """
    payload = request.get_json(force=True) or {}
    required = ["name", "category", "price", "image"]
    missing = [f for f in required if f not in payload]
    if missing:
        return jsonify({"error": f"الحقول التالية مطلوبة: {', '.join(missing)}"}), 400

    product = {
        "name": payload["name"],
        "category": payload["category"],
        "price": payload["price"],
        "old_price": payload.get("old_price"),
        "rating": payload.get("rating", 5),
        "image": payload["image"],
        "badge": payload.get("badge"),
        "desc": payload.get("desc", ""),
    }
    created = storage.add_product(product)
    return jsonify(created), 201


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def edit_product(product_id):
    """تعديل منتج موجود — أرسلي فقط الحقول التي تريدين تغييرها"""
    payload = request.get_json(force=True) or {}
    updated = storage.update_product(product_id, payload)
    if not updated:
        return jsonify({"error": "المنتج غير موجود"}), 404
    return jsonify(updated)


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def remove_product(product_id):
    storage.delete_product(product_id)
    return jsonify({"message": "تم حذف المنتج بنجاح"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
