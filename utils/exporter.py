import csv
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from PySide6.QtWidgets import QMessageBox

class Exporter:
    @staticmethod
    def export_csv(file_path, table_widget):
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                headers = [table_widget.horizontalHeaderItem(i).text() for i in range(table_widget.columnCount())]
                writer.writerow(headers)

                for row in range(table_widget.rowCount()):
                    row_data = []
                    for column in range(table_widget.columnCount()):
                        item = table_widget.item(row, column)
                        if item is not None:
                            row_data.append(item.text())
                        else:
                            row_data.append('')
                    writer.writerow(row_data)
            return True, "Export CSV berhasil!"
        except Exception as e:
            return False, f"Gagal export CSV: {str(e)}"

    @staticmethod
    def export_pdf(file_path, table_widget, title="Laporan Goldata"):
        try:
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            elements = []

            styles = getSampleStyleSheet()
            elements.append(Paragraph(title, styles['Title']))
            elements.append(Spacer(1, 12))

            headers = [table_widget.horizontalHeaderItem(i).text() for i in range(table_widget.columnCount())]
            data = [headers]

            for row in range(table_widget.rowCount()):
                row_data = []
                for column in range(table_widget.columnCount()):
                    item = table_widget.item(row, column)
                    if item is not None:
                        row_data.append(item.text())
                    else:
                        row_data.append('')
                data.append(row_data)

            t = Table(data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            elements.append(t)
            doc.build(elements)
            return True, "Export PDF berhasil!"
        except Exception as e:
            return False, f"Gagal export PDF: {str(e)}"
