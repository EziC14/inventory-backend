from rest_framework import serializers

def validation_required_fields(fields):
    """Valida que los campos no estén vacíos.
    
    Args:
        fields (dict): Diccionario con nombres de campos como claves y sus valores asociados.

    Raises:
        serializers.ValidationError: Si faltan campos requeridos.

    """
    missing_fields = [name for name, value in fields.items() if not value]
    if missing_fields:
        missing_fields_str = ', '.join(missing_fields)
        raise serializers.ValidationError(f"Los siguientes campos son requeridos y no deben estar vacíos: {missing_fields_str}")