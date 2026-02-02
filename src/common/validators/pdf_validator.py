"""Validador de segurança para ficheiros PDF.

Verifica:
- Extensão e magic bytes (é realmente PDF?)
- Tamanho do ficheiro
- Número de páginas
- Presença de features perigosas (JavaScript, launch, embedded files)
- Padrões maliciosos no stream

Uso:
    from src.common.validators.pdf_validator import PdfValidator

    validator = PdfValidator()
    result = validator.validate(filepath)

    if result.is_safe:
        # Prosseguir com importação
    else:
        # Mostrar avisos/erros
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

from ..constants.pdf_constants import (
    ALLOWED_EXTENSIONS,
    DANGEROUS_FEATURES,
    MALICIOUS_PATTERNS,
    MAX_FILE_SIZE_MB,
    MAX_PAGES,
    PDF_MAGIC,
)
from .base_validator import BaseValidator


@dataclass
class ValidationResult:
    """Resultado da validação de segurança de PDF."""

    is_safe: bool = True
    is_valid_pdf: bool = True
    has_dangerous_features: bool = False
    has_javascript: bool = False
    file_size_mb: float = 0.0
    page_count: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add_warning(self, msg: str) -> None:
        """Adiciona aviso."""
        self.warnings.append(msg)

    def add_error(self, msg: str) -> None:
        """Adiciona erro e marca como não seguro."""
        self.errors.append(msg)
        self.is_safe = False


class PdfValidator(BaseValidator):
    """Validador de segurança para ficheiros PDF."""

    def __init__(
        self,
        max_file_size_mb: float = MAX_FILE_SIZE_MB,
        max_pages: int = MAX_PAGES,
        allow_javascript: bool = False,
        allow_embedded_files: bool = False,
    ) -> None:
        """Inicializa validador.

        Args:
            max_file_size_mb: Tamanho máximo em MB
            max_pages: Número máximo de páginas
            allow_javascript: Permite JavaScript em PDFs
            allow_embedded_files: Permite ficheiros embebidos
        """
        super().__init__()
        self.max_file_size_mb = max_file_size_mb
        self.max_pages = max_pages
        self.allow_javascript = allow_javascript
        self.allow_embedded_files = allow_embedded_files
        self._validation_result: ValidationResult | None = None

    def is_valid(self, data: Path | str) -> bool:
        """Valida ficheiro PDF.

        Args:
            data: Caminho para ficheiro PDF

        Returns:
            True se ficheiro é seguro, False caso contrário
        """
        filepath = Path(data)
        self._validation_result = self.validar_arquivo(filepath)
        return self._validation_result["valido"]

    def get_errors(self) -> dict[str, str]:
        """Obtém erros de validação.

        Returns:
            Dicionário com mensagens de erro
        """
        if self._validation_result is None:
            return {}

        errors = {}

        if self._validation_result["erros"]:
            errors["pdf_file"] = " | ".join(
                self._validation_result["erros"]
            )

        return errors

    def validar_arquivo(self, filepath: Path | str) -> dict:
        """Valida ficheiro PDF.

        Args:
            filepath: Caminho para o ficheiro

        Returns:
            Dicionário com detalhes da validação
        """
        filepath = Path(filepath)
        result = ValidationResult()

        # 1. Verificar se ficheiro existe
        if not filepath.exists():
            result.add_error(f"Ficheiro não encontrado: {filepath}")
            result.is_valid_pdf = False
            return self._to_dict(result)

        # 2. Verificar extensão
        if not self._check_extension(filepath, result):
            return self._to_dict(result)

        # 3. Verificar tamanho
        if not self._check_file_size(filepath, result):
            return self._to_dict(result)

        # 4. Verificar magic bytes
        if not self._check_magic_bytes(filepath, result):
            return self._to_dict(result)

        # 5. Validar conteúdo PDF
        self._validate_content(filepath, result)

        return self._to_dict(result)

    def _to_dict(self, result: ValidationResult) -> dict:
        """Converte ValidationResult para dicionário."""
        return {
            "valido": result.is_safe and result.is_valid_pdf,
            "paginas": result.page_count,
            "tamanho_mb": result.file_size_mb,
            "tem_javascript": result.has_javascript,
            "tem_features_perigosas": result.has_dangerous_features,
            "avisos": result.warnings,
            "erros": result.errors,
        }

    def _check_extension(
        self, filepath: Path, result: ValidationResult
    ) -> bool:
        """Verifica extensão do ficheiro."""
        ext = filepath.suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            result.add_error(
                f"Extensão não permitida: {ext}. "
                f"Permitidas: {', '.join(ALLOWED_EXTENSIONS)}"
            )
            result.is_valid_pdf = False
            return False
        return True

    def _check_file_size(
        self, filepath: Path, result: ValidationResult
    ) -> bool:
        """Verifica tamanho do ficheiro."""
        size_bytes = filepath.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        result.file_size_mb = round(size_mb, 2)

        if size_mb > self.max_file_size_mb:
            result.add_error(
                f"Ficheiro muito grande: {size_mb:.1f} MB "
                f"(máximo: {self.max_file_size_mb} MB)"
            )
            return False

        if size_mb > self.max_file_size_mb * 0.8:
            result.add_warning(f"Ficheiro grande: {size_mb:.1f} MB")

        return True

    def _check_magic_bytes(
        self, filepath: Path, result: ValidationResult
    ) -> bool:
        """Verifica magic bytes para confirmar tipo de ficheiro."""
        try:
            with open(filepath, "rb") as f:
                header = f.read(4)

            if not header.startswith(PDF_MAGIC):
                result.add_error(
                    "Ficheiro não é um PDF válido (magic bytes "
                    "incorrectos)"
                )
                result.is_valid_pdf = False
                return False

            return True

        except Exception as e:
            result.add_error(f"Erro ao ler ficheiro: {e}")
            result.is_valid_pdf = False
            return False

    def _validate_content(
        self, filepath: Path, result: ValidationResult
    ) -> None:
        """Valida conteúdo do ficheiro PDF."""
        if PyPDF2 is None:
            result.add_warning(
                "PyPDF2 não instalado - validação de conteúdo limitada"
            )
            return

        try:
            with open(filepath, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)

                # Verificar número de páginas
                page_count = len(pdf_reader.pages)
                result.page_count = page_count

                if page_count > self.max_pages:
                    result.add_error(
                        f"PDF tem {page_count} páginas "
                        f"(máximo: {self.max_pages})"
                    )

                # Verificar features perigosas
                self._check_dangerous_features(pdf_reader, result)

                # Verificar padrões maliciosos no stream
                self._check_malicious_patterns(pdf_reader, result)

        except Exception as e:
            result.add_error(f"Erro ao abrir ficheiro PDF: {e}")
            result.is_valid_pdf = False

    def _check_dangerous_features(
        self, pdf_reader: "PyPDF2.PdfReader", result: ValidationResult
    ) -> None:
        """Verifica features perigosas em PDF."""
        try:
            if pdf_reader.is_encrypted:
                result.add_warning("PDF está encriptado")

            # Verificar metadados
            if hasattr(pdf_reader, "metadata") and pdf_reader.metadata:
                # Procurar padrões suspeitos em metadados
                for feature in DANGEROUS_FEATURES:
                    if feature in str(pdf_reader.metadata):
                        result.has_dangerous_features = True
                        result.add_error(
                            f"Feature perigosa detectada: {feature}"
                        )

        except Exception:
            # Alguns PDFs podem não permitir inspeção de metadados
            pass

    def _check_malicious_patterns(
        self, pdf_reader: "PyPDF2.PdfReader", result: ValidationResult
    ) -> None:
        """Verifica padrões maliciosos nos streams PDF."""
        try:
            for page_num, page in enumerate(pdf_reader.pages):
                if not hasattr(page, "get_object"):
                    continue

                page_obj = page.get_object()
                page_str = str(page_obj)

                # Procurar padrões maliciosos
                for pattern in MALICIOUS_PATTERNS:
                    if pattern in page_str:
                        if pattern == "/JS":
                            result.has_javascript = True
                            if not self.allow_javascript:
                                result.add_error(
                                    f"JavaScript detectado na página "
                                    f"{page_num + 1}"
                                )
                        else:
                            result.has_dangerous_features = True
                            result.add_error(
                                f"Padrão perigoso {pattern} "
                                f"detectado na página {page_num + 1}"
                            )

        except Exception:
            # Alguns PDFs podem ter estrutura complexa
            pass


def validate_pdf_file(filepath: Path | str) -> dict:
    """Função de conveniência para validar ficheiro PDF.

    Args:
        filepath: Caminho para o ficheiro

    Returns:
        Dicionário com detalhes da validação
    """
    validator = PdfValidator()
    return validator.validar_arquivo(filepath)


# CLI para testes
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python pdf_validator.py <ficheiro.pdf>")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    validator = PdfValidator()
    result = validator.validate(filepath)

    print()
    print("=" * 60)
    print(f"VALIDAÇÃO: {filepath.name}")
    print("=" * 60)
    print()
    print(f"  É seguro: {'✅ SIM' if result.is_safe else '❌ NÃO'}")
    print(f"  PDF válido: {'✅' if result.is_valid_pdf else '❌'}")
    print(f"  Tamanho: {result.file_size_mb} MB")
    print(f"  Páginas: {result.page_count}")
    print(
        f"  JavaScript: {'⚠️ SIM' if result.has_javascript else '✅ Não'}"
    )
    print(
        f"  Features perigosas: {'❌ SIM' if result.has_dangerous_features else '✅ Não'}"
    )

    if result.warnings:
        print()
        print("⚠️ AVISOS:")
        for w in result.warnings:
            print(f"  - {w}")

    if result.errors:
        print()
        print("❌ ERROS:")
        for e in result.errors:
            print(f"  - {e}")

    print()
    sys.exit(0 if result.is_safe else 1)
