from flask import Blueprint, send_file, current_app
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from io import BytesIO
from datetime import datetime
from sqlalchemy import func
from database import db
from database.models import Usuario, ResultadosRuleta, ResultadosTragaperras, ResultadosBlackjack, ResultadosSnake

informe_bp = Blueprint('informe', __name__)

def header_footer(canvas, doc):
    width, height = letter
    margin = 50
    # Cabecera gris con logo y título
    canvas.saveState()
    canvas.setFillColorRGB(0.9, 0.9, 0.9)
    canvas.rect(0, height - 70, width, 70, fill=1, stroke=0)
    logo_path = current_app.root_path + '/static/Image/LOGO.png'
    try:
        canvas.drawImage(logo_path, margin, height - 65, width=50, height=50, preserveAspectRatio=True)
    except Exception:
        pass
    canvas.setFillColor(colors.black)
    canvas.setFont("Helvetica-Bold", 24)
    canvas.drawString(margin + 60, height - 40, "FNAFBET")
    canvas.setFont("Helvetica-Bold", 16)
    canvas.drawCentredString(width/2, height - 90, "Informe Global de Actividad - FNAF.BET")
    # Pie de página
    canvas.setFillColorRGB(0.9, 0.9, 0.9)
    canvas.rect(0, 20, width, 40, fill=1, stroke=0)
    canvas.setFillColor(colors.black)
    canvas.setFont("Helvetica-Oblique", 12)
    canvas.drawCentredString(width / 2, 35, "Gracias por usar FNAF.BET")
    canvas.restoreState()

@informe_bp.route('/generar_informe', methods=['GET', 'POST'])
def generar_informe_global():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=50, leftMargin=50,
                            topMargin=120, bottomMargin=70)
    styles = getSampleStyleSheet()
    normal = styles['Normal']
    title_style = ParagraphStyle(
        'title_style',
        parent=styles['Heading2'],
        alignment=TA_CENTER,
        fontSize=14,
        spaceAfter=12,
    )
    elements = []

    # Fecha
    fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"Fecha del informe: {fecha_str}", normal))
    elements.append(Spacer(1, 12))

    # Función para resumen de juegos
    juegos = {
        "Tragaperras": ResultadosTragaperras,
        "Ruleta": ResultadosRuleta,
        "Blackjack": ResultadosBlackjack,
    }

    def resumen_juego(model):
        partidas = db.session.query(func.count(model.id)).scalar() or 0
        apostado = db.session.query(func.coalesce(func.sum(model.dinero_invertido), 0)).scalar() or 0
        ganado = db.session.query(func.coalesce(func.sum(model.dinero_ganado), 0)).scalar() or 0
        return partidas, apostado, ganado, ganado - apostado

    elements.append(Paragraph("Resumen por Juego:", styles['Heading3']))
    data = [["Juego", "Partidas", "Apostado", "Ganado", "Balance"]]
    total_partidas = 0
    total_apostado = 0
    total_ganado = 0

    for nombre, modelo in juegos.items():
        p, a, g, b = resumen_juego(modelo)
        total_partidas += p
        total_apostado += a
        total_ganado += g
        data.append([nombre, str(p), f"${a:.2f}", f"${g:.2f}", f"${b:.2f}"])

    balance_general = total_ganado - total_apostado

    table = Table(data, hAlign='LEFT', colWidths=[100, 70, 90, 90, 90])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 18))

    elements.append(Paragraph("Totales Generales:", styles['Heading3']))
    elements.append(Paragraph(f"Total Partidas (con dinero): {total_partidas}", normal))
    elements.append(Paragraph(f"Total Apostado: ${total_apostado:.2f}", normal))
    elements.append(Paragraph(f"Total Ganado: ${total_ganado:.2f}", normal))
    elements.append(Paragraph(f"Balance General: ${balance_general:.2f}", normal))
    elements.append(Spacer(1, 18))

    # Partidas snake
    total_snake = db.session.query(ResultadosSnake).count()
    elements.append(Paragraph("Snake - Partidas Registradas:", styles['Heading3']))
    elements.append(Paragraph(f"Total de partidas jugadas en Snake: {total_snake}", normal))
    elements.append(Spacer(1, 24))

    # Ahora agregamos detalle por usuario con las tablas que me diste

    users = Usuario.query.order_by(Usuario.usuario).all()
    for user in users:
        elements.append(Paragraph(f"{user.usuario} - {user.nombre1} {user.apellido1}", title_style))

        data = [["Juego", "Partidas", "Apostado", "Ganado", "Balance"]]

        def user_stats(modelo):
            partidas = db.session.query(modelo).filter_by(id_usuario=user.id).count()
            apostado = db.session.query(func.coalesce(func.sum(modelo.dinero_invertido), 0)).filter_by(id_usuario=user.id).scalar() or 0
            ganado = db.session.query(func.coalesce(func.sum(modelo.dinero_ganado), 0)).filter_by(id_usuario=user.id).scalar() or 0
            return partidas, apostado, ganado, ganado - apostado

        for nombre, modelo in juegos.items():
            p, a, g, b = user_stats(modelo)
            if p > 0:
                data.append([nombre, str(p), f"${a:.2f}", f"${g:.2f}", f"${b:.2f}"])

        snake_p = db.session.query(ResultadosSnake).filter_by(id_usuario=user.id).count()
        if snake_p > 0:
            data.append(["Snake", str(snake_p), "-", "-", "-"])

        if len(data) > 1:
            table = Table(data, hAlign='LEFT', colWidths=[80, 60, 80, 80, 80])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#ffc107")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 18))

        # Al final de cada usuario, agregar estadísticas detalladas

        # Estadísticas Blackjack - cartas jugadas (cartas_jugador)
        # Contamos ocurrencias de combinaciones de cartas_jugador
        cartas = db.session.query(
            ResultadosBlackjack.cartas_jugador,
            func.count(ResultadosBlackjack.id)
        ).filter_by(id_usuario=user.id).group_by(ResultadosBlackjack.cartas_jugador).all()

        if cartas:
            elements.append(Paragraph("Estadísticas Blackjack - Cartas Jugadas:", styles['Heading4']))
            data_cartas = [["Cartas Jugador", "Veces Jugadas"]]
            for carta_str, veces in cartas:
                data_cartas.append([carta_str, str(veces)])
            table_cartas = Table(data_cartas, hAlign='LEFT', colWidths=[200, 100])
            table_cartas.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#28a745")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ]))
            elements.append(table_cartas)
            elements.append(Spacer(1, 12))

        # Estadísticas Tragaperras - resultados 1, 2, 3
        resultados_traga = db.session.query(
            ResultadosTragaperras.resultado1,
            ResultadosTragaperras.resultado2,
            ResultadosTragaperras.resultado3,
            func.count(ResultadosTragaperras.id)
        ).filter_by(id_usuario=user.id).group_by(
            ResultadosTragaperras.resultado1,
            ResultadosTragaperras.resultado2,
            ResultadosTragaperras.resultado3
        ).all()

        if resultados_traga:
            elements.append(Paragraph("Estadísticas Tragaperras - Resultados:", styles['Heading4']))
            data_traga = [["Resultado 1", "Resultado 2", "Resultado 3", "Veces"]]

            emoji_map = {
                "🍒": "Cereza",
                "🍋": "Limón",
                "🍉": "Sandía",
                "🍇": "Uva",
                "⭐": "Estrella",
                "🔔": "Campana"
            }
            for r1, r2, r3, veces in resultados_traga:
                r1_txt = emoji_map.get(r1, r1)
                r2_txt = emoji_map.get(r2, r2)
                r3_txt = emoji_map.get(r3, r3)
                data_traga.append([r1_txt, r2_txt, r3_txt, str(veces)])
            table_traga = Table(data_traga, hAlign='LEFT', colWidths=[80, 80, 80, 80])
            table_traga.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#17a2b8")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ]))
            elements.append(table_traga)
            elements.append(Spacer(1, 12))

        # Estadísticas Ruleta - casillas apostadas y resultado
        # El modelo tiene campos 'apuesta' (casilla apostada) y 'resultado' (casilla resultado)
        ruleta_stats = db.session.query(
            ResultadosRuleta.apuesta,
            ResultadosRuleta.resultado,
            func.count(ResultadosRuleta.id)
        ).filter_by(id_usuario=user.id).group_by(
            ResultadosRuleta.apuesta,
            ResultadosRuleta.resultado
        ).all()

        if ruleta_stats:
            elements.append(Paragraph("Estadísticas Ruleta - Casillas Apostadas y Resultado:", styles['Heading4']))
            data_ruleta = [["Casilla Apostada", "Casilla Resultado", "Veces"]]
            for casilla_a, casilla_r, veces in ruleta_stats:
                data_ruleta.append([casilla_a, casilla_r, str(veces)])
            table_ruleta = Table(data_ruleta, hAlign='LEFT', colWidths=[120, 120, 80])
            table_ruleta.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#6f42c1")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ]))
            elements.append(table_ruleta)
            elements.append(Spacer(1, 18))    

    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
    buffer.seek(0)
    fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"Informe_Global_FNAFBET_{fecha_str}.pdf"

    return send_file(buffer, as_attachment=True, download_name=nombre_archivo, mimetype='application/pdf')

