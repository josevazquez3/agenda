from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import redirect
import os

def generar_pdf_historial(request, paciente, template_name, turnos=None):
    try:
        from weasyprint import HTML
        from weasyprint.text.fonts import FontConfiguration

        # Renderizar el template a HTML
        html_string = render_to_string(template_name, {
            'paciente': paciente,
            'turnos': turnos,
            'request': request
        })

        # Configuración de fuentes
        font_config = FontConfiguration()
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))

        # Generar PDF
        pdf = html.write_pdf(font_config=font_config)

        # Crear respuesta HTTP con el PDF
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'filename="historial_{paciente.id}.pdf"'
        return response

    except ImportError:
        return redirect('historial_paciente_nodisponible', paciente_id=paciente.id)