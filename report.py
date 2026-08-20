from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import datetime
import os

def generate_pdf_report(user_name, tasks):
    """Generate a PDF progress report"""
    
    # Create reports directory if it doesn't exist
    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'Study_Report_{user_name.replace(" ", "_")}_{timestamp}.pdf'
    filepath = os.path.join('reports', filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(filepath, pagesize=letter,
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=6,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2e5c8a'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    normal_style = styles['Normal']
    
    # Title
    elements.append(Paragraph('📚 Student Study Progress Report', title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Student info
    student_info = f'<b>Student:</b> {user_name}<br/><b>Date:</b> {datetime.now().strftime("%B %d, %Y")}'
    elements.append(Paragraph(student_info, normal_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Calculate statistics
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t[5] == 'completed'])
    pending_tasks = total_tasks - completed_tasks
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Statistics section
    elements.append(Paragraph('📊 Progress Statistics', heading_style))
    
    # Statistics table
    stats_data = [
        ['Metric', 'Value'],
        ['Total Tasks', str(total_tasks)],
        ['Completed', str(completed_tasks)],
        ['Pending', str(pending_tasks)],
        ['Completion Rate', f'{completion_rate:.1f}%']
    ]
    
    stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Upcoming tasks
    if tasks:
        elements.append(Paragraph('🎯 Upcoming Tasks (Next 7 Days)', heading_style))
        
        upcoming_tasks = [t for t in tasks if t[5] != 'completed'][:5]
        
        if upcoming_tasks:
            task_data = [['Task', 'Deadline', 'Status']]
            
            for task in upcoming_tasks:
                status = '✓ Completed' if task[5] == 'completed' else '⏳ Pending'
                task_data.append([
                    task[2][:30],  # Title (truncate)
                    task[4],       # Deadline
                    status
                ])
            
            task_table = Table(task_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
            task_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e5c8a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f8f8')])
            ]))
            
            elements.append(task_table)
        else:
            elements.append(Paragraph('✅ All tasks completed!', normal_style))
        
        elements.append(Spacer(1, 0.3*inch))
    
    # Recommendations
    elements.append(Paragraph('💡 Study Recommendations', heading_style))
    
    recommendations = []
    
    if completion_rate < 30:
        recommendations.append('• Focus on getting started with your pending tasks')
    elif completion_rate < 70:
        recommendations.append('• Keep up the momentum! You\'re making good progress')
    else:
        recommendations.append('• Excellent progress! Keep maintaining this pace')
    
    recommendations.append('• Review completed tasks to reinforce learning')
    recommendations.append('• Break large tasks into smaller, manageable chunks')
    
    for rec in recommendations:
        elements.append(Paragraph(rec, normal_style))
        elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Footer
    footer_text = f'<font size=9 color="grey">Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} by Student Study Planner</font>'
    elements.append(Paragraph(footer_text, normal_style))
    
    # Build PDF
    doc.build(elements)
    
    return filepath
