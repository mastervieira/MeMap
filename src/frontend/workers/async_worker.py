"""
Worker assíncrono para tarefas pesadas que não bloqueiam a interface.
Utiliza QThread para manter a Main Thread fluida a 60fps.
"""

import asyncio
import time
from typing import Optional

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import QApplication


class WorkerSignals(QObject):
    """Sinais do worker para comunicação com a UI."""

    # Sinais principais
    started = Signal()
    finished = Signal()
    result = Signal(object)
    error = Signal(str)

    # Sinais de progresso
    progress = Signal(int)  # 0-100
    progress_text = Signal(str)

    # Sinais de status
    status_message = Signal(str)
    status_error = Signal(str)
    status_success = Signal(str)


class AsyncWorker(QThread):
    """
    Worker assíncrono que executa tarefas pesadas sem bloquear a interface.

    Características:
    - Suporte a async/await
    - Comunicação via sinais
    - Tratamento de erros robusto
    - Progresso em tempo real
    """

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.signals = WorkerSignals()
        self._task: Optional[asyncio.Task] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._running = False
        self._should_stop = False

    def run(self):
        """Executa o worker em uma thread separada."""
        try:
            # Cria um novo event loop para esta thread
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

            # Executa a tarefa principal
            self._running = True
            self.signals.started.emit()

            try:
                self._loop.run_until_complete(self._main_task())
            except Exception as e:
                self._handle_error(f"Erro no worker: {str(e)}")
            finally:
                self._running = False
                self.signals.finished.emit()

        except Exception as e:
            self._handle_error(f"Erro crítico no worker: {str(e)}")
        finally:
            # Limpa o event loop
            if self._loop:
                self._loop.close()

    async def _main_task(self):
        """Tarefa principal do worker."""
        # Este método deve ser sobrescrito nas subclasses
        pass

    def stop(self):
        """Para a execução do worker de forma segura."""
        self._should_stop = True
        if self._task and not self._task.done():
            self._task.cancel()
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)

    def is_running(self) -> bool:
        """Verifica se o worker está em execução."""
        return self._running

    def should_stop(self) -> bool:
        """Verifica se o worker deve parar."""
        return self._should_stop

    def _handle_error(self, error_msg: str):
        """Trata erros e envia para a UI via sinais."""
        self.signals.error.emit(error_msg)
        self.signals.status_error.emit(error_msg)

    def _emit_progress(self, value: int, text: str | None = None):
        """Emite sinal de progresso."""
        self.signals.progress.emit(max(0, min(100, value)))
        if text:
            self.signals.progress_text.emit(text)

    def _emit_status(self, message: str, level: str = "info"):
        """Emite mensagem de status."""
        if level == "error":
            self.signals.status_error.emit(message)
        elif level == "success":
            self.signals.status_success.emit(message)
        else:
            self.signals.status_message.emit(message)




class HeavyCalculationWorker(AsyncWorker):
    """
    Worker para cálculos matemáticos pesados.
    Demonstra como manter a interface responsiva durante operações intensivas.
    """

    def __init__(
        self, calculation_type: str, parent: Optional[QObject] = None
    ):
        super().__init__(parent)
        self.calculation_type = calculation_type
        self._result = None

    async def _main_task(self):
        """Executa cálculo pesado de forma assíncrona."""
        try:
            self._emit_status(
                f"Iniciando cálculo {self.calculation_type}...", "info"
            )

            if self.calculation_type == "fibonacci":
                await self._calculate_fibonacci()
            elif self.calculation_type == "prime":
                await self._calculate_primes()
            elif self.calculation_type == "factorial":
                await self._calculate_factorial()
            else:
                raise ValueError(
                    f"Tipo de cálculo desconhecido: {self.calculation_type}"
                )

            self.signals.result.emit(self._result)
            self.signals.status_success.emit(
                f"Cálculo {self.calculation_type} concluído!"
            )

        except asyncio.CancelledError:
            self.signals.status_message.emit("Cálculo cancelado pelo usuário.")
            raise
        except Exception as e:
            self._handle_error(f"Erro no cálculo: {str(e)}")

    async def _calculate_fibonacci(self):
        """Calcula sequência de Fibonacci."""
        n = 35  # Número suficientemente grande para ser pesado
        self._emit_progress(0, "Calculando Fibonacci...")

        a, b = 0, 1
        for i in range(n):
            if self.should_stop():
                raise asyncio.CancelledError()

            a, b = b, a + b

            # Atualiza progresso a cada 5 iterações
            if i % 5 == 0:
                progress = int((i / n) * 100)
                self._emit_progress(progress, f"Fibonacci: {i}/{n}")
                await asyncio.sleep(0.001)  # Pequena pausa para não bloquear

        self._result = {"type": "fibonacci", "n": n, "result": a}
        self._emit_progress(100, "Concluído!")

    async def _calculate_primes(self):
        """Calcula números primos."""
        limit = 10000
        self._emit_progress(0, "Calculando primos...")

        primes = []
        for num in range(2, limit):
            if self.should_stop():
                raise asyncio.CancelledError()

            is_prime = True
            for i in range(2, int(num**0.5) + 1):
                if num % i == 0:
                    is_prime = False
                    break

            if is_prime:
                primes.append(num)

            # Atualiza progresso a cada 1000 números
            if num % 1000 == 0:
                progress = int((num / limit) * 100)
                self._emit_progress(
                    progress, f"Primos: {len(primes)} encontrados"
                )
                await asyncio.sleep(0.001)

        self._result = {
            "type": "primes",
            "limit": limit,
            "count": len(primes),
            "largest": primes[-1] if primes else 0,
        }
        self._emit_progress(100, "Concluído!")

    async def _calculate_factorial(self):
        """Calcula fatorial grande."""
        n = 50
        self._emit_progress(0, "Calculando fatorial...")

        result = 1
        for i in range(1, n + 1):
            if self.should_stop():
                raise asyncio.CancelledError()

            result *= i

            # Atualiza progresso
            if i % 5 == 0:
                progress = int((i / n) * 100)
                self._emit_progress(progress, f"Fatorial: {i}/{n}")
                await asyncio.sleep(0.001)

        self._result = {"type": "factorial", "n": n, "result": result}
        self._emit_progress(100, "Concluído!")


class FileProcessorWorker(AsyncWorker):
    """
    Worker para processamento de arquivos.
    Demonstra como lidar com operações de IO pesadas.
    """

    def __init__(
        self, file_path: str, operation: str, parent: Optional[QObject] = None
    ):
        super().__init__(parent)
        self.file_path = file_path
        self.operation = operation
        self._result = None

    async def _main_task(self):
        """Processa arquivo de forma assíncrona."""
        try:
            self._emit_status(
                f"Iniciando operação {self.operation} no arquivo...", "info"
            )

            if self.operation == "read":
                await self._read_file()
            elif self.operation == "write":
                await self._write_file()
            elif self.operation == "analyze":
                await self._analyze_file()
            else:
                raise ValueError(f"Operação desconhecida: {self.operation}")

            self.signals.result.emit(self._result)
            self.signals.status_success.emit(
                f"Operação {self.operation} concluída!"
            )

        except asyncio.CancelledError:
            self.signals.status_message.emit("Operação de arquivo cancelada.")
            raise
        except Exception as e:
            self._handle_error(f"Erro na operação de arquivo: {str(e)}")

    async def _read_file(self):
        """Lê arquivo grande de forma assíncrona."""
        self._emit_progress(0, "Lendo arquivo...")

        try:
            # Simula leitura de arquivo grande
            content = []
            for i in range(1000):
                if self.should_stop():
                    raise asyncio.CancelledError()

                content.append(
                    f"Linha {i}: Dados simulados para demonstração de processamento assíncrono.\n"
                )

                if i % 100 == 0:
                    progress = int((i / 1000) * 100)
                    self._emit_progress(progress, f"Lendo: {i}/1000 linhas")
                    await asyncio.sleep(0.001)

            self._result = {
                "operation": "read",
                "lines": len(content),
                "content_preview": "".join(content[:5]),
            }
            self._emit_progress(100, "Concluído!")

        except Exception as e:
            raise Exception(f"Erro ao ler arquivo: {str(e)}")

    async def _write_file(self):
        """Escreve arquivo grande de forma assíncrona."""
        self._emit_progress(0, "Escrevendo arquivo...")

        try:
            # Simula escrita de arquivo grande
            for i in range(500):
                if self.should_stop():
                    raise asyncio.CancelledError()

                # Simula escrita
                await asyncio.sleep(0.002)

                if i % 50 == 0:
                    progress = int((i / 500) * 100)
                    self._emit_progress(
                        progress, f"Escrevendo: {i}/500 blocos"
                    )

            self._result = {
                "operation": "write",
                "blocks_written": 500,
                "file_size_mb": 2.5,
            }
            self._emit_progress(100, "Concluído!")

        except Exception as e:
            raise Exception(f"Erro ao escrever arquivo: {str(e)}")

    async def _analyze_file(self):
        """Analisa arquivo de forma assíncrona."""
        self._emit_progress(0, "Analisando arquivo...")

        try:
            # Simula análise de arquivo
            analysis = {
                "total_lines": 0,
                "total_words": 0,
                "total_chars": 0,
                "word_frequency": {},
            }

            for i in range(200):
                if self.should_stop():
                    raise asyncio.CancelledError()

                # Simula análise
                analysis["total_lines"] += 10
                analysis["total_words"] += 50
                analysis["total_chars"] += 250

                if i % 20 == 0:
                    progress = int((i / 200) * 100)
                    self._emit_progress(
                        progress, f"Analisando: {i}/200 seções"
                    )
                    await asyncio.sleep(0.001)

            self._result = {"operation": "analyze", "analysis": analysis}
            self._emit_progress(100, "Concluído!")

        except Exception as e:
            raise Exception(f"Erro ao analisar arquivo: {str(e)}")
