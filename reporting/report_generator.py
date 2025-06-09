import os
from pandas import DataFrame

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

from .utils import convert_to_eat, ffloat, fpos

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()

    def generate_report(self, best_results, filename=None, *, symbol=None, interval=None, start_time=None, end_time=None):
        """Generate a PDF report.

        If ``filename`` is not provided a name will be constructed from
        ``symbol``, ``interval``, ``start_time`` and ``end_time`` and saved
        under the ``reports`` directory.
        """
        if filename is None:
            parts = [symbol, start_time, end_time, interval]
            parts = [str(p).replace(' ', '').replace(',', '-') for p in parts if p]
            base = "-".join(parts) if parts else "trading_system_report"
            filename = f"reports/{base}.pdf"

        # Ensure the reports directory exists in case a custom filename is used
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []

        # Title
        elements.append(Paragraph("Trading System Optimization Report", self.styles['Title']))

        for idx, (strategy_name, result) in enumerate(best_results.items()):
            elements.append(Paragraph(f"Strategy: {strategy_name}", self.styles['Heading2']))
            
            # Parameters table
            param_data = [['Parameter', 'Value']] + list(zip(result['params'].keys(), result['params'].values()))
            param_table = Table(param_data)
            param_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(param_table)

            # Performance tables
            perf_sections = []
            if 'performance' in result:
                perf_sections.append(('Performance', result['performance']))
            else:
                if 'train_performance' in result:
                    perf_sections.append(('Train Performance', result['train_performance']))
                if 'test_performance' in result:
                    perf_sections.append(('Test Performance', result['test_performance']))

            for heading, perf in perf_sections:
                elements.append(Paragraph(heading, self.styles['Heading3']))
                perf_data = [['Metric', 'Value']] + list(perf.items())
                perf_table = Table(perf_data)
                perf_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 12),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(perf_table)
            
            # Trades table
            if 'trades' in result:
                elements.append(Paragraph("Trades", self.styles['Heading2']))
                trade_data = [['Entry Time', 'Entry Price', 'Position', 'Exit Time', 'Exit Price', 'PROFIT/LOSS', 'Size', "CAPITAL"]] + [
                    [convert_to_eat(trade['entry_time']), ffloat(trade['entry_price']), fpos(trade['position']), convert_to_eat(trade['exit_time']), ffloat(trade['exit_price']), ffloat(trade['profit_loss']), ffloat(trade['size']), ffloat(trade['remaining_capital'])]
                    for trade in result['trades']
                ]
                trade_table = Table(trade_data)
                trade_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 12),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(trade_table)
                try:
                    DataFrame(result["trades"]).to_csv("./data/trades.csv", index=False)
                except Exception:
                    print("Failed to save trades")

            # Add a page break between strategies
            if idx < len(best_results) - 1:
                elements.append(PageBreak())

        doc.build(elements)
        print(f"Report generated: {filename}")
