from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle
import os

def generar_pdf(actividad, lista_participantes):
    filename = f"actividad_{actividad.id}.pdf"
    filepath = os.path.join("pdfs", filename)
    os.makedirs("pdfs", exist_ok=True)

    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    # Colores y estilo
    color_marco = colors.HexColor("#5b9bd5")
    color_fondo_titulo = colors.HexColor("#f2f2f2")
    color_titulo = colors.HexColor("#003366")
    fuente_base = "Helvetica"
    fuente_negrita = "Helvetica-Bold"

    # --- Dibujo del marco decorativo ---
    def dibujar_marco():
        c.setStrokeColor(color_marco)
        c.setLineWidth(4)
        c.rect(40, 40, width - 80, height - 80)

    x_margin = 60
    y_start = height - 60
    y = y_start

    def cabecera():
        nonlocal y
        c.setFillColor(color_fondo_titulo)
        c.rect(40, height - 80, width - 80, 60, fill=1, stroke=0)

        logo_path = os.path.join("static", "img", "logo_ies.jpg")
        logo_width = 1 * inch
        logo_height = 1 * inch

        if os.path.exists(logo_path):
            c.drawImage(logo_path, x_margin, height - 60, width=logo_width, height=logo_height, mask='auto')

        c.setFont(fuente_negrita, 16)
        c.setFillColor(color_titulo)
        c.drawString(x_margin + logo_width + 10, height - 40, "I.E.S Puerta del Mar – Almuñécar")
        y = height - 100

        c.setFont(fuente_negrita, 14)
        c.setFillColor(colors.black)
        c.drawCentredString(width / 2, y, "INFORME DE ACTIVIDAD EXTRAESCOLAR")
        y -= 30

    dibujar_marco()
    cabecera()
    c.setFont(fuente_base, 12)

    def dibujar_linea(etiqueta, contenido="", salto=20, negrita=False):
        nonlocal y
        if y < 100:
            c.showPage()
            dibujar_marco()
            y = y_start
            cabecera()
            c.setFont(fuente_base, 12)

        if negrita:
            c.setFont(fuente_negrita, 12)
        c.drawString(x_margin, y, f"{etiqueta}: {contenido}")
        y -= salto
        if negrita:
            c.setFont(fuente_base, 12)

    # Datos del formulario
    dibujar_linea("Nombre de la actividad", actividad.nombre, negrita=True)
    dibujar_linea("Fecha", str(actividad.fecha))
    dibujar_linea("Hora de inicio", str(actividad.hora_inicio))
    dibujar_linea("Hora de fin", str(actividad.hora_fin))

    if hasattr(actividad, "departamentos") and actividad.departamentos:
        nombres_departamentos = ", ".join(d.nombre for d in actividad.departamentos)
        dibujar_linea("Departamentos responsables", nombres_departamentos)

    dibujar_linea("Descripción", actividad.descripcion, salto=30)
    dibujar_linea("Observaciones", actividad.observaciones, salto=30)

    # --- Procesar lista de participantes sin duplicados ---
    participantes_por_grupo = {}
    alumnos_unicos = {}
    for p in lista_participantes:
        alumno = p.alumno
        if alumno and hasattr(alumno, "id"):
            alumnos_unicos[alumno.id] = p

    for p in alumnos_unicos.values():
        alumno = p.alumno
        nombre = f"{alumno.nombre} {getattr(alumno, 'apellido', '')}".strip()
        grupo = getattr(alumno, 'grupo', None)
        grupo_id = getattr(grupo, 'id', 0)
        grupo_nombre = getattr(grupo, 'nombre', 'Sin grupo')
        curso_nombre = getattr(grupo.curso, 'nombre', '') if grupo and grupo.curso else ''

        if grupo_id not in participantes_por_grupo:
            participantes_por_grupo[grupo_id] = {
                "nombre": grupo_nombre,
                "curso": curso_nombre,
                "asisten": {},
                "no_asisten": {}
            }

        grupo_info = participantes_por_grupo[grupo_id]
        if getattr(p, 'asistira', 0) == 1:
            grupo_info["asisten"][alumno.id] = nombre
            grupo_info["no_asisten"].pop(alumno.id, None)
        else:
            grupo_info["no_asisten"][alumno.id] = nombre
            grupo_info["asisten"].pop(alumno.id, None)

    def dibujar_tabla(titulo, participantes_dict):
        nonlocal y
        if not participantes_dict:
            return

        participantes = sorted(participantes_dict.values())
        data = [["Nº", "Nombre del Alumno"]]
        for i, nombre in enumerate(participantes):
            data.append([str(i + 1), nombre])

        colWidths = [30, 430] if len(participantes) <= 30 else [30, 400]
        fontSize = 10 if len(participantes) <= 30 else 9

        c.setFont(fuente_negrita, 12)
        dibujar_linea(titulo, salto=25)
        c.setFont(fuente_base, fontSize)

        table = Table(data, colWidths=colWidths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ddeeff") if "asiste" in titulo.lower() else colors.HexColor("#ffe5e5")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), fuente_negrita),
            ('FONTSIZE', (0, 0), (-1, -1), fontSize),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ]))

        table_height = 18 * len(data) + 10
        if y - table_height < 100:
            c.showPage()
            dibujar_marco()
            y = y_start
            cabecera()
            c.setFont(fuente_base, 12)

        table.wrapOn(c, width, height)
        table.drawOn(c, x_margin, y - table_height)
        y -= table_height + 30

    for grupo_id, grupo_info in participantes_por_grupo.items():
        curso = grupo_info["curso"]
        grupo = grupo_info["nombre"]
        if grupo_info["asisten"]:
            dibujar_tabla(f"Asistentes de {curso} {grupo}", grupo_info["asisten"])
        if grupo_info["no_asisten"]:
            dibujar_tabla(f"No asistentes de {curso} {grupo}", grupo_info["no_asisten"])

    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.grey)
    c.drawCentredString(width / 2, 45, "Documento generado automáticamente – I.E.S Puerta del Mar")

    c.save()
    return filepath
