"""Testes para utilitários e validações.

Testa validações de Excel, exportação PDF e outros utilitários.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from src.common.validators.exel_validator import ExcelValidator
from src.common.utils.pdf_export import PDFExporter
from src.common.utils.notification import NotificationManager


class TestExcelValidator:
    """Testes para ExcelValidator."""

    def test_validar_arquivo_excel_valido(self):
        """Testa validação de arquivo Excel válido."""
        # Cria um mock para o arquivo Excel
        mock_workbook = Mock()
        mock_sheet = Mock()
        mock_sheet.max_row = 10
        mock_sheet.max_column = 5
        mock_workbook.active = mock_sheet

        with patch('openpyxl.load_workbook', return_value=mock_workbook):
            validator = ExcelValidator()
            resultado = validator.validar_arquivo("test.xlsx")

            assert resultado["valido"] is True
            assert resultado["linhas"] == 10
            assert resultado["colunas"] == 5

    def test_validar_arquivo_excel_invalido(self):
        """Testa validação de arquivo Excel inválido."""
        with patch('openpyxl.load_workbook', side_effect=Exception("Arquivo inválido")):
            validator = ExcelValidator()
            resultado = validator.validar_arquivo("invalid.xlsx")

            assert resultado["valido"] is False
            assert "Arquivo inválido" in resultado["erro"]

    def test_validar_colunas_obrigatorias(self):
        """Testa validação de colunas obrigatórias."""
        mock_workbook = Mock()
        mock_sheet = Mock()
        mock_sheet.max_row = 10
        mock_sheet.max_column = 5

        # Mock para iter_rows retornando cabeçalhos
        mock_sheet.iter_rows.return_value = [
            [Mock(value="Coluna1"), Mock(value="Coluna2"), Mock(value="Coluna3")]
        ]

        mock_workbook.active = mock_sheet

        with patch('openpyxl.load_workbook', return_value=mock_workbook):
            validator = ExcelValidator()
            resultado = validator.validar_arquivo("test.xlsx")

            assert resultado["valido"] is True
            assert "Coluna1" in resultado["colunas"]
            assert "Coluna2" in resultado["colunas"]
            assert "Coluna3" in resultado["colunas"]

    def test_validar_dados_numericos(self):
        """Testa validação de dados numéricos."""
        mock_workbook = Mock()
        mock_sheet = Mock()
        mock_sheet.max_row = 3
        mock_sheet.max_column = 3

        # Mock para iter_rows retornando dados
        mock_sheet.iter_rows.return_value = [
            [Mock(value="Coluna1"), Mock(value="Coluna2"), Mock(value="Coluna3")],
            [Mock(value="100"), Mock(value="200"), Mock(value="300")],
            [Mock(value="400"), Mock(value="500"), Mock(value="600")]
        ]

        mock_workbook.active = mock_sheet

        with patch('openpyxl.load_workbook', return_value=mock_workbook):
            validator = ExcelValidator()
            resultado = validator.validar_arquivo("test.xlsx")

            assert resultado["valido"] is True
            assert resultado["linhas"] == 3


class TestPDFExporter:
    """Testes para PDFExporter."""

    def test_exportar_mapa_assiduidade_pdf(self):
        """Testa exportação de mapa de assiduidade para PDF."""
        # Cria dados de teste
        mapa_data = {
            "mes": 1,
            "ano": 2024,
            "total_dias_trabalho": 20,
            "total_km": 500.0,
            "total_ips": 160,
            "total_faturacao": 2500.0,
            "linhas": [
                {
                    "dia": 1,
                    "dia_semana": "Segunda-feira",
                    "tipo": "trabalho",
                    "ips": 8,
                    "valor_sem_iva": 100.0,
                    "km": 25.0,
                    "locais": "Lisboa",
                }
            ]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "mapa_assiduidade.pdf")

            exporter = PDFExporter()
            resultado = exporter.exportar_mapa_assiduidade(mapa_data, output_path)

            assert resultado["sucesso"] is True
            assert os.path.exists(output_path)
            assert resultado["caminho"] == output_path

    def test_exportar_mapa_taxas_pdf(self):
        """Testa exportação de mapa de taxas para PDF."""
        # Cria dados de teste
        mapa_data = {
            "mes": 1,
            "ano": 2024,
            "total_setubal": 1000.0,
            "total_santarem": 500.0,
            "total_evora": 250.0,
            "total_ips": 80,
            "total_dividas": 100.0,
            "total_faturacao": 1750.0,
            "linhas": [
                {
                    "ordem": 1,
                    "recibo": 100,
                    "setubal": 500.0,
                    "santarem": 250.0,
                    "evora": 125.0,
                    "ips": 40,
                    "dividas": 50.0,
                }
            ]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "mapa_taxas.pdf")

            exporter = PDFExporter()
            resultado = exporter.exportar_mapa_taxas(mapa_data, output_path)

            assert resultado["sucesso"] is True
            assert os.path.exists(output_path)
            assert resultado["caminho"] == output_path

    def test_exportar_pdf_erro_arquivo(self):
        """Testa erro ao exportar PDF para caminho inválido."""
        mapa_data = {"mes": 1, "ano": 2024}

        # Tenta exportar para um caminho inválido
        with pytest.raises(Exception):
            exporter = PDFExporter()
            exporter.exportar_mapa_assiduidade(mapa_data, "/invalid/path/file.pdf")


class TestNotificationManager:
    """Testes para NotificationManager."""

    def test_enviar_notificacao_sucesso(self):
        """Testa envio de notificação de sucesso."""
        with patch('src.common.utils.notification.logger') as mock_logger:
            manager = NotificationManager()
            manager.enviar_sucesso("Operação concluída com sucesso")

            mock_logger.info.assert_called_once_with("Operação concluída com sucesso")

    def test_enviar_notificacao_erro(self):
        """Testa envio de notificação de erro."""
        with patch('src.common.utils.notification.logger') as mock_logger:
            manager = NotificationManager()
            manager.enviar_erro("Ocorreu um erro na operação")

            mock_logger.error.assert_called_once_with("Ocorreu um erro na operação")

    def test_enviar_notificacao_aviso(self):
        """Testa envio de notificação de aviso."""
        with patch('src.common.utils.notification.logger') as mock_logger:
            manager = NotificationManager()
            manager.enviar_aviso("Atenção: operação incompleta")

            mock_logger.warning.assert_called_once_with("Atenção: operação incompleta")

    def test_enviar_notificacao_debug(self):
        """Testa envio de notificação de debug."""
        with patch('src.common.utils.notification.logger') as mock_logger:
            manager = NotificationManager()
            manager.enviar_debug("Detalhes da operação")

            mock_logger.debug.assert_called_once_with("Detalhes da operação")

    def test_formatar_mensagem(self):
        """Testa formatação de mensagens."""
        manager = NotificationManager()

        mensagem = manager.formatar_mensagem("sucesso", "Operação concluída")
        assert "SUCESSO" in mensagem
        assert "Operação concluída" in mensagem

        mensagem = manager.formatar_mensagem("erro", "Operação falhou")
        assert "ERRO" in mensagem
        assert "Operação falhou" in mensagem

    def test_notificacao_com_dados(self):
        """Testa notificação com dados adicionais."""
        with patch('src.common.utils.notification.logger') as mock_logger:
            manager = NotificationManager()

            dados = {"arquivo": "test.xlsx", "linhas": 100}
            manager.enviar_sucesso("Arquivo processado", dados)

            # Verifica se os dados foram incluídos na mensagem
            args = mock_logger.info.call_args[0][0]
            assert "test.xlsx" in args
            assert "100" in args


class TestUtilsIntegracao:
    """Testes de integração para utilitários."""

    def test_fluxo_completo_validacao_exportacao(self):
        """Testa fluxo completo: validação Excel → exportação PDF."""
        # 1. Validação do Excel
        mock_workbook = Mock()
        mock_sheet = Mock()
        mock_sheet.max_row = 10
        mock_sheet.max_column = 5
        mock_workbook.active = mock_sheet

        with patch('openpyxl.load_workbook', return_value=mock_workbook):
            validator = ExcelValidator()
            resultado_validacao = validator.validar_arquivo("test.xlsx")

            assert resultado_validacao["valido"] is True

        # 2. Exportação para PDF
        mapa_data = {
            "mes": 1,
            "ano": 2024,
            "total_dias_trabalho": 10,
            "linhas": []
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "mapa.pdf")

            exporter = PDFExporter()
            resultado_exportacao = exporter.exportar_mapa_assiduidade(mapa_data, output_path)

            assert resultado_exportacao["sucesso"] is True
            assert os.path.exists(output_path)

    def test_notificacoes_em_cascata(self):
        """Testa notificações em cascata para diferentes operações."""
        with patch('src.common.utils.notification.logger') as mock_logger:
            manager = NotificationManager()

            # Simula uma sequência de operações
            manager.enviar_sucesso("Início da operação")
            manager.enviar_aviso("Processando dados")
            manager.enviar_sucesso("Operação concluída")

            # Verifica todas as chamadas
            assert mock_logger.info.call_count == 2  # início e conclusão
            assert mock_logger.warning.call_count == 1  # aviso

    def test_erro_em_validacao_excel(self):
        """Testa tratamento de erro em validação Excel."""
        with patch('openpyxl.load_workbook', side_effect=Exception("Erro de leitura")):
            with patch('src.common.utils.notification.logger') as mock_logger:
                validator = ExcelValidator()
                manager = NotificationManager()

                try:
                    validator.validar_arquivo("invalid.xlsx")
                except Exception as e:
                    manager.enviar_erro(f"Erro ao validar arquivo: {str(e)}")

                mock_logger.error.assert_called_once()
                args = mock_logger.error.call_args[0][0]
                assert "Erro ao validar arquivo" in args
