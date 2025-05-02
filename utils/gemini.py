import google.generativeai as genai
from PIL import Image
import PyPDF2
from decouple import config

API_KEY = config('API_KEY_GEMINI')
genai.configure(api_key=API_KEY)

def cargar_imagen_o_pdf(ruta):
    if ruta.endswith('.pdf'):
        # Si el archivo es un PDF, lo extraemos como texto
        with open(ruta, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
    elif ruta.endswith(('.jpg', '.png', '.jpeg')):
        # Si es una imagen, la abrimos con Pillow
        imagen = Image.open(ruta)
        return imagen
    else:
        raise ValueError("Solo se permiten archivos PDF o de imagen (JPG, PNG, JPEG)")

# Enviar el archivo al modelo para su procesamiento
def analizar_documento_con_gemini(ruta_archivo):
    contenido = cargar_imagen_o_pdf(ruta_archivo)

    # Selecciona el modelo con capacidades de procesamiento de visión
    model = genai.GenerativeModel('models/gemini-1.5-pro')

    # Define el prompt
    prompt = """
        Extract the following information from the provided document and output it in JSON format:

        {
        "ProveedorRUC": "The RUC number of the provider/seller",
        "FechaDePedido": "The date when the order/invoice was issued",
        "DetallesPedido": [
            {
            "Codigo": "Product code/article number",
            "NombreProducto": "Product name/description",
            "PrecioUnitario": "UNIT PRICE PER SINGLE ITEM (not total, not quantity)",
            "Cantidad": "NUMBER OF ITEMS ordered/purchased",
            "MontoTotal": "Total amount for this line (PrecioUnitario * Cantidad)"
            }
        ]
        }

        IMPORTANT: Pay special attention to correctly identifying:
        - PrecioUnitario: This is the price of ONE single unit/item
        - Cantidad: This is how many units/items were ordered
        - Do NOT switch or confuse these two fields

        If any field is not found in the document, use null or empty string, but include all keys.
        Ensure the JSON is properly formatted and accurately reflects the document data.
    """

    if isinstance(contenido, str):  # Si es un texto (PDF)
        # Si es texto extraído de un PDF
        response = model.generate_content([prompt, contenido])  # Pass both prompt and content
    else:
        # Si es una imagen, le pasamos la imagen para analizar
        response = model.generate_content([prompt, contenido]) # Passboth prompt and image

    return response

ruta_archivo = '20424729052-01-F001-0023319.pdf'  # Cambia el archivo aquí

# Llamar a la función para analizar el archivo
response = analizar_documento_con_gemini(ruta_archivo)

# Imprimir la respuesta
print("Respuesta del modelo:")
print(response.text)