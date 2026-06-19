# -*- coding: utf-8 -*-
"""
storage.py
وحدة بسيطة لقراءة وكتابة بيانات الأقسام والمنتجات من/إلى ملفات JSON.
هذا يجعل إضافة أو تعديل المواد سهلاً جدًا: كل البيانات في ملفين JSON
يمكن تعديلهما يدويًا، أو عبر نقاط API الموجودة في app.py
"""
import json
import os
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")

_lock = threading.Lock()  # لمنع تعارض الكتابة المتزامنة على الملف


def _read(path):
    with _lock:
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


def _write(path, data):
    with _lock:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------- الأقسام ----------------
def get_categories():
    return _read(CATEGORIES_FILE)


def save_categories(categories):
    _write(CATEGORIES_FILE, categories)


def add_category(category):
    categories = get_categories()
    categories.append(category)
    save_categories(categories)
    return category


def delete_category(category_id):
    categories = [c for c in get_categories() if c.get("id") != category_id]
    save_categories(categories)


# ---------------- المنتجات ----------------
def get_products():
    return _read(PRODUCTS_FILE)


def save_products(products):
    _write(PRODUCTS_FILE, products)


def add_product(product):
    products = get_products()
    next_id = max([p.get("id", 0) for p in products], default=0) + 1
    product["id"] = next_id
    products.append(product)
    save_products(products)
    return product


def update_product(product_id, updates):
    products = get_products()
    for p in products:
        if p.get("id") == product_id:
            p.update(updates)
            save_products(products)
            return p
    return None


def delete_product(product_id):
    products = [p for p in get_products() if p.get("id") != product_id]
    save_products(products)
