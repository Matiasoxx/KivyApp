from kivy.properties import partial
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivy.metrics import dp
from kivymd.uix.textfield import MDTextField
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivymd.uix.screen import Screen
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.navigationrail import MDNavigationRail, MDNavigationRailItem
from kivymd.uix.list import MDList, OneLineListItem
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivymd.uix.toolbar import toolbar
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.button import MDFlatButton
from kivy.clock import Clock
from kivy.properties import StringProperty
import re
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests

from estacionamiento_basedatos import AccesoBaseDatos

def enviar_correo(destinatario, asunto, mensaje):
    servidor_smtp = "smtp.office365.com"
    puerto_smtp = 587  # Usar 587 para TLS
    usuario_smtp = "parkwaze@outlook.com"
    contraseña_smtp = "Hola1234."

    # Crear un objeto MIMEMultipart para el mensaje
    correo = MIMEMultipart()
    correo["From"] = usuario_smtp
    correo["To"] = destinatario
    correo["Subject"] = asunto

    # Adjuntar el cuerpo del mensaje
    cuerpo_mensaje = MIMEText(mensaje, "plain")
    correo.attach(cuerpo_mensaje)

    # Conectar al servidor SMTP y enviar el correo
    with smtplib.SMTP(host=servidor_smtp, port=puerto_smtp) as servidor:
        servidor.starttls()  # Iniciar el modo de conexión TLS (Transport Layer Security)
        servidor.login(usuario_smtp, contraseña_smtp)
        servidor.send_message(correo)
class DefaultScreen(Screen):
    pass


class LoginScreen(Screen):
    pass


class RegisterScreen(Screen):
    def registrarse(self):
        print("Llegué aquí")


class RegisterScreen2(Screen):
    pass


class proximamenteScreen(Screen):
    pass


class MenuScreen(Screen):
    tarifa_actualizada = StringProperty("Tarifa Actual: 0")

    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.popup = None  # Atributo para almacenar la instancia del Popup
        self.estacionamientos_solicitados = set()
        self.tiempo_recordatorio = 0

    def on_enter(self, *args):
        super(MenuScreen, self).on_enter(*args)
        app = MDApp.get_running_app()
        app.cargardatos()
        self.mostrar_estacionamientos()

    def mostrar_estacionamientos(self):
        self.ids.container.clear_widgets()
        estacionamientos = MDApp.get_running_app().db.obtener_estacionamientos()
        layout = GridLayout(cols=2, spacing=10, size_hint_y=None, padding=dp(10))

        for estacionamiento in estacionamientos:
            boton = MDFlatButton(
                text=f"{estacionamiento[0]}\nSolicitado por : {estacionamiento[2]} usuarios",
                size_hint_y=None, height=dp(100),
                md_bg_color=[1, 1, 0, 1] if estacionamiento[0] in self.estacionamientos_solicitados else [0, 1, 0, 1] if
                estacionamiento[1] else [1, 0, 0, 1]
            )
            boton.bind(on_release=partial(self.solicitar_estacionamiento, estacionamiento[0]))

            layout.add_widget(boton)

        self.ids.container.add_widget(layout)

    def solicitar_estacionamiento(self, direccion, instance):
        if direccion in self.estacionamientos_solicitados:
            self.mostrar_popup("Error", f"Ya has solicitado el espacio {direccion}.")
            return

        if len(self.estacionamientos_solicitados) >= 3:
            self.mostrar_popup("Error", "No puedes solicitar más de 3 espacios.")
            return

        self.estacionamientos_solicitados.add(direccion)
        instance.md_bg_color = [1, 1, 0, 1]
        self.mostrar_popup_recordatorio(direccion)
        self.mostrar_estacionamientos()

    def mostrar_popup(self, titulo, mensaje):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_label = Label(text=mensaje)
        popup_button = MDFlatButton(text='Cerrar', on_release=lambda x: self.popup.dismiss())
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(popup_button)
        self.popup = Popup(title=titulo, content=popup_layout, size_hint=(None, None), size=(400, 200))
        self.popup.open()

    def cerrar_popup(self, instance):
        if self.popup:
            self.popup.dismiss()

    def mostrar_popup_recordatorio(self, direccion):
        content = BoxLayout(orientation='vertical')
        label = Label(
            text=f'Has solicitado el estacionamiento {direccion}. En cuántos minutos quieres ser recordado sobre esta solicitud?')
        time_input = MDTextField(input_filter='int', hint_text="Minutos")
        button = Button(text="Confirmar",
                        on_release=lambda x: self.configurar_y_cerrar_recordatorio(time_input.text, direccion))
        content.add_widget(label)
        content.add_widget(time_input)
        content.add_widget(button)
        self.popup_recordatorio = Popup(title="Configurar Recordatorio", content=content, size_hint=(0.9, 0.4))
        self.popup_recordatorio.open()

    def cerrar_popup_recordatorio(self, instance):
        if self.popup_recordatorio:
            self.popup_recordatorio.dismiss()

    def configurar_y_cerrar_recordatorio(self, tiempo, direccion):
        self.configurar_recordatorio(tiempo, direccion)
        self.cerrar_popup_recordatorio(None)

    def configurar_recordatorio(self, tiempo, direccion):
        try:
            tiempo_en_minutos = int(tiempo)
            Clock.schedule_once(
                lambda dt: self.mostrar_popup("Recordatorio",
                                              f"Te recordamos que solicitaste el estacionamiento \n{direccion} y aún está disponible."),
                tiempo_en_minutos * 60)
        except ValueError:
            self.mostrar_popup("Error", "Introduce un número válido.")


class RecuperarContrasenaScreen(Screen):
    pass


class AdminLoginScreen(Screen):
    pass


class proximamenteIngresoPatenteScreen(Screen):
    pass


class EstacionamientoApp(MDApp):
    admin_actu = None
    usuario_actu = None

    def build(self):
        self.db = AccesoBaseDatos()
        self.sm = ScreenManager()

        Builder.load_file("estilo.kv")

        self.sm.add_widget(DefaultScreen(name='default'))
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(RegisterScreen(name='register'))
        self.sm.add_widget(MenuScreen(name='menu'))
        self.sm.add_widget(AdminLoginScreen(name='admin_login'))
        self.sm.add_widget(proximamenteScreen(name='proximamente'))
        self.sm.add_widget(RegisterScreen2(name='register2'))
        self.sm.add_widget(proximamenteIngresoPatenteScreen(name='proximamentePatente'))

        return self.sm

    def cambiar_pantalla(self, nombre_pantalla):
        self.sm.current = nombre_pantalla

    def iniciar_sesion(self, email, password):
        usuario_id = self.db.iniciar_sesion(email, password)
        if usuario_id:
            self.usuario_actu = usuario_id
            self.cambiar_pantalla('menu')
        else:
            self.mostrar_popupLocal("Credenciales Invalidas", "No se ha encontrado su usuario. Intentelo de nuevo.")

    def registrarse(self):
        self.sm.current = 'register'

    def cargardatos(self):
        if self.usuario_actu:
            datos = self.db.obtener_datos(self.usuario_actu)
            if datos:
                menu_scren = self.root.get_screen('menu')
                menu_scren.ids.nombre_usuario.text = datos[0]
                menu_scren.ids.apellido_usuario.text = datos[1]
                menu_scren.ids.email_usuario.text = datos[2]

    def guardar_cambios(self):
        nombre = self.root.get_screen('menu').ids.nombre_usuario.text
        apellido = self.root.get_screen('menu').ids.apellido_usuario.text
        email = self.root.get_screen('menu').ids.email_usuario.text
        color_normal = self.theme_cls.primary_color
        hay_error = False
        mensaje_error = ""
        if "@" not in email or "." not in email:
            # Actualiza el color del texto a rojo si no coincide
            self.mostrar_popup("Correo Electrónico Incorrecto",
                               "El correo electrónico es incorrecto, \nel formato debe ser Correo@algo.dominio.")
            self.root.get_screen('menu').ids.email_usuario.line_color_normal = self.theme_cls.error_color
            hay_error = True
        else:
            self.root.get_screen('menu').ids.email_usuario.line_color_normal = color_normal

            # Procede solo si no hay errores
        if not hay_error:
            self.db.editar_usuario(self.usuario_actu, nombre, apellido, email)
            self.mostrar_popup("Actualización Exitosa",
                               "Hemos actualizado tu información con los datos que nos entregaste.")
        else:
            # Opcionalmente, podrías querer hacer algo aquí si hay un error
            self.mostrar_popup("Error en la actualización",
                               f"Se encontraron errores en los siguientes campos:\n{mensaje_error}")
            pass

    def iniciar_sesion_admin(self, credentials, email, password):
        admin_actu = self.db.iniciar_sesion_administrador(credentials, email, password)
        if admin_actu:
            self.admin_actu = admin_actu
            self.mostrar_popupLocal("Bienvenido Administrado",
                                    "Es un gusto volver a verlo Administrador. Que tenga un gran día")
        else:
            self.mostrar_popupLocal("Credenciales Invalidas", "Credenciales invalidas. Intentalo otra vez")

    def cerrar_sesion_usuario(self):
        self.usuario_actu = None
        self.mostrar_popupLocal("Sesión Cerrada", "Se ha cerrado sesión.")
        self.cambiar_pantalla('default')

    def cerrar_sesion_admin(self):
        self.admin_actu = None
        self.cambiar_pantalla('default')

    def eliminar_usuario(self):
        if self.usuario_actu:
            self.db.eliminar_usuario(self.usuario_actu)
            self.mostrar_popupLocal("Usuario eliminado",
                                    "Tu cuenta ha sido eliminada exitosamente. Espero hayas disfrutado tú tiempo con nosotros. Hasta luego!")
            # Cerrar sesión del usuario después de eliminarlo
            self.cerrar_sesion_usuario()
        else:
            print("No hay usuario conectado para eliminar")

    def registrar_administrador(self, credentials, email, password):
        if self.db.registrar_administrador(credentials, email, password):
            print("Registro de administrador exitoso")
        else:
            print("El email ya está registrado")

    def mostrar_popup(self, titulo, mensaje):
        # Crea el contenido de la ventana emergente
        contenido = BoxLayout(orientation='vertical', padding=10, spacing=10)
        contenido.add_widget(Label(text=mensaje))
        boton_cerrar = Button(text="Cerrar", size_hint_y=None, height=dp(48))
        contenido.add_widget(boton_cerrar)

        # Crea la ventana emergente
        popup = Popup(title=titulo, content=contenido, size_hint=(None, None), size=(400, 200))

        # Cierra la ventana emergente al hacer clic en el botón de cerrar
        boton_cerrar.bind(on_release=popup.dismiss)

        # Muestra la ventana emergente
        popup.open()

    def registrar_usuario(self):

        # Obtiene los textos de los campos de contraseña
        contrasena = self.root.get_screen('register').ids.password_field.text
        confirmar_contrasena = self.root.get_screen('register').ids.Confirm_password_field.text
        correo_electronico = self.root.get_screen('register').ids.email_field.text
        confirmar_correo_electronico = self.root.get_screen('register').ids.email_confirm_field.text
        nombre = self.root.get_screen('register').ids.Name_field.text
        apellido = self.root.get_screen('register').ids.Last_name_field.text
        fecha = self.root.get_screen('register').ids.Ageofuser.text
        patente = self.root.get_screen('register2').ids.Patente_field.text.upper()
        marca = self.root.get_screen('register2').ids.Marca_field.text
        modelo = self.root.get_screen('register2').ids.Modelo_field.text
        color_normal = self.theme_cls.primary_color

        hay_error = False

        # Verifica si las contraseñas coinciden
        if contrasena != confirmar_contrasena:
            # Actualiza el color del texto a rojo si no coinciden
            self.mostrar_popup("Contraseña incorrecta", "Las contraseñas no coinciden.")
            self.root.get_screen('register').ids.password_field.line_color_normal = self.theme_cls.error_color
            self.root.get_screen('register').ids.Confirm_password_field.line_color_normal = self.theme_cls.error_color
            hay_error = True
        else:
            self.root.get_screen('register').ids.password_field.line_color_normal = color_normal
            self.root.get_screen('register').ids.Confirm_password_field.line_color_normal = color_normal

        if correo_electronico != confirmar_correo_electronico:
            # Actualiza el color del texto a rojo si no coinciden
            self.mostrar_popup("Correo Electronico incorrecto", "Los correos no coinciden.")
            self.root.get_screen('register').ids.email_field.line_color_normal = self.theme_cls.error_color
            self.root.get_screen('register').ids.email_confirm_field.line_color_normal = self.theme_cls.error_color
            hay_error = True
        else:
            self.root.get_screen('register').ids.email_field.line_color_normal = color_normal
            self.root.get_screen('register').ids.email_confirm_field.line_color_normal = color_normal

        if not correo_electronico or not confirmar_correo_electronico:
            # Actualiza el color del texto a rojo si no coinciden
            self.mostrar_popup("Correo Electronico incorrecto", "Este campo no puede estar vacio.")
            self.root.get_screen('register').ids.email_field.line_color_normal = self.theme_cls.error_color
            self.root.get_screen('register').ids.email_confirm_field.line_color_normal = self.theme_cls.error_color
            hay_error = True
        else:
            self.root.get_screen('register').ids.email_field.line_color_normal = color_normal
            self.root.get_screen('register').ids.email_confirm_field.line_color_normal = color_normal

        if not contrasena or not confirmar_contrasena:
            # Actualiza el color del texto a rojo si no coinciden
            self.mostrar_popup("Contraseña incorrecta", "Este campo no puede estar vacio.")
            self.root.get_screen('register').ids.password_field.line_color_normal = self.theme_cls.error_color
            self.root.get_screen('register').ids.Confirm_password_field.line_color_normal = self.theme_cls.error_color
            hay_error = True
        else:
            self.root.get_screen('register').ids.password_field.line_color_normal = color_normal
            self.root.get_screen('register').ids.Confirm_password_field.line_color_normal = color_normal

        if len(contrasena) < 8 or not any(char.isupper() for char in contrasena) or not any(
                char.isdigit() for char in contrasena) or not re.search("[!@#$%^&*()_+=\[{\]};:<>|./?,-]", contrasena):
            self.mostrar_popup("Contraseña incorrecta",
                               "La contraseña debe tener al menos\n8 caracteres, una mayuscula\n un numero y un caracter especial.")
            self.root.get_screen('register').ids.password_field.line_color_normal = self.theme_cls.error_color
            self.root.get_screen('register').ids.Confirm_password_field.line_color_normal = self.theme_cls.error_color
            hay_error = True
        else:
            self.root.get_screen('register').ids.password_field.line_color_normal = color_normal
            self.root.get_screen('register').ids.Confirm_password_field.line_color_normal = color_normal

        if "@" not in correo_electronico  or "." not in correo_electronico:
            # Actualiza el color del texto a rojo si no coinciden
            self.mostrar_popup("Correo Electronico incorrecto",
                               "El Correo electronico es incorrecto, \nel formato debe ser Correo@algo.dominio")
            self.root.get_screen('register').ids.email_field.line_color_normal = self.theme_cls.error_color
            self.root.get_screen('register').ids.email_confirm_field.line_color_normal = self.theme_cls.error_color
            hay_error = True
        else:
            self.root.get_screen('register').ids.email_field.line_color_normal = color_normal
            self.root.get_screen('register').ids.email_confirm_field.line_color_normal = color_normal

        if not nombre:
            # Actualiza el color del texto a rojo si no coinciden
            self.mostrar_popup("Nombre incorrecto", "Este campo no puede estar vacio.")
            self.root.get_screen('register').ids.Name_field.line_color_normal = self.theme_cls.error_color
            hay_error = True
        else:
            self.root.get_screen('register').ids.Name_field.line_color_normal = color_normal

        if not apellido:
            # Actualiza el color del texto a rojo si no coinciden
            self.mostrar_popup("Apellido incorrecto", "Este campo no puede estar vacio.")
            self.root.get_screen('register').ids.Last_name_field.line_color_normal = self.theme_cls.error_color
            hay_error = True
        else:
            self.root.get_screen('register').ids.Last_name_field.line_color_normal = color_normal

        if not patente:
            # Actualiza el color del texto a rojo si no coinciden
            self.mostrar_popup("Patente incorrecto", "Este campo no puede estar vacio.")
            self.root.get_screen('register2').ids.Patente_field.line_color_normal = self.theme_cls.error_color
            hay_error = True
        else:
            self.root.get_screen('register2').ids.Patente_field.line_color_normal = color_normal

        if not re.match("^[A-Za-z]{4}\d{2}$", patente):
            self.mostrar_popup("Patente incorrecto", "Este campo no puede estar vacio.")
            self.root.get_screen('register2').ids.Patente_field.line_color_normal = self.theme_cls.error_color
            hay_error = True
        else:
            self.root.get_screen('register2').ids.Patente_field.line_color_normal = color_normal

        if not marca:
            # Actualiza el color del texto a rojo si no coinciden
            self.mostrar_popup("Marca incorrecta", "Este campo no puede estar vacio.")
            self.root.get_screen('register2').ids.Marca_field.line_color_normal = self.theme_cls.error_color
            hay_error = True
        else:
            self.root.get_screen('register2').ids.Marca_field.line_color_normal = color_normal

        if not modelo:
            # Actualiza el color del texto a rojo si no coinciden
            self.mostrar_popup("Modelo incorrecto",
                               "La patente debe tener exactamente\n6 caracteres, empezar con cuatro \nletras y luego dos números.\n(ej: ABCD23)")
            self.root.get_screen('register2').ids.Modelo_field.line_color_normal = self.theme_cls.error_color
            hay_error = True
        else:
            self.root.get_screen('register2').ids.Modelo_field.line_color_normal = color_normal

        self.root.get_screen('register').ids.Ageofuser.line_color_normal = color_normal
        if not re.match(r"^\d{8}$", fecha):
            self.mostrar_popup("Fecha incorrecto", "La fecha debe ser en formato\nAAAAMMDD")
            self.root.get_screen('register').ids.Ageofuser.line_color_normal = self.theme_cls.error_color
            hay_error = True
        else:
            año = int(fecha[:4])
            mes = int(fecha[4:6])
            día = int(fecha[6:8])
            # Verificar si la fecha es válida en el calendario
            try:
                datetime.strptime(fecha, '%Y%m%d')
            except ValueError:
                self.mostrar_popup("Fecha incorrecto", "La fecha debe Existir")
                self.root.get_screen('register').ids.Ageofuser.line_color_normal = self.theme_cls.error_color
                hay_error = True
            if año > 2024:
                self.mostrar_popup("Fecha incorrecto", "La fecha debe Existir")
                self.root.get_screen('register').ids.Ageofuser.line_color_normal = self.theme_cls.error_color
                hay_error = True

        if not hay_error:
            resultado_creacion = self.db.crear_usuario(nombre, apellido, fecha, correo_electronico, contrasena, patente,
                                                       marca, modelo)
            if resultado_creacion == "usuario_creado":
                # Usuario creado exitosamente
                self.mostrar_popup("Operación Exitosa", "Usuario creado exitosamente.")
                enviar_correo(correo_electronico, f"{nombre} Bienvenido a Park Waze",
                              f"Gracias {nombre} por unirte\nTu cuenta ha sido creada con exito, ya puedes disfrutar todos nuestros servicios\nAtte Servicio al cliente ParkWaze Chile")
                self.root.get_screen('register').ids.password_field.text = ''
                self.root.get_screen('register').ids.Confirm_password_field.text = ''
                self.root.get_screen('register').ids.email_field.text = ''
                self.root.get_screen('register').ids.email_confirm_field.text = ''
                self.root.get_screen('register').ids.Name_field.text = ''
                self.root.get_screen('register').ids.Last_name_field.text = ''
                self.root.get_screen('register').ids.Ageofuser.text = ''
                self.root.get_screen('register2').ids.Patente_field.text = ''
                self.root.get_screen('register2').ids.Marca_field.text = ''
                self.root.get_screen('register2').ids.Modelo_field.text = ''
                self.iniciar_sesion(correo_electronico, contrasena)
                self.cargardatos()
            elif resultado_creacion == "correo_existente":
                # Correo electrónico ya está en uso
                self.mostrar_popup("Error", "El correo electrónico ya está siendo utilizado.")
                self.root.get_screen('register').ids.email_field.line_color_normal = self.theme_cls.error_color
                self.root.get_screen('register').ids.email_confirm_field.line_color_normal = self.theme_cls.error_color
            elif resultado_creacion == "patente_existente":
                # Patente ya está en uso
                self.mostrar_popup("Error", "La patente ya está siendo utilizada.")
                self.root.get_screen('register2').ids.Patente_field.line_color_normal = self.theme_cls.error_color
            else:
                # Otro tipo de error no manejado
                self.mostrar_popup("Error", "No se pudo crear el usuario por un error desconocido.")

        else:
            self.root.current = 'register'


        
    def ingreso_patente(self):
        print("Ingresa patente")
        pass

    def volver_inicio(self):
        self.sm.current = 'default'
        pass

    def volver_menu(self):
        self.sm.current = 'menu'
        pass

    def proximamente(self):
        self.sm.current = 'proximamente'

    def mostrar_popupLocal(self, titulo, mensaje):
        # Crear el contenido del popup
        contenido = BoxLayout(orientation='vertical')
        contenido.add_widget(Label(text=mensaje))
        boton_cerrar = Button(text="Cerrar")
        contenido.add_widget(boton_cerrar)

        # Crear el popup
        popup = Popup(title=titulo, content=contenido, size_hint=(None, None), size=(400, 200))

        boton_cerrar.bind(on_release=popup.dismiss)

        # Mostrar el popup
        popup.open()

    def actualizar_tarifa(self, *args):
        # Supongamos que esta función genera o recupera una nueva tarifa
        nueva_tarifa = "Tarifa Actual: 2"  # Aquí tendríamos que implementar la lógica para cuando el usuario estacione en un espacio
        self.root.get_screen('menu').tarifa_actualizada = nueva_tarifa

    def on_start(self):
        # Programa la función actualizar_tarifa para que se ejecute cada 60 segundos (1 minuto)
        Clock.schedule_interval(self.actualizar_tarifa, 60)


if __name__ == '__main__':
    EstacionamientoApp().run()
