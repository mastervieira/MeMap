"""Validador de segurança para ficheiros de imagem.

Verifica:
- Extensão e magic bytes (é realmente imagem?)
- Tamanho do ficheiro
- Dimensões da imagem (resolução)
- Corrupção de ficheiro
- Metadados EXIF (sensibilidade privada)
- Sanitização com Pillow (remove metadata)

Uso:
    from src.common.validators.image_validator import ImageValidator

    validator = ImageValidator()
    result = validator.validate(filepath)

    if result.is_safe:
        # Prosseguir com importação
        sanitized_path = result.sanitized_path
    else:
        # Mostrar avisos/erros
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path

try:
    from PIL import Image
    from PIL.Image import Image as PILImage
except ImportError:
    Image = None
    PILImage = None

from ..constants.image_constants import (
    ALLOWED_EXTENSIONS,
    ALLOWED_PIL_FORMATS,
    BMP_MAGIC,
    CACHE_DIR,
    CACHE_ENABLED,
    GIF_MAGIC,
    JPG_MAGIC,
    MAX_DIMENSIONS,
    MAX_FILE_SIZE_MB,
    MIN_DIMENSIONS,
    PNG_MAGIC,
    WEBP_MAGIC,
)
from .base_validator import BaseValidator

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Resultado da validação de segurança de imagem."""

    is_safe: bool = True
    is_valid_image: bool = True
    has_exif_data: bool = False
    has_suspicious_content: bool = False
    file_size_mb: float = 0.0
    width: int = 0
    height: int = 0
    format: str = ""
    sanitized_path: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add_warning(self, msg: str) -> None:
        """Adiciona aviso."""
        self.warnings.append(msg)

    def add_error(self, msg: str) -> None:
        """Adiciona erro e marca como não seguro."""
        self.errors.append(msg)
        self.is_safe = False


class ImageValidator(BaseValidator):
    """Validador de segurança para ficheiros de imagem."""

    def __init__(
        self,
        max_file_size_mb: float = MAX_FILE_SIZE_MB,
        max_width: int = MAX_DIMENSIONS[0],
        max_height: int = MAX_DIMENSIONS[1],
        sanitize: bool = True,
        cache_enabled: bool = CACHE_ENABLED,
    ) -> None:
        """Inicializa validador.

        Args:
            max_file_size_mb: Tamanho máximo em MB
            max_width: Largura máxima da imagem
            max_height: Altura máxima da imagem
            sanitize: Sanitizar imagem (remover metadata)
            cache_enabled: Ativar cache de imagens sanitizadas
        """
        super().__init__()
        self.max_file_size_mb = max_file_size_mb
        self.max_width = max_width
        self.max_height = max_height
        self.sanitize = sanitize
        self.cache_enabled = cache_enabled
        self._cache_dir = Path(CACHE_DIR)
        self._validation_result: ValidationResult | None = None

        if self.sanitize and self.cache_enabled:
            self._cache_dir.mkdir(parents=True, exist_ok=True)

    def is_valid(self, data: Path | str) -> bool:
        """Valida ficheiro de imagem.

        Args:
            data: Caminho para ficheiro de imagem

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
            errors["image_file"] = " | ".join(
                self._validation_result["erros"]
            )

        return errors

    def validar_arquivo(self, filepath: Path | str) -> dict:
        """Valida ficheiro de imagem.

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
            result.is_valid_image = False
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

        # 5. Abrir e validar imagem
        self._validate_image(filepath, result)

        # 6. Sanitizar se necessário
        if self.sanitize and result.is_valid_image:
            self._sanitize_image(filepath, result)

        return self._to_dict(result)

    def _to_dict(self, result: ValidationResult) -> dict:
        """Converte ValidationResult para dicionário."""
        return {
            "valido": result.is_safe and result.is_valid_image,
            "largura": result.width,
            "altura": result.height,
            "formato": result.format,
            "tamanho_mb": result.file_size_mb,
            "tem_exif": result.has_exif_data,
            "caminho_sanitizado": result.sanitized_path,
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
            result.is_valid_image = False
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
                header = f.read(12)

            ext = filepath.suffix.lower()
            is_valid = False

            if ext in {".png"}:
                is_valid = header.startswith(PNG_MAGIC)
            elif ext in {".jpg", ".jpeg"}:
                is_valid = header.startswith(JPG_MAGIC)
            elif ext == ".gif":
                is_valid = header.startswith(GIF_MAGIC)
            elif ext == ".bmp":
                is_valid = header.startswith(BMP_MAGIC)
            elif ext == ".webp":
                is_valid = header.startswith(WEBP_MAGIC)

            if not is_valid:
                result.add_error(
                    "Ficheiro não é uma imagem válida (magic bytes "
                    "incorrectos)"
                )
                result.is_valid_image = False
                return False

            return True

        except Exception as e:
            result.add_error(f"Erro ao ler ficheiro: {e}")
            result.is_valid_image = False
            return False

    def _validate_image(
        self, filepath: Path, result: ValidationResult
    ) -> None:
        """Valida conteúdo da imagem com Pillow."""
        if Image is None:
            result.add_warning(
                "Pillow não instalado - validação limitada"
            )
            return

        try:
            with Image.open(filepath) as img:
                result.width = img.width
                result.height = img.height
                result.format = img.format or "Unknown"

                # Verificar dimensões
                if not (
                    MIN_DIMENSIONS[0] <= result.width <= self.max_width
                    and MIN_DIMENSIONS[1]
                    <= result.height
                    <= self.max_height
                ):
                    result.add_error(
                        f"Dimensões inválidas: {result.width}x"
                        f"{result.height} "
                        f"(máximo: {self.max_width}x{self.max_height})"
                    )

                # Verificar formato suportado
                if result.format not in ALLOWED_PIL_FORMATS:
                    result.add_error(
                        f"Formato não permitido: {result.format}"
                    )
                    return

                # Verificar metadados EXIF
                self._check_exif_data(img, result)

                # Verificar conteúdo suspeito
                self._check_suspicious_content(img, result)

        except Exception as e:
            result.add_error(f"Erro ao abrir imagem: {e}")
            result.is_valid_image = False

    def _check_exif_data(
        self, img: PILImage, result: ValidationResult
    ) -> None:
        """Verifica presença de metadados EXIF."""
        try:
            if hasattr(img, "info") and img.info:
                # Verificar se tem dados EXIF/metadados
                if any(
                    tag in img.info
                    for tag in ["DateTime", "GPSInfo", "Make", "Model"]
                ):
                    result.has_exif_data = True
                    result.add_warning(
                        "Imagem contém metadados EXIF (será removido)"
                    )

                # Verificar dados Exif via tag 0x0112 (orientation)
                if hasattr(img, "_getexif"):
                    exif = img._getexif()
                    if exif:
                        result.has_exif_data = True

        except Exception:
            # Alguns formatos podem não ter EXIF
            pass

    def _check_suspicious_content(
        self, img: PILImage, result: ValidationResult
    ) -> None:
        """Verifica conteúdo suspeito em imagem."""
        try:
            # Verificar palette mode (menos comum, pode ser vetor)
            if img.mode == "P":
                result.add_warning(
                    "Imagem em palette mode (pode conter dados alterados)"
                )
                result.has_suspicious_content = True

            # Verificar tamanho de paleta (GIF com muitas cores)
            if hasattr(img, "palette") and img.palette:
                palette_size = len(img.palette.getdata()[1])
                if palette_size > 256:
                    result.add_warning("Paleta de cores anormalmente grande")

        except Exception:
            pass

    def _sanitize_image(
        self, filepath: Path, result: ValidationResult
    ) -> None:
        """Sanitiza imagem removendo metadados e reencodificando."""
        if Image is None:
            result.add_warning("Pillow não disponível para sanitização")
            return

        try:
            # Gerar caminho cache
            cache_path = self._get_cache_path(filepath)

            # Verificar se já existe em cache
            if cache_path.exists():
                result.sanitized_path = str(cache_path)
                logger.info(f"Cache hit: {cache_path}")
                return

            # Abrir imagem
            with Image.open(filepath) as img:
                # Converter para RGB se necessário (remove alpha/paleta)
                if img.mode in ("RGBA", "LA", "P"):
                    # Criar fundo branco
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    bg.paste(img, mask=img.split()[-1] if img.mode
                             in ("RGBA", "LA") else None)
                    img = bg
                elif img.mode != "RGB":
                    img = img.convert("RGB")

                # Salvar em cache (reencodificação remove metadados)
                img.save(cache_path, format="JPEG", quality=95)
                result.sanitized_path = str(cache_path)
                logger.info(f"Imagem sanitizada: {cache_path}")

        except Exception as e:
            result.add_error(f"Erro ao sanitizar imagem: {e}")
            logger.error(f"Sanitization failed: {e}")

    def _get_cache_path(self, filepath: Path) -> Path:
        """Gera caminho cache baseado no hash do ficheiro."""
        file_hash = hashlib.md5(
            str(filepath.absolute()).encode()
        ).hexdigest()
        return self._cache_dir / f"{file_hash}.jpg"


def validate_image_file(filepath: Path | str) -> dict:
    """Função de conveniência para validar ficheiro de imagem.

    Args:
        filepath: Caminho para o ficheiro

    Returns:
        Dicionário com detalhes da validação
    """
    validator = ImageValidator()
    return validator.validar_arquivo(filepath)


# CLI para testes
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python image_validator.py <ficheiro.jpg>")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    validator = ImageValidator()
    result = validator.validate(filepath)

    print()
    print("=" * 60)
    print(f"VALIDAÇÃO: {filepath.name}")
    print("=" * 60)
    print()
    print(f"  É seguro: {'✅ SIM' if result.is_safe else '❌ NÃO'}")
    print(f"  Imagem válida: {'✅' if result.is_valid_image else '❌'}")
    print(f"  Tamanho: {result.file_size_mb} MB")
    print(f"  Dimensões: {result.width}x{result.height} px")
    print(f"  Formato: {result.format}")
    print(f"  EXIF: {'⚠️ SIM' if result.has_exif_data else '✅ Não'}")
    print(
        f"  Sanitizado: {result.sanitized_path or 'Não'}"
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
