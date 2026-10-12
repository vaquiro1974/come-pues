"""Genera menu.pdf (vertical 9:16, texto real) a partir de fuente/menu.json."""
import json
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI.parent / "menu.pdf"
LOGO = str(AQUI / "img" / "logo.jpg")
FUENTES = Path("/System/Library/Fonts/Supplemental")

W, H = 360, 640          # equivale a 1080 x 1920 px
MARGEN = 26
FONDO = HexColor("#211a14")
COBRE = HexColor("#d39a6a")
CREMA = HexColor("#f4e6cc")
TENUE = HexColor("#6b4f3a")

pdfmetrics.registerFont(TTFont("Titulo", str(FUENTES / "DIN Condensed Bold.ttf")))
pdfmetrics.registerFont(TTFont("Texto", str(FUENTES / "Georgia.ttf")))
pdfmetrics.registerFont(TTFont("Cursiva", str(FUENTES / "Georgia Italic.ttf")))


def precio(valor):
    return f"${valor}" if valor else None


def partir(texto, fuente, tam, ancho):
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = f"{actual} {palabra}".strip()
        if stringWidth(prueba, fuente, tam) <= ancho:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


def fondo(c):
    c.setFillColor(FONDO)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setStrokeColor(TENUE)
    c.setLineWidth(0.8)
    c.rect(12, 12, W - 24, H - 24, stroke=1, fill=0)


def logo(c, cx, cy, diametro):
    r = diametro / 2
    c.saveState()
    p = c.beginPath()
    p.circle(cx, cy, r * 0.992)
    c.clipPath(p, stroke=0, fill=0)
    c.drawImage(LOGO, cx - r, cy - r, diametro, diametro)
    c.restoreState()


def adorno(c, y, ancho=120):
    c.setStrokeColor(COBRE)
    c.setFillColor(COBRE)
    c.setLineWidth(0.8)
    c.line(W / 2 - ancho / 2, y, W / 2 - 7, y)
    c.line(W / 2 + 7, y, W / 2 + ancho / 2, y)
    c.circle(W / 2, y, 2.2, stroke=0, fill=1)


def separador(c, y):
    c.setStrokeColor(TENUE)
    c.setLineWidth(0.6)
    c.line(MARGEN, y, W - MARGEN, y)


def portada(c, datos):
    fondo(c)
    logo(c, W / 2, 432, 250)
    c.setFillColor(COBRE)
    c.setFont("Titulo", 58)
    c.drawCentredString(W / 2, 232, "MENÚ")
    adorno(c, 218)
    c.setFillColor(CREMA)
    c.setFont("Titulo", 24)
    c.drawCentredString(W / 2, 186, "¡AQUÍ NO SE PASA HAMBRE!")
    c.setFillColor(COBRE)
    c.setFont("Cursiva", 15)
    c.drawCentredString(W / 2, 164, "Bien servido, bien comido")
    separador(c, 132)
    c.setFillColor(COBRE)
    c.setFont("Titulo", 15)
    c.drawCentredString(W / 2, 108, "LLÁMANOS")
    c.setFillColor(CREMA)
    c.setFont("Titulo", 22)
    y = 82
    for tel in datos["telefonos"]:
        c.drawCentredString(W / 2, y, tel)
        ancho = stringWidth(tel, "Titulo", 22)
        c.linkURL("tel:" + tel.replace(" ", ""), (W / 2 - ancho / 2, y - 4, W / 2 + ancho / 2, y + 18))
        y -= 25
    c.showPage()


def encabezado(c, titulo):
    fondo(c)
    logo(c, W / 2, 568, 92)
    c.setFillColor(COBRE)
    c.setFont("Titulo", 44)
    c.drawCentredString(W / 2, 474, titulo.upper())
    adorno(c, 460)
    return 424


def pie(c, datos, pagina, total):
    c.setFillColor(COBRE)
    c.setFont("Cursiva", 11)
    c.drawString(MARGEN, 24, "¡Vení, come pues..!")
    c.setFont("Titulo", 12)
    c.drawRightString(W - MARGEN, 24, f"{pagina} / {total}")


def producto(c, y, numero, item):
    ancho = W - 2 * MARGEN
    nombre = item["nombre"].upper()
    if numero:
        nombre = f"{numero}. {nombre}"
    c.setFillColor(CREMA)
    c.setFont("Titulo", 24)
    c.drawString(MARGEN, y, nombre)
    valor = precio(item.get("precio"))
    if valor:
        c.setFillColor(COBRE)
        c.drawRightString(W - MARGEN, y, valor)
    y -= 21
    if item.get("descripcion"):
        c.setFillColor(CREMA)
        c.setFont("Texto", 13.5)
        for linea in partir(item["descripcion"], "Texto", 13.5, ancho):
            c.drawString(MARGEN, y, linea)
            y -= 18
    if "precios" in item:
        partes = [f"{k} {precio(v)}" if precio(v) else k for k, v in item["precios"].items()]
        c.setFillColor(COBRE)
        c.setFont("Titulo", 16)
        c.drawString(MARGEN, y - 4, "  ·  ".join(partes).upper())
        y -= 22
    return y - 8


def linea_bebida(c, y, item):
    c.setFillColor(CREMA)
    c.setFont("Titulo", 22)
    c.drawString(MARGEN, y, item["nombre"].upper())
    valor = precio(item.get("precio"))
    if valor:
        c.setFillColor(COBRE)
        c.setFont("Titulo", 22)
        c.drawRightString(W - MARGEN, y, valor)
    return y - 30


def jugos(c, y, j):
    c.setFillColor(COBRE)
    c.setFont("Titulo", 26)
    c.drawString(MARGEN, y, j["titulo"].upper())
    y -= 24
    c.setFillColor(CREMA)
    c.setFont("Texto", 13.5)
    c.drawString(MARGEN, y, "Sabores: " + " · ".join(j["sabores"]))
    y -= 30
    col = [W - MARGEN - 78, W - MARGEN]
    con_precio = any(v for fila in j["precios"].values() for v in fila)
    if con_precio:
        c.setFillColor(COBRE)
        c.setFont("Titulo", 16)
        for x, tam in zip(col, j["tamanos"]):
            c.drawRightString(x, y, tam.upper())
        y -= 26
        for etiqueta, fila in j["precios"].items():
            c.setFillColor(CREMA)
            c.setFont("Titulo", 22)
            c.drawString(MARGEN, y, etiqueta.upper())
            c.setFillColor(COBRE)
            c.setFont("Titulo", 20)
            for x, v in zip(col, fila):
                c.drawRightString(x, y, precio(v) or "")
            y -= 27
    else:
        c.setFillColor(COBRE)
        c.setFont("Titulo", 16)
        c.drawString(MARGEN, y, "  ·  ".join(j["precios"]).upper())
        y -= 24
        c.drawString(MARGEN, y, "  ·  ".join(j["tamanos"]).upper())
        y -= 27
    return y


def frase(c, y_superior, lineas):
    centro = (y_superior + 60) / 2
    adorno(c, centro + 40, 80)
    c.setFillColor(CREMA)
    c.setFont("Titulo", 26)
    c.drawCentredString(W / 2, centro, lineas[0].upper())
    c.setFillColor(COBRE)
    c.setFont("Cursiva", 15)
    c.drawCentredString(W / 2, centro - 24, lineas[1])


def main():
    datos = json.loads((AQUI / "menu.json").read_text(encoding="utf-8"))
    c = canvas.Canvas(str(SALIDA), pagesize=(W, H))
    c.setTitle(f"{datos['restaurante']} | Menú")
    c.setAuthor(datos["restaurante"])
    total = len(datos["categorias"]) + 1
    portada(c, datos)
    for n, cat in enumerate(datos["categorias"], start=2):
        y = encabezado(c, cat["titulo"])
        numerar = cat.get("numerar", True)
        for i, item in enumerate(cat["productos"], start=1):
            if numerar:
                y = producto(c, y, i, item)
                separador(c, y + 4)
                y -= 26
            else:
                y = linea_bebida(c, y, item)
        if "jugos" in cat:
            separador(c, y + 12)
            y = jugos(c, y - 22, cat["jugos"])
        if "frase" in cat and y > 200:
            frase(c, y, cat["frase"])
        pie(c, datos, n, total)
        c.showPage()
    c.save()
    print(f"{SALIDA.name}: {total} páginas, {SALIDA.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
