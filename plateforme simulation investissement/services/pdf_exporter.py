from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

class CreditPdfExporter:
    def export_amortissement(self, credit, amortissement: dict, output_path: str | Path) -> Path:
        """
        credit : objet Crédit avec au moins les attributs utiles à l'affichage
        amortissement : dict du type
            {
                "ANNEE": [...],
                "CAPITAL DEBUT": [...],
                "INTERETS": [...],
                "CAPITAL REMBOURSE": [...],
                "ANNUITE": [...],
                "CAPITAL FIN": [...]
            }
        output_path : chemin du pdf à créer
        """
        output_path = Path(output_path)

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=landscape(A4),
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
        )

        styles = getSampleStyleSheet()
        elements = []

        # ---- Titre
        elements.append(Paragraph("Tableau d'amortissement", styles["Title"]))
        elements.append(Spacer(1, 0.4 * cm))

        # ---- Résumé crédit
        def fmt_money(x):
            if x is None:
                return "-"
            return f"{float(x):,.2f} EUR".replace(",", " ")

        def fmt_val(x):
            return "-" if x is None else str(x)

        infos = [
            ["Montant emprunté", fmt_money(getattr(credit, "montant", None))],
            ["Taux annuel", f"{getattr(credit, 'taux_crédit_pct', '-')}" + " %"],
            ["Duree credit", f"{fmt_val(getattr(credit, 'durée_crédit_mois', None))} mois"],
            ["Duree differee", f"{fmt_val(getattr(credit, 'duree_diff_mois', None))} mois"],
            ["Mensualite constante", fmt_money(getattr(credit, "mensualite_constante", None))],
            ["Type", fmt_val(getattr(credit, "type", None))],
        ]

        info_table = Table(infos, colWidths=[5.5 * cm, 8.5 * cm])
        info_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f3f5")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cfd4da")),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#adb5bd")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.5 * cm))

        # ---- Préparation tableau amortissement
        colonnes = list(amortissement.keys())
        nb_lignes = len(amortissement[colonnes[0]]) if colonnes else 0

        data = [colonnes]

        for i in range(nb_lignes):
            row = []
            for col in colonnes:
                val = amortissement[col][i]
                if isinstance(val, (int, float)):
                    row.append(f"{val:,.2f}".replace(",", " "))
                else:
                    row.append(str(val))
            data.append(row)

        # Largeurs ajustables selon tes colonnes
        col_widths = []
        for col in colonnes:
            c = col.upper()
            if "ANNEE" in c or "MOIS" in c:
                col_widths.append(2.0 * cm)
            elif "TAUX" in c:
                col_widths.append(2.3 * cm)
            else:
                col_widths.append(4.0 * cm)

        amorti_table = Table(data, repeatRows=1, colWidths=col_widths)

        amorti_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3c88")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#ced4da")),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#adb5bd")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("ALIGN", (0, 1), (-1, -1), "RIGHT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))

        elements.append(amorti_table)

        doc.build(elements)
        return output_path