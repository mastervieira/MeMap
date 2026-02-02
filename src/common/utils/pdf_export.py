"""Utilitários para exportação de dados para PDF.

Usa ReportLab para gerar PDFs profissionais com tabelas formatadas.
"""

from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class PDFExporter:
    """Classe para exportar dados para PDF com formatação profissional."""

    def __init__(self, filename: str = "output.pdf", title: str = "Relatório") -> None:
        """Inicializa o exportador PDF.

        Args:
            filename: Caminho completo do arquivo PDF a ser gerado.
            title: Título do documento.
        """
        self.filename = filename
        self.title = title
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )
        self.styles = getSampleStyleSheet()
        self.elements: list[Any] = []

    def add_title(self, text: str) -> None:
        """Adiciona título ao documento.

        Args:
            text: Texto do título.
        """
        title_style = self.styles["Title"]
        self.elements.append(Paragraph(text, title_style))
        self.elements.append(Spacer(1, 0.5 * cm))

    def add_heading(self, text: str, level: int = 1) -> None:
        """Adiciona cabeçalho ao documento.

        Args:
            text: Texto do cabeçalho.
            level: Nível do cabeçalho (1 ou 2).
        """
        style_name = f"Heading{level}"
        self.elements.append(Paragraph(text, self.styles[style_name]))
        self.elements.append(Spacer(1, 0.3 * cm))

    def add_paragraph(self, text: str) -> None:
        """Adiciona parágrafo ao documento.

        Args:
            text: Texto do parágrafo.
        """
        self.elements.append(Paragraph(text, self.styles["Normal"]))
        self.elements.append(Spacer(1, 0.2 * cm))

    def add_table(
        self,
        data: list[list[Any]],
        col_widths: list[float] | None = None,
        style: str = "default",
    ) -> None:
        """Adiciona tabela formatada ao documento.

        Args:
            data: Lista de listas com os dados da tabela.
                  Primeira linha deve conter os cabeçalhos.
            col_widths: Lista com larguras das colunas em cm.
                       Se None, usa largura automática.
            style: Estilo da tabela ('default', 'colorful', 'minimal').
        """
        # Converte dados para strings
        table_data = [
            [str(cell) if cell is not None else "" for cell in row]
            for row in data
        ]

        # Cria tabela
        if col_widths:
            col_widths_units = [w * cm for w in col_widths]
            table = Table(table_data, colWidths=col_widths_units)
        else:
            table = Table(table_data)

        # Aplica estilo
        table_style = self._get_table_style(style, len(table_data))
        table.setStyle(table_style)

        self.elements.append(table)
        self.elements.append(Spacer(1, 0.5 * cm))

    def _get_table_style(self, style_name: str, num_rows: int) -> TableStyle:
        """Retorna estilo de tabela baseado no nome.

        Args:
            style_name: Nome do estilo.
            num_rows: Número de linhas da tabela.

        Returns:
            TableStyle configurado.
        """
        if style_name == "default":
            return TableStyle(
                [
                    # Cabeçalho
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    # Dados
                    ("BACKGROUND", (0, 1), (-1, -2), colors.beige),
                    ("TEXTCOLOR", (0, 1), (-1, -2), colors.black),
                    ("ALIGN", (0, 1), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 1), (-1, -2), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -2), 9),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    # Linha de totais (última linha)
                    (
                        "BACKGROUND",
                        (0, -1),
                        (-1, -1),
                        colors.lightgoldenrodyellow,
                    ),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, -1), (-1, -1), 10),
                    ("LINEABOVE", (0, -1), (-1, -1), 2, colors.black),
                    # Bordas - espessuras melhoradas para impressão
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#7F8C8D")),
                    ("BOX", (0, 0), (-1, -1), 2, colors.black),
                    # Padding
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )

        elif style_name == "colorful":
            return TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#2C3E50"),
                    ),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -2),
                        [colors.white, colors.HexColor("#ECF0F1")],
                    ),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#7F8C8D")),
                    ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#7F8C8D")),
                ]
            )

        else:  # minimal
            return TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("LINEBELOW", (0, 0), (-1, 0), 1, colors.black),
                    ("LINEBELOW", (0, -1), (-1, -1), 1, colors.black),
                ]
            )

    def add_spacer(self, height_cm: float = 1.0) -> None:
        """Adiciona espaço em branco.

        Args:
            height_cm: Altura do espaço em centímetros.
        """
        self.elements.append(Spacer(1, height_cm * cm))

    def add_page_break(self) -> None:
        """Adiciona quebra de página."""
        self.elements.append(PageBreak())

    def build(self) -> bool:
        """Gera o arquivo PDF.

        Returns:
            True se sucesso, False caso contrário.
        """
        try:
            self.doc.build(self.elements)
            print(f"[PDFExporter] PDF gerado com sucesso: {self.filename}")
            return True
        except Exception as e:
            print(f"[PDFExporter] Erro ao gerar PDF: {e}")
            import traceback

            traceback.print_exc()
            return False

    def exportar_mapa_assiduidade(self, mapa_data: dict, output_path: str) -> dict:
        """Exporta mapa de assiduidade para PDF.

        Args:
            mapa_data: Dados do mapa.
            output_path: Caminho de saída.

        Returns:
            Dict com resultado.
        """
        try:
            # Atualiza configuração
            self.filename = output_path
            self.doc.filename = output_path

            # Título
            mes = mapa_data.get('mes')
            ano = mapa_data.get('ano')
            self.add_title(f"Mapa de Assiduidade - {mes}/{ano}")

            # Totais
            self.add_heading("Resumo", level=2)
            totais = [
                ["Dias Trabalho", str(mapa_data.get('total_dias_trabalho', 0))],
                ["Total KM", f"{mapa_data.get('total_km', 0):.2f}"],
                ["Total IPS", str(mapa_data.get('total_ips', 0))],
                ["Total Faturação", f"{mapa_data.get('total_faturacao', 0):.2f} €"]
            ]
            self.add_table(totais, col_widths=[5, 5])

            # Detalhes
            self.add_heading("Detalhes Diários", level=2)
            headers = ["Dia", "Semana", "Tipo", "IPS", "Valor", "KM", "Locais"]
            rows = []
            for linha in mapa_data.get('linhas', []):
                rows.append([
                    str(linha.get('dia', '')),
                    linha.get('dia_semana', ''),
                    linha.get('tipo', ''),
                    str(linha.get('ips', '')),
                    f"{linha.get('valor_sem_iva', 0):.2f}",
                    f"{linha.get('km', 0):.2f}",
                    linha.get('locais', '') or ''
                ])

            self.add_table([headers] + rows, col_widths=[1.5, 3, 3, 1.5, 2.5, 2, 5])

            if self.build():
                return {"sucesso": True, "caminho": output_path}
            else:
                return {"sucesso": False, "erro": "Falha ao gerar PDF"}

        except Exception as e:
            return {"sucesso": False, "erro": str(e)}

    def exportar_mapa_taxas(self, mapa_data: dict, output_path: str) -> dict:
        """Exporta mapa de taxas para PDF.

        Args:
            mapa_data: Dados do mapa.
            output_path: Caminho de saída.

        Returns:
            Dict com resultado.
        """
        try:
            # Atualiza configuração
            self.filename = output_path
            self.doc.filename = output_path

            # Título
            mes = mapa_data.get('mes')
            ano = mapa_data.get('ano')
            self.add_title(f"Mapa de Taxas - {mes}/{ano}")

            # Totais
            self.add_heading("Resumo por Distrito", level=2)
            totais = [
                ["Setúbal", f"{mapa_data.get('total_setubal', 0):.2f} €"],
                ["Santarém", f"{mapa_data.get('total_santarem', 0):.2f} €"],
                ["Évora", f"{mapa_data.get('total_evora', 0):.2f} €"],
                ["Total IPS", str(mapa_data.get('total_ips', 0))],
                ["Total Faturação", f"{mapa_data.get('total_faturacao', 0):.2f} €"]
            ]
            self.add_table(totais, col_widths=[5, 5])

            # Detalhes
            self.add_heading("Detalhes por Recibo", level=2)
            headers = ["Ordem", "Recibo", "Setúbal", "Santarém", "Évora", "IPS", "Dívidas"]
            rows = []
            for linha in mapa_data.get('linhas', []):
                rows.append([
                    str(linha.get('ordem', '')),
                    str(linha.get('recibo', '')),
                    f"{linha.get('setubal', 0):.2f}",
                    f"{linha.get('santarem', 0):.2f}",
                    f"{linha.get('evora', 0):.2f}",
                    str(linha.get('ips', '')),
                    f"{linha.get('dividas', 0):.2f}"
                ])

            self.add_table([headers] + rows, col_widths=[2, 2, 3, 3, 3, 2, 3])

            if self.build():
                return {"sucesso": True, "caminho": output_path}
            else:
                return {"sucesso": False, "erro": "Falha ao gerar PDF"}

        except Exception as e:
            return {"sucesso": False, "erro": str(e)}


def export_table_to_pdf(
    filename: str,
    title: str,
    subtitle: str,
    headers: list[str],
    data: list[list[Any]],
    totals_row: list[Any] | None = None,
    col_widths: list[float] | None = None,
) -> bool:
    """Função auxiliar para exportar tabela simples para PDF.

    Args:
        filename: Caminho do arquivo PDF.
        title: Título do documento.
        subtitle: Subtítulo (ex: mês, ano, técnico).
        headers: Lista de cabeçalhos das colunas.
        data: Lista de listas com dados (sem cabeçalhos).
        totals_row: Linha de totais (opcional).
        col_widths: Larguras das colunas em cm (opcional).

    Returns:
        True se sucesso, False caso contrário.
    """
    exporter = PDFExporter(filename, title)

    # Título e subtítulo
    exporter.add_title(title)
    if subtitle:
        exporter.add_paragraph(subtitle)

    exporter.add_spacer(0.5)

    # Prepara dados da tabela
    table_data = [headers] + data
    if totals_row:
        table_data.append(totals_row)

    # Adiciona tabela
    exporter.add_table(table_data, col_widths=col_widths, style="default")

    # Gera PDF
    return exporter.build()
