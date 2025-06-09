import google.generativeai as genai
from PIL import Image
import PyPDF2
from decouple import config
import io

API_KEY = config('API_KEY_GEMINI')
genai.configure(api_key=API_KEY)

def cargar_imagen_o_pdf(file_obj, extension):
    if extension == '.pdf':
        reader = PyPDF2.PdfReader(file_obj)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text
    elif extension in ['.jpg', '.jpeg', '.png']:
        image = Image.open(file_obj)
        return image
    else:
        raise ValueError("Unsupported file format")

def analizar_documento_con_gemini(file_obj, extension):
    contenido = cargar_imagen_o_pdf(file_obj, extension)

    model = genai.GenerativeModel('models/gemini-2.0-flash')

    prompt = """
        Extract the following information from the provided document and output it in JSON format:

        {
        "NombreCliente": "The name of the client/buyer",
        "ProveedorRUC": "The RUC number of the provider/seller",
        "FechaDePedido": "The date when the order/invoice was issued",
        "DetallesPedido": [
            {
            "Codigo": "Product code/article number",
            "NombreProducto": "Product name/description",
            "PrecioUnitario": "UNIT PRICE PER SINGLE ITEM (not total, not quantity)",
            "Cantidad": "NUMBER OF ITEMS ordered/purchased", (type number in integer)
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

    response = model.generate_content([prompt, contenido])
    
    return response
