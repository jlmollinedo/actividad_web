from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Tabla intermedia para Actividad ↔ Departamento (relación muchos a muchos)
actividad_departamento = db.Table('actividad_departamento',
    db.Column('actividad_id', db.Integer, db.ForeignKey('actividades.id'), primary_key=True),
    db.Column('departamento_id', db.Integer, db.ForeignKey('departamentos.id'), primary_key=True)
)


# ✅ Corrección en la tabla intermedia para la relación Actividad ↔ Alumnado
actividad_alumnado = db.Table('actividad_alumnado',
    db.Column('alumno_id', db.Integer, db.ForeignKey('alumnos.id'), primary_key=True),
    db.Column('actividad_id', db.Integer, db.ForeignKey('actividades.id'), primary_key=True)
)

actividad_profesorado = db.Table('actividad_profesorado',
    db.Column('actividad_id', db.Integer, db.ForeignKey('actividades.id'), primary_key=True),
    db.Column('profesorado_id', db.Integer, db.ForeignKey('profesorado.id'), primary_key=True)
)


class Alumno(db.Model):
    __tablename__ = 'alumnos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupos.id'))

    grupo = db.relationship('Grupo', back_populates='alumnos')
    participaciones = db.relationship('Participacion', back_populates='alumno')
    actividades = db.relationship('Actividad', secondary=actividad_alumnado, back_populates='alumnado')

class Actividad(db.Model):
    __tablename__ = 'actividades'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)

    # ✅ Relación muchos a muchos con Departamentos
    departamentos = db.relationship('Departamento', secondary=actividad_departamento, backref='actividades')

    # ✅ Relación con alumnos a través de la tabla intermedia
    alumnado = db.relationship('Alumno', secondary=actividad_alumnado, back_populates='actividades')

    # ✅ Relación con Participación (alumnos inscritos en la actividad)
    participantes = db.relationship('Participacion', back_populates='actividad', cascade="all, delete-orphan")
    profesores = db.relationship('Profesorado', secondary=actividad_profesorado, backref='actividades')

    def obtener_grupos(self):
        """Devuelve los grupos únicos asociados a la actividad"""
        return list(set([p.grupo for p in self.participantes]))

class Participacion(db.Model):
    __tablename__ = 'participaciones'

    id = db.Column(db.Integer, primary_key=True)
    actividad_id = db.Column(db.Integer, db.ForeignKey('actividades.id'), nullable=False)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumnos.id'), nullable=False)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupos.id'), nullable=False)
    asistira = db.Column(db.Boolean, default=True)

    alumno = db.relationship('Alumno', back_populates='participaciones')
    grupo = db.relationship('Grupo')
    actividad = db.relationship('Actividad', back_populates='participantes')

class Departamento(db.Model):
    __tablename__ = 'departamentos'
    __table_args__ = {'extend_existing': True}  # <--- esto permite redefinir la tabla sin error

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    profesorado = db.relationship('Profesorado', backref='departamento', lazy=True)



class Curso(db.Model):
    __tablename__ = 'cursos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    grupos = db.relationship('Grupo', back_populates='curso')

class Grupo(db.Model):
    __tablename__ = 'grupos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)

    curso = db.relationship('Curso', back_populates='grupos')
    alumnos = db.relationship('Alumno', back_populates='grupo')

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='usuario')  # 'profesor' o 'usuario'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


from flask_login import UserMixin

class Profesorado(db.Model, UserMixin):
    __tablename__ = 'profesorado'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)  # Contraseña hasheada
    rol = db.Column(db.String(20), nullable=False, default='profesor')
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamentos.id'), nullable=True)

    def __repr__(self):
        return f"<Profesorado {self.nombre} {self.apellido} ({self.email})>"
