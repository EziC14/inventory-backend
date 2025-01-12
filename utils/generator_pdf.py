from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from django.http import HttpResponse
import os
from datetime import datetime

def generar_pdf(datos, template_path, output_directory='trainer/report/', file_prefix='reporte', page_size='A4', orientation='landscape', margin='5mm'):
    """
    Genera un reporte en PDF a partir de un template HTML.

    Args:
        datos (dict): Diccionario con los datos para renderizar el template.
        template_path (str): Ruta del template HTML.
        output_directory (str): Directorio donde se guardará el archivo PDF.
        file_prefix (str): Prefijo para el nombre del archivo PDF.
        page_size (str): Tamaño de la página del PDF (por defecto es 'A4').
        orientation (str): Orientación de la página ('portrait' para vertical, 'landscape' para horizontal).
        margin (str): Márgenes del PDF (por defecto '5mm').

    Returns:
        HttpResponse: Respuesta HTTP con el archivo PDF adjunto.
    """
    # Generar nombre y ruta del archivo PDF
    nombre_archivo = f'{file_prefix}-{datetime.now().strftime("%Y-%m-%d")}.pdf'
    ruta_archivo_pdf = os.path.join(output_directory, nombre_archivo)

    # Renderizar el template con los datos
    html_string = render_to_string(template_path, {'datos': datos})

    # Configurar estilos CSS para el margen y la orientación
    css = CSS(string=f'''
        @page {{
            size: {page_size} {orientation};
            margin: {margin};
        }}
    ''')

    # Generar el PDF con los estilos y opciones de página
    pdf = HTML(string=html_string).write_pdf(stylesheets=[css])

    # Crear respuesta HTTP con el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(ruta_archivo_pdf)}"'

    # Escribir el contenido del PDF en la respuesta
    response.write(pdf)

    return response
