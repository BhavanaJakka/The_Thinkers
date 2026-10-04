import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

def generate_pdf_report(scan_data: dict) -> bytes:
    """
    Generates an executive PDF report for a Deptrix scan using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#c49a6c'),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#888888'),
        spaceAfter=12
    )

    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#c49a6c'),
        spaceBefore=14,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#111111')
    )

    body_bold = ParagraphStyle(
        'BodyDarkBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    danger_style = ParagraphStyle(
        'DangerText',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#d32f2f')
    )

    safe_style = ParagraphStyle(
        'SafeText',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#2e7d32')
    )

    elements = []

    # Title & Subtitle Header
    elements.append(Paragraph("DEPTRIX | Software Supply Chain Security Report", title_style))
    elements.append(Paragraph("Official Supply Chain Audit & Risk Assessment Report", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#c49a6c'), spaceAfter=12))

    # Project metadata table
    summary = scan_data.get('summary', {})
    risk_score = scan_data.get('risk_score', 0)
    verdict = summary.get('risk_level', 'Safe')

    score_color = '#d32f2f' if risk_score >= 70 else '#ed6c02' if risk_score >= 30 else '#2e7d32'

    meta_table_data = [
        [
            Paragraph(f"<b>Project Title:</b> {scan_data.get('project_name', 'N/A')}", body_style),
            Paragraph(f"<b>Overall Risk Score:</b> <font color='{score_color}'><b>{risk_score} / 100</b></font>", body_style)
        ],
        [
            Paragraph(f"<b>Scan ID:</b> {scan_data.get('scan_id', scan_data.get('id', 'N/A'))}", body_style),
            Paragraph(f"<b>Security Verdict:</b> <b>{verdict}</b>", body_style)
        ],
        [
            Paragraph(f"<b>Ecosystem:</b> {scan_data.get('ecosystem', 'N/A')}", body_style),
            Paragraph(f"<b>Total Dependencies:</b> {scan_data.get('total_dependencies', summary.get('total_dependencies', 0))}", body_style)
        ],
        [
            Paragraph(f"<b>Date Completed:</b> {scan_data.get('created_at', scan_data.get('date', 'N/A'))}", body_style),
            Paragraph(f"<b>Audit Engine:</b> Live OSV.dev & Typosquat Heuristics", body_style)
        ]
    ]

    t_meta = Table(meta_table_data, colWidths=[270, 270])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f9f7f5')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#c49a6c')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 10))

    # Metrics Grid Table
    metrics_data = [[
        Paragraph("<b>Critical Vulns</b>", body_style),
        Paragraph("<b>Suspicious Signals</b>", body_style),
        Paragraph("<b>License Flags</b>", body_style),
        Paragraph("<b>Attack Paths</b>", body_style)
    ], [
        Paragraph(f"<font color='#d32f2f'><b>{summary.get('critical_vulns', 0)}</b></font>", body_bold),
        Paragraph(f"<font color='#ed6c02'><b>{summary.get('suspicious_packages', len(scan_data.get('suspicious_signals', [])))}</b></font>", body_bold),
        Paragraph(f"<font color='#c49a6c'><b>{summary.get('license_conflicts', len(scan_data.get('license_findings', [])))}</b></font>", body_bold),
        Paragraph(f"<font color='#2e7d32'><b>{summary.get('attack_path_count', len(scan_data.get('attack_paths', [])))}</b></font>", body_bold)
    ]]

    t_metrics = Table(metrics_data, colWidths=[135, 135, 135, 135])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ffffff')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e0e0e0'))
    ]))
    elements.append(t_metrics)
    elements.append(Spacer(1, 14))

    # 1. Vulnerabilities Section
    elements.append(Paragraph("1. Vulnerability Findings (OSV.dev Advisories)", h2_style))
    findings = scan_data.get('findings', [])
    if findings:
        f_table_data = [[
            Paragraph("<b>Package</b>", body_bold),
            Paragraph("<b>OSV / CVE ID</b>", body_bold),
            Paragraph("<b>Severity</b>", body_bold),
            Paragraph("<b>Fix Version</b>", body_bold),
            Paragraph("<b>Summary</b>", body_bold)
        ]]
        for f in findings:
            f_table_data.append([
                Paragraph(f"{f.get('dependency_name')} ({f.get('dependency_version')})", body_style),
                Paragraph(str(f.get('osv_id', 'N/A')), body_style),
                Paragraph(f"<font color='#d32f2f'><b>{f.get('severity')}</b></font>", body_style),
                Paragraph(f"<font color='#2e7d32'><b>{f.get('fixed_version', 'N/A')}</b></font>", body_style),
                Paragraph(str(f.get('summary', ''))[:90], body_style)
            ])
        t_find = Table(f_table_data, colWidths=[110, 95, 65, 75, 195])
        t_find.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0ece8')),
            ('PADDING', (0,0), (-1,-1), 5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc'))
        ]))
        elements.append(t_find)
    else:
        elements.append(Paragraph("✓ No security vulnerability advisories detected.", safe_style))

    elements.append(Spacer(1, 12))

    # 2. Suspicious Signals Section
    elements.append(Paragraph("2. Typosquatting & Malware Signals", h2_style))
    suspicious = scan_data.get('suspicious_signals', [])
    if suspicious:
        s_table_data = [[
            Paragraph("<b>Dependency</b>", body_bold),
            Paragraph("<b>Signal Type</b>", body_bold),
            Paragraph("<b>Severity</b>", body_bold),
            Paragraph("<b>Description</b>", body_bold)
        ]]
        for s in suspicious:
            s_table_data.append([
                Paragraph(str(s.get('dependency_name')), body_bold),
                Paragraph(str(s.get('signal_type')), body_style),
                Paragraph(f"<font color='#d32f2f'><b>{s.get('severity')}</b></font>", body_style),
                Paragraph(str(s.get('description')), body_style)
            ])
        t_susp = Table(s_table_data, colWidths=[110, 110, 70, 250])
        t_susp.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#fde8e8')),
            ('PADDING', (0,0), (-1,-1), 5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e57373'))
        ]))
        elements.append(t_susp)
    else:
        elements.append(Paragraph("✓ No typosquatting malware or malicious install hook signals detected.", safe_style))

    elements.append(Spacer(1, 12))

    # 3. Dependency Inventory Section
    deps = scan_data.get('dependencies', [])
    elements.append(Paragraph(f"3. Scanned Dependency Inventory ({len(deps)})", h2_style))
    if deps:
        inv_table_data = [[
            Paragraph("<b>Package Name</b>", body_bold),
            Paragraph("<b>Version</b>", body_bold),
            Paragraph("<b>Type</b>", body_bold),
            Paragraph("<b>License</b>", body_bold),
            Paragraph("<b>Security Status</b>", body_bold)
        ]]
        for d in deps:
            is_vuln = any(kw in str(d.get('status', '')) for kw in ['VULNERABLE', 'MALWARE', 'RISK'])
            st_style = danger_style if is_vuln else safe_style
            dep_type = "Direct" if d.get('is_direct') else f"Transitive (Depth {d.get('depth', 2)})"

            inv_table_data.append([
                Paragraph(str(d.get('name')), body_bold),
                Paragraph(str(d.get('version', 'N/A')), body_style),
                Paragraph(dep_type, body_style),
                Paragraph(str(d.get('license', 'MIT')), body_style),
                Paragraph(str(d.get('status', 'SAFE')), st_style)
            ])

        t_inv = Table(inv_table_data, colWidths=[130, 70, 110, 90, 140])
        t_inv.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0ece8')),
            ('PADDING', (0,0), (-1,-1), 4.5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd'))
        ]))
        elements.append(t_inv)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
