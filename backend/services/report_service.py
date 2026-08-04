"""
Report generation service - creates PDF farm reports
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io

# KVK color palette
KVK_GREEN = colors.HexColor('#2E7D32')
KVK_LIGHT_GREEN = colors.HexColor('#66BB6A')
KVK_YELLOW = colors.HexColor('#F9A825')
KVK_DARK = colors.HexColor('#1B5E20')
KVK_BG = colors.HexColor('#F1F8E9')
KVK_GRAY = colors.HexColor('#546E7A')

def generate_farm_report(farmer_data: dict, weather: dict, market_prices: list,
                          advisory: dict, ml_results: dict, schemes: list) -> bytes:
    """Generate a comprehensive PDF farm report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
        title=f"KVK Farm Report - {farmer_data.get('name', 'Farmer')}",
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Styles ──────────────────────────────────────────────
    title_style = ParagraphStyle('KVKTitle', parent=styles['Normal'],
        fontSize=20, fontName='Helvetica-Bold', textColor=KVK_DARK,
        alignment=TA_CENTER, spaceAfter=4)
    subtitle_style = ParagraphStyle('KVKSub', parent=styles['Normal'],
        fontSize=11, fontName='Helvetica', textColor=KVK_GRAY,
        alignment=TA_CENTER, spaceAfter=2)
    section_style = ParagraphStyle('Section', parent=styles['Normal'],
        fontSize=13, fontName='Helvetica-Bold', textColor=colors.white,
        backColor=KVK_GREEN, spaceBefore=10, spaceAfter=6,
        leftIndent=6, rightIndent=6, leading=18)
    body_style = ParagraphStyle('Body', parent=styles['Normal'],
        fontSize=9.5, fontName='Helvetica', textColor=colors.HexColor('#263238'),
        spaceAfter=4, leading=14)
    bullet_style = ParagraphStyle('Bullet', parent=body_style,
        leftIndent=14, bulletIndent=4, bulletFontName='Helvetica',
        spaceAfter=3)
    small_style = ParagraphStyle('Small', parent=styles['Normal'],
        fontSize=8, fontName='Helvetica', textColor=KVK_GRAY)

    # ── Header ───────────────────────────────────────────────
    header_table = Table([[
        Paragraph("🌾", ParagraphStyle('icon', fontSize=28, alignment=TA_CENTER)),
        [
            Paragraph("KVK Krishak Seva Kendra", title_style),
            Paragraph("West Bengal — Automated Farm Advisory Report", subtitle_style),
            Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}", subtitle_style),
        ],
        Paragraph("ICAR", ParagraphStyle('icar', fontSize=11, fontName='Helvetica-Bold',
                                          textColor=KVK_GREEN, alignment=TA_CENTER)),
    ]], colWidths=[2*cm, 13*cm, 2.5*cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,-1), KVK_BG),
        ('ROUNDEDCORNERS', [6]),
        ('BOX', (0,0), (-1,-1), 1.5, KVK_GREEN),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2, color=KVK_GREEN))
    story.append(Spacer(1, 8))

    # ── Farmer Info ───────────────────────────────────────────
    story.append(Paragraph("  👤  Farmer Profile", section_style))
    info_data = [
        ["Field", "Details", "Field", "Details"],
        ["Farmer Name", farmer_data.get("name", "N/A"),
         "Village / Block", farmer_data.get("village", "N/A")],
        ["District", farmer_data.get("district", "N/A"),
         "Land Holding", f"{farmer_data.get('land_ha', 'N/A')} ha"],
        ["Primary Crop", farmer_data.get("primary_crop", "N/A"),
         "Irrigation", farmer_data.get("irrigation", "Canal/Tubewell")],
        ["KVK Contact", advisory.get("kvk_contact", "N/A"), "Season", advisory.get("season", "N/A")],
    ]
    info_table = Table(info_data, colWidths=[3.5*cm, 6*cm, 3.5*cm, 5*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), KVK_DARK),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BACKGROUND', (0,1), (0,-1), KVK_BG),
        ('BACKGROUND', (2,1), (2,-1), KVK_BG),
        ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,1), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#B0BEC5')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#FAFAFA')]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 8))

    # ── Weather ───────────────────────────────────────────────
    story.append(Paragraph("  🌤️  Current Weather & Forecast", section_style))
    w = weather
    weather_data = [
        ["Parameter", "Value", "Parameter", "Value"],
        ["Condition", w.get("condition", "N/A"), "Max Temp", f"{w.get('temp_max', '--')} °C"],
        ["Min Temp", f"{w.get('temp_min', '--')} °C", "Rainfall", f"{w.get('rainfall_mm', '--')} mm"],
        ["Humidity", f"{w.get('humidity_pct', '--')} %", "Wind Speed", f"{w.get('wind_kmh', '--')} km/h"],
    ]
    w_table = Table(weather_data, colWidths=[3.5*cm, 6*cm, 3.5*cm, 5*cm])
    w_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), KVK_DARK),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BACKGROUND', (0,1), (0,-1), KVK_BG),
        ('BACKGROUND', (2,1), (2,-1), KVK_BG),
        ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,1), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#B0BEC5')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#FAFAFA')]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(w_table)

    # 7-day forecast mini table
    forecast = w.get("forecast_7day", [])[:7]
    if forecast:
        story.append(Spacer(1, 6))
        story.append(Paragraph("7-Day Forecast:", ParagraphStyle('ForecastHead',
            fontSize=9, fontName='Helvetica-Bold', textColor=KVK_GRAY)))
        story.append(Spacer(1, 3))
        f_header = [Paragraph(d["day"][:3], small_style) for d in forecast]
        f_cond   = [Paragraph(d["condition"][:12], small_style) for d in forecast]
        f_temp   = [Paragraph(f"{d['temp_max']}°/{d['temp_min']}°", small_style) for d in forecast]
        f_table  = Table([f_header, f_cond, f_temp],
                         colWidths=[2.5*cm]*7)
        f_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), KVK_GREEN),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#CFD8DC')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F9FBE7'), colors.white]),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(f_table)
    story.append(Spacer(1, 8))

    # ── ML Recommendations ────────────────────────────────────
    if ml_results:
        story.append(Paragraph("  🤖  AI-Powered Crop Recommendations", section_style))
        recommendations = ml_results.get("recommendations", [])
        if recommendations:
            rec_data = [["Rank", "Recommended Crop", "AI Confidence", "Suitability"]]
            for i, rec in enumerate(recommendations, 1):
                conf = rec.get("confidence", 0)
                suit = "Excellent" if conf > 60 else ("Good" if conf > 35 else "Moderate")
                rec_data.append([str(i), rec.get("crop", ""), f"{conf}%", suit])
            rec_table = Table(rec_data, colWidths=[1.5*cm, 7*cm, 4*cm, 5*cm])
            rec_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), KVK_DARK),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#E8F5E9')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#B0BEC5')),
                ('ROWBACKGROUNDS', (0,2), (-1,-1), [colors.white, colors.HexColor('#FAFAFA')]),
                ('ALIGN', (2,0), (-1,-1), 'CENTER'),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(rec_table)

        yield_pred = ml_results.get("yield_prediction")
        if yield_pred and "predicted_yield_qtl_per_ha" in yield_pred:
            story.append(Spacer(1, 6))
            yld = yield_pred["predicted_yield_qtl_per_ha"]
            crop = yield_pred.get("crop", "Selected Crop")
            story.append(Paragraph(
                f"<b>Predicted Yield for {crop}:</b>  <font color='#2E7D32'>"
                f"{yld} quintal/ha  ({int(yld * 100)} kg/ha)</font>",
                body_style
            ))

        pest_data = ml_results.get("pest_risk", {})
        if pest_data:
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"<b>Pest Risk Assessment — {pest_data.get('crop', '')}:</b>", body_style))
            pests = pest_data.get("pest_risks", [])
            p_data = [["Pest", "Risk Level", "Recommended Action"]]
            for p in pests:
                risk = p.get("risk_level", "Low")
                color_map = {"High": "red", "Medium": "orange", "Low": "green"}
                risk_colored = f'<font color="{color_map.get(risk, "black")}">{risk}</font>'
                p_data.append([p.get("pest", ""), Paragraph(risk_colored, body_style),
                                Paragraph(p.get("recommendation", "")[:80], small_style)])
            p_table = Table(p_data, colWidths=[4.5*cm, 2.5*cm, 11*cm])
            p_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), KVK_DARK),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#B0BEC5')),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#FAFAFA')]),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('LEFTPADDING', (0,0), (-1,-1), 5),
            ]))
            story.append(p_table)
        story.append(Spacer(1, 8))

    # ── Market Prices ─────────────────────────────────────────
    story.append(Paragraph("  📊  Current Market Prices", section_style))
    price_data = [["Crop", "MSP (₹/qtl)", "Market Price", "Trend"]]
    for p in market_prices[:8]:
        price_data.append([
            p.get("crop", ""), str(p.get("msp", "N/A")),
            f"₹{p.get('market_price', 'N/A')}", p.get("trend", "→")
        ])
    p_table = Table(price_data, colWidths=[5*cm, 3.5*cm, 4*cm, 5*cm])
    p_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), KVK_DARK),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#B0BEC5')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#FAFAFA')]),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(p_table)
    story.append(Spacer(1, 8))

    # ── Advisory ─────────────────────────────────────────────
    story.append(Paragraph("  📋  Seasonal Agricultural Advisory", section_style))
    for i, adv in enumerate(advisory.get("advisories", []), 1):
        story.append(Paragraph(f"• {adv}", bullet_style))
    story.append(Spacer(1, 8))

    # ── Government Schemes ────────────────────────────────────
    story.append(Paragraph("  🏛️  Applicable Government Schemes", section_style))
    for scheme in schemes[:4]:
        scheme_data = [
            [Paragraph(f"<b>{scheme['name']}</b>", body_style),
             Paragraph(f"<b>Benefit:</b> {scheme['benefit']}", body_style)],
            [Paragraph(scheme['description'], small_style),
             Paragraph(f"<b>Apply at:</b> {scheme['apply_at']}", small_style)],
        ]
        s_table = Table(scheme_data, colWidths=[10*cm, 8*cm])
        s_table.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 0.8, KVK_LIGHT_GREEN),
            ('BACKGROUND', (0,0), (-1,0), KVK_BG),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('LINEBELOW', (0,0), (-1,0), 0.5, KVK_LIGHT_GREEN),
        ]))
        story.append(s_table)
        story.append(Spacer(1, 4))
    story.append(Spacer(1, 8))

    # ── Footer ───────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1.5, color=KVK_GREEN))
    story.append(Spacer(1, 4))
    footer_text = (
        "This report is auto-generated by the KVK Farmer Advisory System | "
        "ICAR-Krishi Vigyan Kendra, West Bengal | "
        "For expert advice, contact your nearest KVK centre | "
        f"Report Date: {datetime.now().strftime('%d/%m/%Y')}"
    )
    story.append(Paragraph(footer_text, ParagraphStyle('Footer',
        fontSize=7.5, fontName='Helvetica', textColor=KVK_GRAY, alignment=TA_CENTER)))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
