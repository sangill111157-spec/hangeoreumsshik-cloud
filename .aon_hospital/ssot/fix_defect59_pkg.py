# -*- coding: utf-8 -*-
import sys, os, subprocess, json, urllib.request, time

backend_dir = r'C:\trading\package\nvda_trading_system\backend'
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# 1. Inspect package namespace & paths (결함 59)
print("==================================================")
print("1. [결함 59] Package Namespace & Paths Inspection")
print("==================================================")
import app
import app.services
import app.services.master_signal

print("app.__file__                   :", getattr(app, "__file__", None))
print("list(app.__path__)             :", list(getattr(app, "__path__", [])))
print("app.services.__file__          :", getattr(app.services, "__file__", None))
print("list(app.services.__path__)    :", list(getattr(app.services, "__path__", [])))
print("master_signal.__file__         :", getattr(app.services.master_signal, "__file__", None))

# Check if __init__.py exists
app_init = os.path.join(backend_dir, 'app', '__init__.py')
services_init = os.path.join(backend_dir, 'app', 'services', '__init__.py')
print("app/__init__.py exists         :", os.path.exists(app_init))
print("services/__init__.py exists    :", os.path.exists(services_init))

if not os.path.exists(app_init):
    with open(app_init, 'w', encoding='utf-8') as f:
        f.write('# Explicit app package init\n')
    print("Created app/__init__.py")

if not os.path.exists(services_init):
    with open(services_init, 'w', encoding='utf-8') as f:
        f.write('# Explicit app.services package init\n')
    print("Created app/services/__init__.py")

