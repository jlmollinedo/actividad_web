from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime, date, timedelta
import os
from functools import wraps
from config import Config
from extensions import db
from config import Config
from models import Actividad, Departamento, Grupo, Alumno, Participacion, Profesorado
from flask_login import login_user
from models import Profesorado
from extensions import db, login_manager
from models import Actividad
from flask import jsonify
from werkzeug.security import check_password_hash
from sqlalchemy.orm import joinedload
from flask import request, session
from flask_login import login_user
from werkzeug.security import check_password_hash
from datetime import datetime
from sqlalchemy.orm import joinedload

app = Flask(__name__)
app.config.from_object(Config)
login_manager.init_app(app)

db.init_app(app)
mail = Mail(app)
mail.init_app(app)

actividad_departamentos = db.Table('actividad_departamentos',
    db.Column('actividad_id', db.Integer, db.ForeignKey('actividades.id')),
    db.Column('departamento_id', db.Integer, db.ForeignKey('departamentos.id'))
)
from flask_login import current_user

from flask_login import current_user
from flask import flash, redirect, url_for
from functools import wraps

def rol_requerido(rol):
    def decorador(f):
        @wraps(f)
        def decorado(*args, **kwargs):
            print(f"[DEBUG] current_user.is_authenticated = {current_user.is_authenticated}")
            print(f"[DEBUG] current_user.rol = {getattr(current_user, 'rol', None)}")
            if not current_user.is_authenticated or current_user.rol != rol:
                flash("No tienes permiso para acceder a esta funcionalidad.", "success")
                return redirect(url_for('calendario'))
            return f(*args, **kwargs)
        return decorado
    return decorador

from fpdf import FPDF
import os

from fpdf import FPDF
import os

from fpdf import FPDF
import os
from collections import defaultdict

from fpdf import FPDF
import os
from collections import defaultdict

def generar_pdf(actividad, participaciones, profesorado=None, profesor_nombre=None):
    from collections import defaultdict
    import os
    from fpdf import FPDF

    class PDF(FPDF):
        def __init__(self):
            super().__init__()
            self.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
            self.add_font("DejaVu", "B", "fonts/DejaVuSans-Bold.ttf", uni=True)
            self.add_font("DejaVu", "I", "fonts/DejaVuSans-Oblique.ttf", uni=True)
            self.set_font("DejaVu", "", 12)
            self.set_auto_page_break(auto=True, margin=15)

        def header(self):
            self.set_fill_color(33, 150, 243)  # Azul profesional
            self.rect(10, 10, 190, 10, 'F')
            self.set_text_color(255, 255, 255)
            self.set_font("DejaVu", "B", 12)
            self.set_y(10)
            self.cell(0, 10, "I.E.S Puerta del Mar – Almuñécar", align="C", ln=True)
            self.set_text_color(0, 0, 0)
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font("DejaVu", "I", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, "Documento generado automáticamente – I.E.S Puerta del Mar", align="C")

        def encabezado_actividad(self):
            self.set_font("DejaVu", "B", 14)
            self.set_text_color(0, 102, 204)
            self.cell(0, 10, "INFORME DE ACTIVIDAD EXTRAESCOLAR", ln=True, align="C")
            self.set_text_color(0, 0, 0)
            self.ln(5)

            def campo(label, valor, multiline=False):
                self.set_font("DejaVu", "B", 12)
                self.set_x(self.l_margin)
                self.cell(0, 8, f"{label}:", ln=1)
                self.set_font("DejaVu", "", 12)
                self.set_x(self.l_margin)
                if multiline:
                    self.multi_cell(0, 8, valor)
                else:
                    self.cell(0, 8, valor, ln=1)

            campo("Nombre de la actividad", actividad.nombre, multiline=True)
            campo("Fecha", actividad.fecha.strftime('%d/%m/%Y'))
            campo("Hora de inicio", actividad.hora_inicio.strftime('%H:%M'))
            campo("Hora de fin", actividad.hora_fin.strftime('%H:%M'))

            departamentos = ', '.join(d.nombre for d in actividad.departamentos) or '—'
            campo("Departamentos responsables", departamentos, multiline=True)

            # Aquí mostramos el profesorado responsable que se recibe como argumento
            if profesorado and len(profesorado) > 0:
                nombres_profes = ', '.join(f"{p.nombre} {p.apellido}" for p in profesorado)
                campo("Profesorado responsable participante", nombres_profes, multiline=True)
            else:
                campo("Profesorado responsable participante", "—")

            desc = (actividad.descripcion or '—').replace('\r', ' ').replace('\n', ' ').strip()
            campo("Descripción", desc, multiline=True)

            obs = (actividad.observaciones or '—').replace('\r', ' ').replace('\n', ' ').strip()
            campo("Observaciones", obs, multiline=True)

            self.ln(5)

        def tabla_grupo(self, titulo, alumnos):
            self.set_font("DejaVu", "B", 12)
            self.set_fill_color(200, 230, 255)
            self.cell(0, 10, titulo, ln=True, fill=True)

            self.set_font("DejaVu", "B", 10)
            self.set_fill_color(240, 240, 240)
            self.cell(10, 8, "Nº", 1, 0, 'C', fill=True)
            self.cell(0, 8, "Nombre del Alumno", 1, 1, 'C', fill=True)

            self.set_font("DejaVu", "", 10)
            for i, alumno in enumerate(alumnos, start=1):
                nombre = f"{alumno.alumno.nombre} {alumno.alumno.apellido}"
                self.cell(10, 8, str(i), 1, 0, 'C')
                self.cell(0, 8, nombre, 1, 1)

            self.ln(5)

    grupos_asistentes = defaultdict(list)
    grupos_no_asistentes = defaultdict(list)

    for p in participaciones:
        grupo = f"{p.alumno.grupo.curso.nombre} {p.alumno.grupo.nombre}" if p.alumno.grupo and p.alumno.grupo.curso else "Sin grupo"
        if p.asistira:
            grupos_asistentes[grupo].append(p)
        else:
            grupos_no_asistentes[grupo].append(p)

    pdf = PDF()
    pdf.add_page()
    pdf.encabezado_actividad()

    for grupo, alumnos in grupos_asistentes.items():
        pdf.tabla_grupo(f"Asistentes de {grupo}:", alumnos)

    for grupo, alumnos in grupos_no_asistentes.items():
        pdf.tabla_grupo(f"No asistentes de {grupo}:", alumnos)

    # Aseguramos que la carpeta existe
    os.makedirs("pdfs", exist_ok=True)
    output_path = os.path.join("pdfs", f"actividad_{actividad.id}.pdf")

    pdf.output(output_path)
    return output_path

from flask import send_from_directory

@app.route('/pdfs/<filename>')
def pdfs(filename):
    return send_from_directory('pdfs', filename)

@login_manager.user_loader
def load_user(user_id):
    return Profesorado.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('calendario'))

@app.route('/calendario')
def calendario():
    rol = session.get('rol')
    actividades = Actividad.query.order_by(Actividad.fecha).all()  # Todas ordenadas por fecha
    return render_template('calendario.html', rol=rol)
@app.route('/logout')
def logout():
    session.clear()  # o lo que uses para cerrar sesión
    flash('Has cerrado sesión.', "success")
    return redirect(url_for('calendario'))


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@rol_requerido('profesor')
def editar_actividad(id):
    actividad = Actividad.query.get_or_404(id)

    def parse_time(s):
        for fmt in ('%H:%M:%S', '%H:%M'):
            try:
                return datetime.strptime(s, fmt).time()
            except ValueError:
                pass
        raise ValueError(f"Formato de hora no válido: {s}")

    if request.method == 'POST':
        actividad.nombre = request.form['nombre']
        actividad.descripcion = request.form.get('descripcion', '')
        actividad.observaciones = request.form.get('observaciones', '')
        actividad.fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
        actividad.hora_inicio = parse_time(request.form['hora_inicio'])
        actividad.hora_fin = parse_time(request.form['hora_fin'])

        # Actualizar departamentos
        departamento_ids = request.form.getlist('departamentos_ids[]')
        actividad.departamentos = Departamento.query.filter(Departamento.id.in_(departamento_ids)).all()
        
        # Actualizar profesorado responsable
        profesores_ids_form = list(map(int, request.form.getlist('profesores_ids[]')))
        profesores_seleccionados = Profesorado.query.filter(Profesorado.id.in_(profesores_ids_form)).all()
        actividad.profesores = profesores_seleccionados
        
        # Actualizar grupos seleccionados
        grupos_ids_seleccionados = set(map(int, request.form.getlist('grupos[]')))
        grupos_actuales_ids = set(g.id for g in actividad.obtener_grupos())

        if grupos_ids_seleccionados != grupos_actuales_ids:
            # Borrar participaciones de grupos que ya no están
            participaciones_a_borrar = Participacion.query.filter(
                Participacion.actividad_id == actividad.id,
                Participacion.grupo_id.notin_(grupos_ids_seleccionados)
            ).all()
            for p in participaciones_a_borrar:
                db.session.delete(p)

            # Añadir participaciones para alumnos de los nuevos grupos
            grupos_nuevos_ids = grupos_ids_seleccionados - grupos_actuales_ids
            if grupos_nuevos_ids:
                alumnos_nuevos = Alumno.query.filter(Alumno.grupo_id.in_(grupos_nuevos_ids)).all()
                for alumno in alumnos_nuevos:
                    existe = Participacion.query.filter_by(
                        actividad_id=actividad.id, alumno_id=alumno.id).first()
                    if not existe:
                        nueva_participacion = Participacion(
                            actividad_id=actividad.id,
                            alumno_id=alumno.id,
                            grupo_id=alumno.grupo_id,
                            asistira=0
                        )
                        db.session.add(nueva_participacion)

        # Actualizar asistencia
        alumnos_ids_marcados = set(map(int, request.form.getlist('alumnos_participantes[]')))
        participaciones = Participacion.query.filter_by(actividad_id=actividad.id).all()
        for p in participaciones:
            p.asistira = 1 if p.alumno_id in alumnos_ids_marcados else 0

        db.session.commit()

        # Construir el nombre completo del profesor editor
        profesor_editor = f"{current_user.nombre} {current_user.apellido}"

        # Generar PDF
        participantes = Participacion.query.filter_by(actividad_id=actividad.id).all()
        pdf_path = None
        try:
            db.session.refresh(actividad)  # ← Aseguramos que se recargue la relación
            _ = actividad.profesores       # ← Forzamos la carga de profesorado
            #pdf_path = generar_pdf(actividad, participantes, profesor_nombre=profesor_editor)
            print("Profesores pasados a generar_pdf:", [f"{p.nombre} {p.apellido}" for p in actividad.profesores])
            pdf_path = generar_pdf(actividad, participantes, profesorado=actividad.profesores, profesor_nombre=profesor_editor)
            if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
                print("❌ Error: El archivo PDF no se generó o está vacío:", pdf_path)
                pdf_path = None
            else:
                print("✅ PDF generado correctamente:", pdf_path)
        except Exception as e:
            print("❌ Error al generar el PDF:", e)
            pdf_path = None

        # Enviar correo
        try:
            msg = Message(
                subject=f"Actividad modificada: {actividad.nombre}",
                recipients=['jlmollinedo@gmail.com'],
                #body=f"La actividad '{actividad.nombre}' ha sido modificada para el día {actividad.fecha.strftime('%d/%m/%Y')}."
                body=f"La actividad '{actividad.nombre}' ha sido modificada para el día {actividad.fecha.strftime('%d/%m/%Y')} por {profesor_editor}."

            )
            if pdf_path:
                with app.open_resource(pdf_path) as pdf_file:
                    msg.attach(f"actividad_{actividad.id}.pdf", "application/pdf", pdf_file.read())
            mail.send(msg)
            print("✅ Correo enviado correctamente.")
        except Exception as e:
            print("❌ Error al enviar el correo:", e)

        return redirect(url_for('calendario'))

    # GET: cargar datos para formulario
    departamentos = Departamento.query.all()
    grupos = Grupo.query.options(joinedload(Grupo.curso)).all()

    participaciones = Participacion.query.filter_by(actividad_id=actividad.id).all()
    alumnos_existentes = {p.alumno_id: p.alumno for p in participaciones}

    # Obtener grupos y departamentos seleccionados
    grupos_seleccionados = list(set(p.grupo_id for p in participaciones))
    departamentos_ids_seleccionados = [d.id for d in actividad.departamentos]
    profesores_ids_seleccionados = [p.id for p in actividad.profesores]
    alumnos_participantes_ids = [p.alumno_id for p in participaciones if p.asistira == 1]

    # Añadir alumnos de todos los grupos disponibles (para filtrado JS en el cliente)
    alumnos_extra = Alumno.query.filter(Alumno.grupo_id.in_([g.id for g in grupos])).all()
    for alumno in alumnos_extra:
        if alumno.id not in alumnos_existentes:
            alumnos_existentes[alumno.id] = alumno

    alumnos = list(alumnos_existentes.values())

    hora_inicio_str = actividad.hora_inicio.strftime('%H:%M') if actividad.hora_inicio else ''
    hora_fin_str = actividad.hora_fin.strftime('%H:%M') if actividad.hora_fin else ''

    return render_template(
        'formulario.html',
        actividad=actividad,
        departamentos=departamentos,
        grupos=grupos,
        alumnos=alumnos,
        departamentos_ids_seleccionados=departamentos_ids_seleccionados,
        grupos_seleccionados=grupos_seleccionados,
        alumnos_participantes_ids=alumnos_participantes_ids,
        fecha=actividad.fecha,
        hora_inicio_str=hora_inicio_str,
        hora_fin_str=hora_fin_str,
        profesores_ids_seleccionados=profesores_ids_seleccionados  # <-- Añadir esto
    )

from flask_login import login_user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        contrasena = request.form.get('contrasena')

        if not email or not contrasena:
            flash("Por favor, introduce email y contraseña.")
            return redirect(url_for('login'))

        usuario = Profesorado.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.contrasena, contrasena):
            login_user(usuario)  # <--- Aquí logueas con Flask-Login
            session['rol'] = 'profesor'  # Opcional, si usas session para otros fines
            flash("Has iniciado sesión correctamente.", "success")
            return redirect(url_for('calendario'))
        else:
            flash("Email o contraseña incorrectos.")
            return redirect(url_for('login'))

    return render_template('login.html')

from flask import current_app
import smtplib

@app.route('/api/actividad/<int:id>/mover', methods=['POST'])
@rol_requerido('profesor')
def mover_actividad(id):
    print("🔄 Petición recibida para mover actividad.")

    actividad = Actividad.query.get_or_404(id)

    try:
        data = request.get_json()
        print("📦 Datos recibidos:", data)
    except Exception as e:
        print("❌ Error al obtener JSON:", e)
        traceback.print_exc()
        return jsonify({'error': 'No se pudo leer el JSON'}), 400

    nueva_fecha_str = data.get('fecha') if data else None
    if not nueva_fecha_str:
        print("⚠️ Fecha no proporcionada.")
        return jsonify({'error': 'Fecha no proporcionada'}), 400

    try:
        nueva_fecha = datetime.strptime(nueva_fecha_str, '%Y-%m-%d').date()
    except ValueError:
        print("⚠️ Fecha inválida:", nueva_fecha_str)
        return jsonify({'error': 'Fecha inválida'}), 400

    actividad.fecha = nueva_fecha
    db.session.commit()
    print("✅ Fecha de actividad actualizada a:", nueva_fecha)

    try:
        participantes = Participacion.query.filter_by(actividad_id=actividad.id).options(
            joinedload(Participacion.alumno).joinedload(Alumno.grupo).joinedload(Grupo.curso)
        ).all()
        print(f"👥 Participaciones cargadas: {len(participantes)}")
    except Exception as e:
        print("❌ Error al cargar participaciones:", e)
        traceback.print_exc()
        return jsonify({'error': 'Error al cargar participantes'}), 500

    try:
        print("📝 Generando PDF...")
        profesorado = actividad.profesores  # Aquí aseguramos pasar el profesorado responsable
        print("👨‍🏫 Profesores responsables a pasar al PDF:")
        for p in profesorado:
            print(f"- {p.nombre} {p.apellido}")

        pdf_path = generar_pdf(actividad, participantes, profesorado=profesorado)

        if not os.path.exists(pdf_path):
            print("❌ PDF no encontrado en:", pdf_path)
            return jsonify({'error': 'PDF no encontrado'}), 500
        print(f"✅ PDF generado en {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
    except Exception as e:
        print("❌ Error al generar el PDF:", e)
        traceback.print_exc()
        return jsonify({'error': 'Error al generar el PDF'}), 500

    profesor_editor = f"{current_user.nombre} {current_user.apellido}"
    print("📛 Profesor actual:", profesor_editor)

    try:
        print("📧 Enviando correo...")

        # Activar depuración SMTP
        smtplib.SMTP.debuglevel = 1

        msg = Message(
            subject=f"Actividad reprogramada: {actividad.nombre}",
            recipients=['jlmollinedo@gmail.com'],
            body=f"La actividad '{actividad.nombre}' ha sido reprogramada para el día {actividad.fecha.strftime('%d/%m/%Y')} por {profesor_editor}."
        )

        with app.open_resource(pdf_path) as pdf_file:
            msg.attach(f"actividad_{actividad.id}.pdf", "application/pdf", pdf_file.read())

        with current_app.app_context():
            mail.send(msg)

        print("✅ Correo enviado correctamente.")
    except smtplib.SMTPServerDisconnected as e:
        print("❌ Desconexión inesperada del servidor SMTP:", e)
    except Exception as e:
        print("❌ Error inesperado al enviar el correo:", e)
        traceback.print_exc()
        return jsonify({'error': 'Error al enviar el correo'}), 500

    return jsonify({'success': True})


@app.route('/api/actividades')
def api_actividades():
    rol = session.get('rol')

    if rol == 'profesor':
        actividades = Actividad.query.all()
    else:
        actividades = Actividad.query.all()

    eventos = []
    for act in actividades:
        eventos.append({
            'id': act.id,
            'title': act.nombre,
            'start': act.fecha.isoformat(),
        })

    print("Eventos devueltos:", eventos)  # Para ver en consola servidor qué devuelve

    return jsonify(eventos)

def parse_time(s):
    for fmt in ('%H:%M:%S', '%H:%M'):
        try:
            return datetime.strptime(s, fmt).time()
        except ValueError:
            pass
    raise ValueError(f"Formato de hora no válido: {s}")

from dateutil import parser as dateparser
from datetime import datetime, timedelta

from flask import request, render_template, redirect, url_for, flash
from datetime import datetime, date, timedelta
from dateutil import parser as dateutil_parser
from zoneinfo import ZoneInfo

from flask import request, render_template, redirect, url_for, flash
from datetime import datetime, date, timedelta
from dateutil import parser as dateutil_parser
from zoneinfo import ZoneInfo

import pytz
from dateutil import parser as dateutil_parser
from datetime import datetime, date, timedelta

from datetime import datetime, timedelta, date
from flask import request, render_template, redirect, url_for, flash
import pytz
import re
import os
from flask_mail import Message

import re
import pytz
from datetime import datetime, timedelta, date
from flask import request, render_template, redirect, url_for, flash
from flask_mail import Message
from sqlalchemy.orm import joinedload
import os

def extraer_fecha_hora(fecha_str):
    if not fecha_str:
        return None, '', ''

    try:
        tz = pytz.timezone("Europe/Madrid")

        # Regex para extraer partes: fecha, hora, zona horaria
        m = re.match(
            r'(\d{4}-\d{2}-\d{2})'               # fecha
            r'(?:T(\d{2}):(\d{2}):(\d{2}))?'    # hora opcional
            r'([+-]\d{2}:\d{2}|Z)?',             # zona horaria opcional
            fecha_str
        )
        if not m:
            raise ValueError("Formato no reconocido")

        fecha_part = m.group(1)   # 2025-05-22
        h = m.group(2)            # hora '06' o None
        mi = m.group(3)           # minuto '00' o None
        s = m.group(4)            # segundo '00' o None
        tz_str = m.group(5)       # '+02:00' o 'Z' o None

        fecha = datetime.strptime(fecha_part, '%Y-%m-%d').date()

        if h is None:
            # Solo fecha, sin horas
            return fecha, '', ''

        # Construimos datetime naive
        dt_naive = datetime(
            int(fecha_part[0:4]), int(fecha_part[5:7]), int(fecha_part[8:10]),
            int(h), int(mi), int(s)
        )

        # Procesamos zona horaria
        if tz_str == 'Z':
            dt_utc = dt_naive.replace(tzinfo=pytz.utc)
            dt_local = dt_utc.astimezone(tz)
        elif tz_str is None:
            # Sin zona, asumimos hora local
            dt_local = tz.localize(dt_naive)
        else:
            # tz_str ejemplo '+02:00' o '-05:30'
            signo = 1 if tz_str[0] == '+' else -1
            offset_h = int(tz_str[1:3])
            offset_m = int(tz_str[4:6])
            total_offset_min = signo * (offset_h * 60 + offset_m)
            tzinfo_custom = pytz.FixedOffset(total_offset_min)
            dt_with_tz = dt_naive.replace(tzinfo=tzinfo_custom)
            dt_local = dt_with_tz.astimezone(tz)

        hora_inicio = dt_local.strftime('%H:%M')
        hora_fin = (dt_local + timedelta(minutes=30)).strftime('%H:%M')

        return fecha, hora_inicio, hora_fin

    except Exception as e:
        print(f"❌ Error al interpretar la fecha: {fecha_str} → {e}")
        return None, '', ''


@app.route('/actividad/nueva', methods=['GET', 'POST'])
@rol_requerido('profesor')
def nueva_actividad():
    fecha_str = request.args.get('fecha')
    fecha, hora_inicio_str, hora_fin_str = extraer_fecha_hora(fecha_str)

    if fecha is None:
        fecha = date.today()
        hora_inicio_str = ''
        hora_fin_str = ''

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form.get('descripcion', '')
        observaciones = request.form.get('observaciones', '')
        fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
        hora_inicio = datetime.strptime(request.form['hora_inicio'], '%H:%M').time()
        hora_fin = datetime.strptime(request.form['hora_fin'], '%H:%M').time()
        departamento_ids = request.form.getlist('departamentos_ids[]')
        grupos_ids = request.form.getlist('grupos[]')
        alumnos_ids_marcados = [x.strip() for x in request.form.getlist('alumnos_participantes[]')]
        profesores_ids = request.form.getlist('profesores_ids[]')  # NUEVO: recoger profesores seleccionados

        actividad = Actividad(
            nombre=nombre,
            descripcion=descripcion,
            observaciones=observaciones,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin
        )
        actividad.departamentos = Departamento.query.filter(Departamento.id.in_(departamento_ids)).all()

        # Guardar profesores seleccionados (asumiendo relación muchos a muchos)
        if profesores_ids:
            actividad.profesores = Profesorado.query.filter(Profesorado.id.in_(profesores_ids)).all()
        else:
            actividad.profesores = []

        db.session.add(actividad)
        db.session.commit()

        alumnos_en_grupos = Alumno.query.filter(Alumno.grupo_id.in_(grupos_ids)).all()
        alumnos_insertados = set()

        for alumno in alumnos_en_grupos:
            if alumno.id in alumnos_insertados:
                continue
            alumnos_insertados.add(alumno.id)

            asistira = 1 if str(alumno.id) in alumnos_ids_marcados else 0

            participacion = Participacion(
                actividad_id=actividad.id,
                grupo_id=alumno.grupo_id,
                alumno_id=alumno.id,
                asistira=asistira
            )
            db.session.add(participacion)

        db.session.commit()

        participantes = Participacion.query.filter_by(actividad_id=actividad.id).all()

        # Construir el nombre completo del profesor creador
        profesor_creador = f"{current_user.nombre} {current_user.apellido}"
        profesorado_responsable = actividad.profesores  # profesores seleccionados en el formulario



        try:
            # Pasar el nombre del profesor creador a la función generar_pdf
            pdf_path = generar_pdf(actividad, participantes, profesorado=profesorado_responsable, profesor_nombre=profesor_creador)

            if not pdf_path or not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
                print("❌ Error: PDF no generado o está vacío.")
                pdf_path = None
            else:
                print("✅ PDF generado correctamente:", pdf_path)
        except Exception as e:
            print("❌ Error al generar PDF:", e)

        try:
            msg = Message(
                subject=f"Nueva actividad creada: {actividad.nombre}",
                recipients=['jlmollinedo@gmail.com'],
                body=f"Se ha creado la actividad '{actividad.nombre}' para el día {actividad.fecha.strftime('%d/%m/%Y')} por {profesor_creador}."
            )
            if pdf_path:
                with app.open_resource(pdf_path) as pdf_file:
                    msg.attach(f"actividad_{actividad.id}.pdf", "application/pdf", pdf_file.read())
            mail.send(msg)
            print("✅ Correo enviado correctamente.")
        except Exception as e:
            print("❌ Error al enviar correo:", e)

        flash('Actividad creada correctamente.')
        return redirect(url_for('calendario'))

    departamentos = Departamento.query.all()
    grupos = Grupo.query.options(joinedload(Grupo.curso)).all()
    alumnos = Alumno.query.all()

    # Obtener profesores agrupados por departamento
    profesores_por_departamento = {}
    for departamento in departamentos:
        #profesores_por_departamento[departamento.id] = departamento.profesores.all()  # Ajusta según tu relación
        profesores_por_departamento[departamento.id] = departamento.profesorado  # sin .all()

    return render_template(
        'formulario.html',
        actividad=None,
        departamentos=departamentos,
        grupos=grupos,
        alumnos=alumnos,
        departamentos_ids_seleccionados=[],
        grupos_seleccionados=[],
        alumnos_participantes_ids=[],
        fecha=fecha,
        hora_inicio_str=hora_inicio_str,
        hora_fin_str=hora_fin_str,
        profesores_por_departamento=profesores_por_departamento  # NUEVO
    )

@app.route('/profesorado_por_departamento', methods=['POST'])
def profesorado_por_departamento():
    departamento_ids = request.json.get('departamento_ids', [])

    profesorado = Profesorado.query.filter(Profesorado.departamento_id.in_(departamento_ids)).all()

    lista_profesorado = [
        {
            'id': prof.id,
            'nombre_completo': f"{prof.nombre} {prof.apellido}",
            'departamento_id': prof.departamento_id
        }
        for prof in profesorado
    ]

    return jsonify(lista_profesorado)

import os
import os
from flask import flash, redirect, url_for
from flask_login import login_required

@app.route('/actividad/<int:id>/eliminar', methods=['POST'])
@rol_requerido('profesor')
def eliminar_actividad(id):
    actividad = Actividad.query.get_or_404(id)

    try:
        # Eliminar participaciones relacionadas
        participaciones = Participacion.query.filter_by(actividad_id=id).all()
        for p in participaciones:
            db.session.delete(p)
        print(f"🗑 Participaciones eliminadas: {len(participaciones)}")

        # Eliminar PDF si existe
        pdf_filename = f"actividad_{actividad.id}.pdf"
        pdf_path = os.path.join("pdfs", pdf_filename)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            print(f"✅ PDF eliminado: {pdf_path}")
        else:
            print(f"📄 No se encontró el PDF: {pdf_path}")

        # Eliminar la actividad
        db.session.delete(actividad)
        db.session.commit()
        print(f"✅ Actividad con id={id} eliminada de la base de datos")

        flash("Actividad y PDF eliminados correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al eliminar actividad: {e}")
        flash("Error al eliminar la actividad.", "danger")

    return redirect(url_for('calendario'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

