from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from .models import EmailLog
from app.bookings.models import Booking
from app.clients.models import Client
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Servicio para manejo de emails del sistema"""
    
    @staticmethod
    def send_booking_confirmation(booking_id: int) -> dict:
        """
        Envía email de confirmación de reserva
        
        Args:
            booking_id: ID de la reserva
            
        Returns:
            dict: Resultado del envío
        """
        try:
            # Obtener la reserva
            booking = Booking.objects.select_related('client', 'room').get(id=booking_id)
            
            # Verificar que el cliente tenga email
            if not booking.client.email:
                logger.warning(f"Cliente {booking.client.id} no tiene email configurado")
                return {
                    "success": False,
                    "message": "El cliente no tiene email configurado"
                }
            
            # Preparar datos del email
            subject = f"Confirmación de Reserva - {booking.room.number}"
            recipient_email = booking.client.email
            recipient_name = booking.client.first_name
            
            # Crear contenido HTML
            html_content = EmailService._create_booking_confirmation_html(booking)
            text_content = EmailService._create_booking_confirmation_text(booking)
            
            # Crear registro de email
            email_log = EmailLog.objects.create(
                recipient_email=recipient_email,
                recipient_name=recipient_name,
                subject=subject,
                content=html_content,
                booking=booking,
                client=booking.client
            )
            
            # Enviar email
            try:
                send_mail(
                    subject=subject,
                    message=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient_email],
                    html_message=html_content,
                    fail_silently=False
                )
                
                # Marcar como enviado
                email_log.mark_as_sent()
                
                logger.info(f"Email de confirmación enviado exitosamente a {recipient_email}")
                
                return {
                    "success": True,
                    "message": "Email enviado exitosamente",
                    "email_log_id": email_log.id,
                    "recipient_email": recipient_email,
                    "subject": subject
                }
                
            except Exception as e:
                error_msg = f"Error al enviar email: {str(e)}"
                email_log.mark_as_failed(error_msg)
                logger.error(error_msg)
                
                return {
                    "success": False,
                    "message": error_msg,
                    "email_log_id": email_log.id
                }
                
        except Booking.DoesNotExist:
            return {
                "success": False,
                "message": "Reserva no encontrada"
            }
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return {
                "success": False,
                "message": f"Error interno: {str(e)}"
            }
    
    @staticmethod
    def send_booking_confirmation_async(booking_id: int):
        """
        Envía email de confirmación de forma asíncrona (para uso en save() del modelo)
        No retorna resultado para evitar bloquear la creación de la reserva
        """
        try:
            result = EmailService.send_booking_confirmation(booking_id)
            if not result["success"]:
                logger.warning(f"Email de confirmación falló para reserva {booking_id}: {result['message']}")
        except Exception as e:
            logger.error(f"Error al enviar email de confirmación para reserva {booking_id}: {str(e)}")
    
    @staticmethod
    def send_welcome_email(client_id: int) -> dict:
        """
        Envía email de bienvenida a un nuevo cliente
        
        Args:
            client_id: ID del cliente
            
        Returns:
            dict: Resultado del envío
        """
        try:
            client = Client.objects.get(id=client_id)
            
            subject = "¡Bienvenido a O11CE!"
            recipient_email = client.email
            recipient_name = client.first_name
            
            html_content = EmailService._create_welcome_html(client)
            text_content = EmailService._create_welcome_text(client)
            
            # Crear registro de email
            email_log = EmailLog.objects.create(
                recipient_email=recipient_email,
                recipient_name=recipient_name,
                subject=subject,
                content=html_content,
                client=client
            )
            
            try:
                send_mail(
                    subject=subject,
                    message=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient_email],
                    html_message=html_content,
                    fail_silently=False
                )
                
                email_log.mark_as_sent()
                
                return {
                    "success": True,
                    "message": "Email de bienvenida enviado exitosamente",
                    "email_log_id": email_log.id,
                    "recipient_email": recipient_email
                }
                
            except Exception as e:
                error_msg = f"Error al enviar email de bienvenida: {str(e)}"
                email_log.mark_as_failed(error_msg)
                
                return {
                    "success": False,
                    "message": error_msg,
                    "email_log_id": email_log.id
                }
                
        except Client.DoesNotExist:
            return {
                "success": False,
                "message": "Cliente no encontrado"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error interno: {str(e)}"
            }
    
    @staticmethod
    def _create_booking_confirmation_html(booking: Booking) -> str:
        """Crea el contenido HTML para confirmación de reserva"""
        return f"""
        <html>
        <head>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    padding: 20px; 
                }}
                .header {{ 
                    background-color: #009485; 
                    color: white; 
                    padding: 30px; 
                    text-align: center; 
                    border-radius: 8px 8px 0 0;
                }}
                .content {{ 
                    padding: 30px; 
                    background-color: #f9f9f9;
                }}
                .details {{ 
                    background-color: white; 
                    padding: 20px; 
                    margin: 20px 0; 
                    border-radius: 8px;
                    border-left: 4px solid #009485;
                }}
                .footer {{ 
                    text-align: center; 
                    color: #666; 
                    font-size: 12px; 
                    padding: 20px;
                    background-color: #f5f5f5;
                    border-radius: 0 0 8px 8px;
                }}
                .highlight {{
                    color: #009485;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Confirmación de Reserva</h1>
                    <p>Tu reserva ha sido confirmada exitosamente</p>
                </div>
                <div class="content">
                    <h2>Hola {booking.client.first_name},</h2>
                    <p>Nos complace confirmar que tu reserva ha sido procesada exitosamente.</p>
                    
                    <div class="details">
                        <h3>📋 Detalles de la Reserva:</h3>
                        <p><strong>Número de Reserva:</strong> <span class="highlight">#{booking.id}</span></p>
                        <p><strong>Habitación:</strong> {booking.room.number}</p>
                        <p><strong>Fecha de Llegada:</strong> {booking.check_in_date}</p>
                        <p><strong>Fecha de Salida:</strong> {booking.check_out_date}</p>
                        <p><strong>Número de Personas:</strong> {booking.guests_count}</p>
                        <p><strong>Estado:</strong> <span class="highlight">{booking.get_status_display()}</span></p>
                    </div>
                    
                    <p>¡Gracias por elegir O11CE! Esperamos tu llegada.</p>
                    
                    <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
                </div>
                <div class="footer">
                    <p>Este es un email automático, por favor no respondas a este mensaje.</p>
                    <p>© 2024 O11CE - Sistema de Gestión Hotelera</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def _create_booking_confirmation_text(booking: Booking) -> str:
        """Crea el contenido de texto plano para confirmación de reserva"""
        return f"""
        Confirmación de Reserva - O11CE
        
        Hola {booking.client.first_name},
        
        Tu reserva ha sido confirmada exitosamente.
        
        Detalles de la Reserva:
        - Número de Reserva: #{booking.id}
        - Habitación: {booking.room.number}
        - Fecha de Llegada: {booking.check_in_date}
        - Fecha de Salida: {booking.check_out_date}
        - Número de Personas: {booking.guests_count}
        - Estado: {booking.get_status_display()}
        
        ¡Gracias por elegir O11CE! Esperamos tu llegada.
        
        Si tienes alguna pregunta, no dudes en contactarnos.
        
        Este es un email automático, por favor no respondas a este mensaje.
        © 2024 O11CE - Sistema de Gestión Hotelera
        """
    
    @staticmethod
    def _create_welcome_html(client: Client) -> str:
        """Crea el contenido HTML para email de bienvenida"""
        return f"""
        <html>
        <head>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    padding: 20px; 
                }}
                .header {{ 
                    background-color: #009485; 
                    color: white; 
                    padding: 30px; 
                    text-align: center; 
                    border-radius: 8px 8px 0 0;
                }}
                .content {{ 
                    padding: 30px; 
                    background-color: #f9f9f9;
                }}
                .footer {{ 
                    text-align: center; 
                    color: #666; 
                    font-size: 12px; 
                    padding: 20px;
                    background-color: #f5f5f5;
                    border-radius: 0 0 8px 8px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 ¡Bienvenido a O11CE!</h1>
                </div>
                <div class="content">
                    <h2>Hola {client.first_name},</h2>
                    <p>¡Bienvenido a nuestro sistema de gestión hotelera!</p>
                    
                    <p>Estamos emocionados de tenerte como parte de nuestra comunidad. 
                    En O11CE encontrarás:</p>
                    
                    <ul>
                        <li>✅ Reservas fáciles y rápidas</li>
                        <li>✅ Habitaciones de alta calidad</li>
                        <li>✅ Atención personalizada</li>
                        <li>✅ Sistema de gestión moderno</li>
                    </ul>
                    
                    <p>¡Esperamos que disfrutes de tu experiencia con nosotros!</p>
                </div>
                <div class="footer">
                    <p>© 2024 O11CE - Sistema de Gestión Hotelera</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def _create_welcome_text(client: Client) -> str:
        """Crea el contenido de texto plano para email de bienvenida"""
        return f"""
        ¡Bienvenido a O11CE!
        
        Hola {client.name},
        
        ¡Bienvenido a nuestro sistema de gestión hotelera!
        
        Estamos emocionados de tenerte como parte de nuestra comunidad. 
        En O11CE encontrarás:
        
        - Reservas fáciles y rápidas
        - Habitaciones de alta calidad
        - Atención personalizada
        - Sistema de gestión moderno
        
        ¡Esperamos que disfrutes de tu experiencia con nosotros!
        
        © 2024 O11CE - Sistema de Gestión Hotelera
        """
    
    @staticmethod
    def send_booking_cancellation(booking_id: int) -> dict:
        """
        Envía email de cancelación de reserva
        
        Args:
            booking_id: ID de la reserva
            
        Returns:
            dict: Resultado del envío
        """
        try:
            # Obtener la reserva
            booking = Booking.objects.select_related('client', 'room').get(id=booking_id)
            
            # Verificar que el cliente tenga email
            if not booking.client.email:
                logger.warning(f"Cliente {booking.client.id} no tiene email configurado")
                return {
                    "success": False,
                    "message": "El cliente no tiene email configurado"
                }
            
            # Preparar datos del email
            subject = f"Cancelación de Reserva - {booking.room.number}"
            recipient_email = booking.client.email
            recipient_name = booking.client.first_name
            
            # Crear contenido HTML
            html_content = EmailService._create_booking_cancellation_html(booking)
            text_content = EmailService._create_booking_cancellation_text(booking)
            
            # Crear registro de email
            email_log = EmailLog.objects.create(
                recipient_email=recipient_email,
                recipient_name=recipient_name,
                subject=subject,
                content=html_content,
                booking=booking,
                client=booking.client
            )
            
            # Enviar email
            try:
                send_mail(
                    subject=subject,
                    message=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient_email],
                    html_message=html_content,
                    fail_silently=False
                )
                
                # Marcar como enviado
                email_log.mark_as_sent()
                
                logger.info(f"Email de cancelación enviado exitosamente a {recipient_email}")
                
                return {
                    "success": True,
                    "message": "Email enviado exitosamente",
                    "email_log_id": email_log.id,
                    "recipient_email": recipient_email,
                    "subject": subject
                }
                
            except Exception as e:
                error_msg = f"Error al enviar email: {str(e)}"
                email_log.mark_as_failed(error_msg)
                logger.error(error_msg)
                
                return {
                    "success": False,
                    "message": error_msg,
                    "email_log_id": email_log.id
                }
                
        except Booking.DoesNotExist:
            return {
                "success": False,
                "message": "Reserva no encontrada"
            }
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return {
                "success": False,
                "message": f"Error inesperado: {str(e)}"
            }
    
    @staticmethod
    def _create_booking_cancellation_html(booking: Booking) -> str:
        """Crea el contenido HTML para email de cancelación"""
        return f"""
        <html>
        <head>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    padding: 20px; 
                }}
                .header {{ 
                    background-color: #dc3545; 
                    color: white; 
                    padding: 30px; 
                    text-align: center; 
                    border-radius: 8px 8px 0 0;
                }}
                .content {{ 
                    padding: 30px; 
                    background-color: #f9f9f9;
                }}
                .booking-details {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                    border-left: 4px solid #dc3545;
                }}
                .footer {{ 
                    text-align: center; 
                    color: #666; 
                    font-size: 12px; 
                    padding: 20px;
                    background-color: #f5f5f5;
                    border-radius: 0 0 8px 8px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>❌ Reserva Cancelada</h1>
                </div>
                <div class="content">
                    <h2>Hola {booking.client.first_name},</h2>
                    <p>Tu reserva ha sido cancelada exitosamente.</p>
                    
                    <div class="booking-details">
                        <h3>Detalles de la Reserva Cancelada:</h3>
                        <p><strong>Número de Reserva:</strong> #{booking.id}</p>
                        <p><strong>Habitación:</strong> {booking.room.number} ({booking.room.get_type_display()})</p>
                        <p><strong>Fechas:</strong> {booking.check_in_date.strftime('%d/%m/%Y')} - {booking.check_out_date.strftime('%d/%m/%Y')}</p>
                        <p><strong>Número de Personas:</strong> {booking.guests_count}</p>
                        <p><strong>Precio Total:</strong> ${booking.total_price}</p>
                    </div>
                    
                    <p>Si tienes alguna pregunta sobre la cancelación, no dudes en contactarnos.</p>
                    
                    <p>Esperamos verte pronto en O11CE.</p>
                </div>
                <div class="footer">
                    <p>© 2024 O11CE - Sistema de Gestión Hotelera</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    def _create_booking_cancellation_text(booking: Booking) -> str:
        """Crea el contenido de texto plano para email de cancelación"""
        return f"""
        Reserva Cancelada - O11CE
        
        Hola {booking.client.first_name},
        
        Tu reserva ha sido cancelada exitosamente.
        
        Detalles de la Reserva Cancelada:
        - Número de Reserva: #{booking.id}
        - Habitación: {booking.room.number} ({booking.room.get_type_display()})
        - Fechas: {booking.check_in_date.strftime('%d/%m/%Y')} - {booking.check_out_date.strftime('%d/%m/%Y')}
        - Número de Personas: {booking.guests_count}
        - Precio Total: ${booking.total_price}
        
        Si tienes alguna pregunta sobre la cancelación, no dudes en contactarnos.
        
        Esperamos verte pronto en O11CE.
        
        Este es un email automático, por favor no respondas a este mensaje.
        © 2024 O11CE - Sistema de Gestión Hotelera
        """
    
    @staticmethod
    def send_payment_confirmation(booking_id: int) -> dict:
        """Envía email de confirmación/recibo de pago de una reserva"""
        try:
            booking = Booking.objects.select_related('client', 'room').get(id=booking_id)
            if not booking.client.email:
                logger.warning(f"Cliente {booking.client.id} no tiene email configurado")
                return {"success": False, "message": "El cliente no tiene email configurado"}

            is_partial = (booking.payment_status == 'partial')
            subject = (
                f"Pago Parcial Registrado - {booking.room.number}" if is_partial
                else f"Confirmación de Pago - {booking.room.number}"
            )
            recipient_email = booking.client.email
            recipient_name = booking.client.first_name

            html_content = EmailService._create_payment_confirmation_html(booking)
            text_content = EmailService._create_payment_confirmation_text(booking)

            email_log = EmailLog.objects.create(
                recipient_email=recipient_email,
                recipient_name=recipient_name,
                subject=subject,
                content=html_content,
                booking=booking,
                client=booking.client
            )

            try:
                send_mail(
                    subject=subject,
                    message=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient_email],
                    html_message=html_content,
                    fail_silently=False
                )
                email_log.mark_as_sent()
                logger.info(f"Email de pago enviado a {recipient_email}")
                return {"success": True, "message": "Email enviado exitosamente", "email_log_id": email_log.id}
            except Exception as e:
                error_msg = f"Error al enviar email: {str(e)}"
                email_log.mark_as_failed(error_msg)
                logger.error(error_msg)
                return {"success": False, "message": error_msg, "email_log_id": email_log.id}
        except Booking.DoesNotExist:
            return {"success": False, "message": "Reserva no encontrada"}
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return {"success": False, "message": f"Error interno: {str(e)}"}

    @staticmethod
    def _create_payment_confirmation_html(booking: Booking) -> str:
        """Crea HTML para email de confirmación/recibo de pago"""
        status_label = 'Pago Parcial' if booking.payment_status == 'partial' else 'Pagado'
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #198754; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ padding: 30px; background-color: #f9f9f9; }}
                .booking-details {{ background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #198754; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; padding: 20px; background-color: #f5f5f5; border-radius: 0 0 8px 8px; }}
            </style>
        </head>
        <body>
            <div class=\"container\">
                <div class=\"header\">
                    <h1>✔ {status_label}</h1>
                </div>
                <div class=\"content\">
                    <h2>Hola {booking.client.first_name},</h2>
                    <p>Hemos registrado tu {status_label.lower()} para la reserva #{booking.id}.</p>
                    <div class=\"booking-details\">
                        <h3>Detalles de la Reserva:</h3>
                        <p><strong>Número de Reserva:</strong> #{booking.id}</p>
                        <p><strong>Habitación:</strong> {booking.room.number} ({booking.room.get_type_display()})</p>
                        <p><strong>Fechas:</strong> {booking.check_in_date.strftime('%d/%m/%Y')} - {booking.check_out_date.strftime('%d/%m/%Y')}</p>
                        <p><strong>Número de Personas:</strong> {booking.guests_count}</p>
                        <p><strong>Total:</strong> ${booking.total_price}</p>
                        <p><strong>Pagado:</strong> ${booking.paid_amount}</p>
                        <p><strong>Saldo Pendiente:</strong> ${booking.amount_due}</p>
                        <p><strong>Estado de Pago:</strong> {status_label}</p>
                    </div>
                    <p>Gracias por tu confianza en O11CE. ¡Te esperamos!</p>
                </div>
                <div class=\"footer\">
                    <p>© 2024 O11CE - Sistema de Gestión Hotelera</p>
                </div>
            </div>
        </body>
        </html>
        """

    @staticmethod
    def _create_payment_confirmation_text(booking: Booking) -> str:
        """Texto plano para email de pago"""
        status_label = 'Pago Parcial' if booking.payment_status == 'partial' else 'Pagado'
        return f"""
        Confirmación de Pago - O11CE
        
        Hola {booking.client.first_name},
        
        Hemos registrado tu {status_label.lower()} para la reserva #{booking.id}.
        
        Detalles:
         - Habitación: {booking.room.number} ({booking.room.get_type_display()})
         - Fechas: {booking.check_in_date.strftime('%d/%m/%Y')} - {booking.check_out_date.strftime('%d/%m/%Y')}
         - Total: ${booking.total_price}
         - Pagado: ${booking.paid_amount}
         - Saldo Pendiente: ${booking.amount_due}
         - Estado de Pago: {status_label}
         
         ¡Gracias por tu preferencia!
         
         © 2024 O11CE - Sistema de Gestión Hotelera
        """