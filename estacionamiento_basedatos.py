import sqlite3
import hashlib





# Clase para acceder a metodos en la Base de datos
class AccesoBaseDatos:
    def __init__(self):
        # Conexión a la base de datos
        self.conn = sqlite3.connect('estacionamientoapp.db')
        self.cursor = self.conn.cursor()
        self.crear_tablas()
    def crear_tablas(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY,
                nombre TEXT,
                apellido TEXT,
                fecha_nacimiento DATE,
                email TEXT UNIQUE,
                contraseña TEXT,
                estado_bloqueo BOOLEAN DEFAULT 0
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehiculos (
                id INTEGER PRIMARY KEY,
                usuario_id INTEGER,
                marca TEXT,
                modelo TEXT,
                patente TEXT(6) UNIQUE,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Multas (
                id INTEGER PRIMARY KEY,
                usuario_id INTEGER,
                admin_id INTEGER,
                accion TEXT,
                fecha_accion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY(admin_id) REFERENCES administradores(id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS estacionamientos (
                id INTEGER PRIMARY KEY,
                direccion TEXT UNIQUE,
                Discapacitados BOOLEAN DEFAULT 0,
                Disponible BOOLEAN DEFAULT 0,
                usuario_id INTEGER,
                vehiculo_id INTEGER,
                solicitudes INTEGER DEFAULT 0,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY(vehiculo_id) REFERENCES vehiculos(id)
            )
        ''')
        self.conn.commit()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS administradores (
                id_credenciales INTEGER PRIMARY KEY,
                nombre_completo TEXT,
                email TEXT UNIQUE,
                fecha_nacimiento DATE,
                usuario_id INTEGER,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
            )
        ''')
        try:
            self.cursor.execute('''
                    ALTER TABLE administradores ADD COLUMN contraseña TEXT 
                ''')
            self.conn.commit()
        except sqlite3.OperationalError:

            pass
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS tarifas (
            id INTEGER PRIMARY KEY,
            usuario_id INTEGER,
            estacionamiento_id INTEGER,
            tarifa NUMERIC,
            tiempo_inicio TIMESTAMP,
            tiempo_fin TIMESTAMP,
            total_pagar NUMERIC,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY(estacionamiento_id) REFERENCES estacionamientos(id)
            );''')
        self.conn.commit()

    #Función para el inicio de sesión

    def iniciar_sesion(self,email, contraseña):
        # Hashear la contraseña para compararla con la almacenada en la base de datos
        contraseña_hasheada = hashlib.sha256(contraseña.encode()).hexdigest()

        # Buscar el usuario en la base de datos
        self.cursor.execute('''
            SELECT id, nombre FROM usuarios WHERE email = ? AND contraseña = ?
        ''', (email, contraseña_hasheada))
        usuario = self.cursor.fetchone()

        if usuario:
            print(f"Bienvenido, {usuario[1]}")
            return usuario[0]  # Devolver el ID del usuario
        else:
            print("Credenciales inválidas")
            return None

    # Función para crear un nuevo usuario con su vehículo
    def crear_usuario(self, nombre, apellido, fecha_nacimiento, email, contraseña, patente, marca, modelo):
        # Verifica si el correo electrónico ya está en uso
        if self.verificar_existenciacorreo(email):
            return "correo_existente"

        # Verifica si la patente ya está en uso
        if self.verificar_existenciapatente(patente):
            return "patente_existente"

        # Hashear la contraseña antes de almacenarla en la base de datos
        contraseña_hasheada = hashlib.sha256(contraseña.encode()).hexdigest()

        # Insertar el nuevo usuario en la tabla de usuarios
        self.cursor.execute('''
            INSERT INTO usuarios (nombre, apellido, fecha_nacimiento, email, contraseña)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, apellido, fecha_nacimiento, email, contraseña_hasheada))
        usuario_id = self.cursor.lastrowid  # Obtener el ID del usuario recién creado

        # Insertar el vehículo asociado al nuevo usuario en la tabla de vehículos
        self.cursor.execute('''
            INSERT INTO vehiculos (usuario_id, marca, modelo, patente)
            VALUES (?, ?, ?, ?)
        ''', (usuario_id, marca, modelo, patente))
        self.conn.commit()

        return "usuario_creado"
    def verificar_existenciacorreo(self, email):
        self.cursor.execute('SELECT id FROM usuarios WHERE email = ?', (email,))
        return self.cursor.fetchone() is not None
    def verificar_existenciapatente(self, patente):
        self.cursor.execute('SELECT id FROM vehiculos WHERE patente = ?', (patente,))
        return self.cursor.fetchone() is not None
    # Función para solicitar un estacionamiento
    def solicitar_estacionamiento(self,usuario_id):
        # Solicitar la patente del vehículo
        patente = input("Por favor, ingresa la patente de tu vehículo (6 caracteres): ").strip().upper()

        # Verificar si el vehículo existe en la base de datos
        self.cursor.execute('''
            SELECT id FROM vehiculos WHERE patente = ? AND usuario_id = ?
        ''', (patente, usuario_id))
        vehiculo = self.cursor.fetchone()

        if vehiculo:
            # Registrar la solicitud de estacionamiento
            self.cursor.execute('''
                INSERT INTO estacionamientos (direccion, usuario_id, vehiculo_id)
                VALUES (?, ?, ?)
            ''', ("Dirección de estacionamiento", usuario_id, vehiculo[0]))
            self.conn.commit()
            print("Solicitud de estacionamiento realizada con éxito.")
        else:
            print("No se encontró ningún vehículo registrado con esa patente para este usuario.")

    # Función para registrar un estacionamiento
    def registrar_estacionamiento(self,direccion, discapacitados=False, disponible=False, usuario_id=None, vehiculo_id=None):
        self.cursor.execute('''
            INSERT INTO estacionamientos (direccion, Discapacitados, Disponible, usuario_id, vehiculo_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (direccion, discapacitados, disponible, usuario_id, vehiculo_id))
        self.conn.commit()
        print("Estacionamiento registrado exitosamente")

    # Funcion editar usuario
    def editar_usuario(self, id_usuario, nuevo_nombre, nuevo_apellido, nuevo_email):
        self.cursor.execute("""
        UPDATE usuarios SET nombre = ?, apellido = ?, email = ?
        WHERE id = ?;""", (nuevo_nombre, nuevo_apellido, nuevo_email, id_usuario))
        self.conn.commit()

    # Funcion obtener datos del usuario
    def obtener_datos(self, id_usuario):
        self.cursor.execute("""SELECT nombre, apellido, email FROM usuarios WHERE id = ?;""", (id_usuario,))
        return self.cursor.fetchone()
    # Funcion obtener id del usuario
    def obtener_id_usuario(self, email):
        self.cursor.execute("SELECT id FROM usuarios WHERE email = ?;", (email))
        return self.cursor.fetchone()

    def eliminar_usuario(self, id_usuario):
        try:
            # Eliminar el usuario de la tabla de usuarios
            self.cursor.execute('DELETE FROM usuarios WHERE id = ?', (id_usuario,))
            # Eliminar los registros relacionados en otras tablas, como vehículos asociados
            self.cursor.execute('DELETE FROM vehiculos WHERE usuario_id = ?', (id_usuario,))
            # Eliminar los registros relacionados en la tabla de administradores, si corresponde
            self.cursor.execute('DELETE FROM administradores WHERE usuario_id = ?', (id_usuario,))
            # Commit los cambios
            self.conn.commit()
            print("Usuario eliminado exitosamente.")
        except Exception as e:
            print(f"Error al intentar eliminar el usuario: {e}")
    def registrar_administrador(self, id_credenciales, nombre_completo, email, fecha_nacimiento, contraseña,
                                usuario_id):
        # Verificar si el administrador ya está registrado
        self.cursor.execute('SELECT nombre_completo FROM administradores WHERE id_credenciales = ?', (id_credenciales,))
        existente = self.cursor.fetchone()
        if existente:
            print(f"Error: El administrador {nombre_completo} ya está registrado.")
            return

        # Hashear la contraseña antes de almacenarla en la base de datos
        contraseña_hasheada = hashlib.sha256(contraseña.encode()).hexdigest()
        self.cursor.execute('''
            INSERT INTO administradores (id_credenciales, nombre_completo, email, fecha_nacimiento, contraseña, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (id_credenciales, nombre_completo, email, fecha_nacimiento, contraseña_hasheada, usuario_id))

        # Guardar los cambios
        self.conn.commit()
        print(f"El administrador {nombre_completo} se registró correctamente.")

    def iniciar_sesion_administrador(self, credenciales, email, contraseña):
        # Hashear la contraseña para compararla con la almacenada en la base de datos
        contraseña_hasheada = hashlib.sha256(contraseña.encode()).hexdigest()

        # Buscar al administrador en la base de datos
        self.cursor.execute('''
            SELECT nombre_completo FROM administradores 
            WHERE email = ? AND contraseña = ? AND id_credenciales = ?
        ''', (email, contraseña_hasheada, credenciales))
        administrador = self.cursor.fetchone()

        if administrador:
            nombre_completo = administrador[0]
            return f"Bienvenido, administrador {nombre_completo}. Sesión iniciada como administrador."
        else:
            return print("error")
    def obtener_id_admin(self, email):
        self.cursor.execute("SELECT id FROM admininistradores WHERE email = ?;", (email))
        return self.cursor.fetchone()

    # Funcion para crear estacionamientos
    def crear_estacionamiento(self, direccion, discapacitados=False, disponible=True):
        try:
            self.cursor.execute('''
                INSERT INTO estacionamientos (direccion, Discapacitados, Disponible)
                VALUES (?, ?, ?)
            ''', (direccion, discapacitados, disponible))
            self.conn.commit()
            print(f"El espacio '{direccion}' creado exitosamente.")
        except sqlite3.IntegrityError:
            print(f"Error: El estacionamiento '{direccion}' ya existe.")
        except Exception as e:
            print(f"Ocurrió un error al intentar crear el estacionamiento: {e}")

    # Funcion para que me de los estacionamientos
    def obtener_estacionamientos(self):
        self.cursor.execute('''
            SELECT direccion, Disponible, COUNT(usuario_id) as Solicitudes
            FROM estacionamientos
            GROUP BY direccion
        ''')
        return self.cursor.fetchall()

    # Funcion para actualizar de disponible a no
    def actualizar_estado_estacionamiento(self, direccion, disponible):
        self.cursor.execute('''
            UPDATE estacionamientos SET Disponible = ?
            WHERE direccion = ?
        ''', (disponible, direccion))
        self.conn.commit()

    def actualizar_solicitud_estacionamiento(self, direccion):
        # Aumenta el contador de solicitudes para un estacionamiento específico
        self.cursor.execute('''
            UPDATE estacionamientos SET solicitudes = solicitudes + 1
            WHERE direccion = ?
        ''', [direccion])
        self.conn.commit()
    def obtener_info_estacionamiento(self, direccion):
        self.cursor.execute('''
            SELECT direccion, Disponible FROM estacionamientos WHERE direccion = ?
        ''', (direccion,))
        return self.cursor.fetchone()

    # Cerrar la conexión después de usar las funciones
    def cerrar_conexion(self):
        self.cursor.close()
        self.conn.close()

# Aqui para los ejemplos
db = AccesoBaseDatos()
#db.crear_usuario("Matias","Saa",20001211,"e@gmail.com","1234","HJKU20","Toyota","R-26")
db.iniciar_sesion("e","1234")
id_credenciales = 1
nombre_completo = "Nombre Apellido"
email = "admin@example.com"
fecha_nacimiento = "1990-01-01"
contraseña = "contraseña_segura"
usuario_id = None

# Llamar al método para registrar un nuevo administrador
db.registrar_administrador(id_credenciales, nombre_completo, email, fecha_nacimiento, contraseña, usuario_id)
#id_credenciales = 1  # Asegúrate de que este ID coincida con el de un administrador existente
#email = "admin@example.com"
#contraseña = "contraseña_segura"

# Llamar al método para iniciar sesión como administrador
mensaje = db.iniciar_sesion_administrador(id_credenciales, email, contraseña)
print(mensaje)

print(db.obtener_estacionamientos())
#Estacionamientos creados
"""db.crear_estacionamiento("A1",False, True)
db.crear_estacionamiento("A2",False, True)
db.crear_estacionamiento("A3",False, True)
db.crear_estacionamiento("A4",False, True)
db.crear_estacionamiento("A5",False, True)
db.crear_estacionamiento("A6",False, True)
db.crear_estacionamiento("A7",False, True)"""


