# ⚡ AveríasOEM — Motor Nocturno de Códigos de Error y Repuestos OEM

Sistema automatizado que genera y publica cada madrugada páginas técnicas hiper-específicas (`[Marca + Modelo + Código de Error] -> [Referencia Exacta de Pieza OEM]`) monetizadas con enlaces de afiliado directos a la pieza de recambio (Amazon Afiliados, eBay Partner Network y AliExpress) y un feed JSON estructurado (`dist/api/errors.json`).

---

## 💰 Paso Único para que el dinero vaya a TU cuenta (2 minutos)

Yo (la IA) ya he construido el motor, la base de datos inicial de códigos OEM, el generador web SEO con Schema.org (`FAQPage` + `HowTo`) y la tarea nocturna programada. Como no puedo abrir una cuenta bancaria a tu nombre, solo tienes que cambiar tu identificador en [`config.json`](./config.json):

1. Abre [`config.json`](./config.json).
2. Cambia `"amazon_tag": "averiasoem-21"` por tu ID de **Amazon Afiliados** (se crea gratis en [afiliados.amazon.es](https://afiliados.amazon.es/) o [affiliate-program.amazon.com](https://affiliate-program.amazon.com/)).
3. *(Opcional)* Cambia `"ebay_campid"` por tu ID de campaña de [eBay Partner Network](https://partnernetwork.ebay.com/).

---

## 🌐 Cómo publicarlo gratis en Internet (Coste: $0/mes)

El repositorio ya incluye [`.github/workflows/nightly-deploy.yml`](./.github/workflows/nightly-deploy.yml):

1. Sube esta carpeta a un repositorio gratuito de GitHub (`git remote add origin https://github.com/TU_USUARIO/oem-error-engine.git && git push -u origin main`).
2. En tu repositorio de GitHub, ve a **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3.*(Opcional)* En **Settings → Secrets and variables → Actions**, añade `GEMINI_API_KEY` (con una clave gratuita de Google AI Studio) para que GitHub genere fichas infinitas en la nube incluso con tu ordenador apagado.

---

## 🌙 Cómo funciona mientras duermes

* **En tu Mac (vía Antigravity Schedule a las 03:00 AM):** Cada madrugada el agente despierta a las 03:00 AM, investiga nuevos códigos de avería y sus referencias de pieza OEM reales, actualiza `data/errors_db.json`, ejecuta `python3 nightly_generator.py` y reconstruye todo el portal en `dist/`.
* **En la nube (vía GitHub Actions a las 03:00 UTC):** Ejecuta `nightly_generator.py` y publica las nuevas páginas directamente en GitHub Pages.
