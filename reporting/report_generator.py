from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from .utils import convert_to_eat, ffloat, fpos

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()

    def generate_report(self, best_results, filename="reports/trading_system_report.pdf"):
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []

        # Title
        elements.append(Paragraph("Trading System Optimization Report", self.styles['Title']))

        for strategy_name, result in best_results.items():
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

            # Performance table
            perf_data = [['Metric', 'Value']] + list(result['performance'].items())
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
                result["trades"].to_csv("./data/trades.csv", index=False)
            except Exception:
                print("Failed to save trades")

        doc.build(elements)
        print(f"Report generated: {filename}")