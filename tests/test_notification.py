"""Testes para o gerenciador de notificações."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from src.common.utils.notification import NotificationManager


class TestNotificationManager:
    """Testa o gerenciador de notificações."""

    @pytest.fixture
    def notification_manager(self):
        """Fixture para NotificationManager."""
        return NotificationManager()

    def test_init_creates_logger(self, notification_manager):
        """Testa inicialização do logger."""
        assert notification_manager.logger is not None
        assert isinstance(notification_manager.logger, logging.Logger)

    def test_enviar_sucesso_formata_mensagem(self, notification_manager):
        """Testa envio de notificação de sucesso."""
        with patch.object(notification_manager.logger, 'info') as mock_info:
            notification_manager.enviar_sucesso("Operação realizada")
            mock_info.assert_called_once()
            call_args = mock_info.call_args[0][0]
            assert "[SUCESSO]" in call_args
            assert "Operação realizada" in call_args

    def test_enviar_sucesso_com_dados(self, notification_manager):
        """Testa envio de sucesso com dados adicionais."""
        with patch.object(notification_manager.logger, 'info') as mock_info:
            dados = {"usuario": "João", "ação": "create"}
            notification_manager.enviar_sucesso("Usuário criado", dados)
            call_args = mock_info.call_args[0][0]
            assert "[SUCESSO]" in call_args
            assert "usuario: João" in call_args
            assert "ação: create" in call_args

    def test_enviar_erro_formata_mensagem(self, notification_manager):
        """Testa envio de notificação de erro."""
        with patch.object(notification_manager.logger, 'error') as mock_error:
            notification_manager.enviar_erro("Erro ao processar")
            mock_error.assert_called_once()
            call_args = mock_error.call_args[0][0]
            assert "[ERRO]" in call_args
            assert "Erro ao processar" in call_args

    def test_enviar_erro_com_dados(self, notification_manager):
        """Testa envio de erro com dados adicionais."""
        with patch.object(notification_manager.logger, 'error') as mock_error:
            dados = {"código": 500, "serviço": "API"}
            notification_manager.enviar_erro("Falha no servidor", dados)
            call_args = mock_error.call_args[0][0]
            assert "[ERRO]" in call_args
            assert "código: 500" in call_args
            assert "serviço: API" in call_args

    def test_enviar_aviso_formata_mensagem(self, notification_manager):
        """Testa envio de notificação de aviso."""
        with patch.object(notification_manager.logger, 'warning') as mock_warning:
            notification_manager.enviar_aviso("Atenção necessária")
            mock_warning.assert_called_once()
            call_args = mock_warning.call_args[0][0]
            assert "[AVISO]" in call_args
            assert "Atenção necessária" in call_args

    def test_enviar_aviso_com_dados(self, notification_manager):
        """Testa envio de aviso com dados adicionais."""
        with patch.object(notification_manager.logger, 'warning') as mock_warning:
            dados = {"limite": "80%"}
            notification_manager.enviar_aviso("Limite atingido", dados)
            call_args = mock_warning.call_args[0][0]
            assert "[AVISO]" in call_args
            assert "limite: 80%" in call_args

    def test_enviar_debug_formata_mensagem(self, notification_manager):
        """Testa envio de notificação de debug."""
        with patch.object(notification_manager.logger, 'debug') as mock_debug:
            notification_manager.enviar_debug("Informação de debug")
            mock_debug.assert_called_once()
            call_args = mock_debug.call_args[0][0]
            assert "[DEBUG]" in call_args
            assert "Informação de debug" in call_args

    def test_enviar_debug_com_dados(self, notification_manager):
        """Testa envio de debug com dados adicionais."""
        with patch.object(notification_manager.logger, 'debug') as mock_debug:
            dados = {"variável": "teste", "valor": 123}
            notification_manager.enviar_debug("Estado da aplicação", dados)
            call_args = mock_debug.call_args[0][0]
            assert "[DEBUG]" in call_args
            assert "variável: teste" in call_args
            assert "valor: 123" in call_args

    def test_formatar_mensagem_sem_dados(self, notification_manager):
        """Testa formatação de mensagem sem dados adicionais."""
        resultado = notification_manager.formatar_mensagem(
            "INFO",
            "Mensagem de teste"
        )
        assert resultado == "[INFO] Mensagem de teste"

    def test_formatar_mensagem_com_dados(self, notification_manager):
        """Testa formatação de mensagem com dados adicionais."""
        dados = {"chave1": "valor1", "chave2": "valor2"}
        resultado = notification_manager.formatar_mensagem(
            "TEST",
            "Mensagem",
            dados
        )
        assert "[TEST] Mensagem" in resultado
        assert "chave1: valor1" in resultado
        assert "chave2: valor2" in resultado

    def test_formatar_mensagem_com_dados_vazio(self, notification_manager):
        """Testa formatação com dicionário vazio."""
        resultado = notification_manager.formatar_mensagem(
            "TEST",
            "Mensagem",
            {}
        )
        assert resultado == "[TEST] Mensagem"

    def test_formatar_mensagem_tipos_diferentes(self, notification_manager):
        """Testa formatação com tipos diferentes de dados."""
        dados = {
            "string": "texto",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "none": None
        }
        resultado = notification_manager.formatar_mensagem(
            "TYPE",
            "Tipos",
            dados
        )
        assert "[TYPE] Tipos" in resultado
        assert "string: texto" in resultado
        assert "int: 42" in resultado
        assert "float: 3.14" in resultado
        assert "bool: True" in resultado
        assert "none: None" in resultado

    def test_enviar_sucessos_multiplos(self, notification_manager):
        """Testa envio de múltiplas notificações de sucesso."""
        with patch.object(notification_manager.logger, 'info') as mock_info:
            notification_manager.enviar_sucesso("Msg 1")
            notification_manager.enviar_sucesso("Msg 2")
            notification_manager.enviar_sucesso("Msg 3")
            assert mock_info.call_count == 3

    def test_notificacoes_diferentes_tipos(self, notification_manager):
        """Testa envio de notificações de diferentes tipos."""
        with patch.object(notification_manager.logger, 'info') as mock_info:
            with patch.object(notification_manager.logger, 'error') as mock_error:
                with patch.object(notification_manager.logger, 'warning') as mock_warning:
                    with patch.object(notification_manager.logger, 'debug') as mock_debug:
                        notification_manager.enviar_sucesso("Sucesso")
                        notification_manager.enviar_erro("Erro")
                        notification_manager.enviar_aviso("Aviso")
                        notification_manager.enviar_debug("Debug")

                        assert mock_info.call_count == 1
                        assert mock_error.call_count == 1
                        assert mock_warning.call_count == 1
                        assert mock_debug.call_count == 1

    def test_formatar_mensagem_dados_ordenacao(self, notification_manager):
        """Testa que dados são incluídos na mensagem."""
        dados = {"a": 1, "b": 2}
        resultado = notification_manager.formatar_mensagem("TEST", "Msg", dados)
        # Verifica que ambas as chaves estão presentes
        assert "a: 1" in resultado
        assert "b: 2" in resultado

    def test_enviar_com_mensagem_especial(self, notification_manager):
        """Testa envio com mensagens que contêm caracteres especiais."""
        with patch.object(notification_manager.logger, 'info') as mock_info:
            mensagem = "Operação com caracteres: ñ, ü, @, #, $, %"
            notification_manager.enviar_sucesso(mensagem)
            call_args = mock_info.call_args[0][0]
            assert mensagem in call_args

    def test_logger_name(self, notification_manager):
        """Testa que o logger tem o nome correto."""
        assert notification_manager.logger.name == "src.common.utils.notification"
