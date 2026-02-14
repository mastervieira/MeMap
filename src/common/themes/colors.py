"""
Paleta de cores para temas dark e light do MeMap Pro.
"""

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class ColorPalette:
    """Paleta de cores para um tema."""

    # Cores primárias
    primary: str
    primary_hover: str
    primary_pressed: str

    # Cores de fundo
    background: str
    background_secondary: str
    background_tertiary: str

    # Cores de superfície (cards, panels)
    surface: str
    surface_hover: str

    # Cores de texto
    text_primary: str
    text_secondary: str
    text_disabled: str

    # Cores de borda
    border: str
    border_focus: str

    # Cores de status
    success: str
    success_hover: str
    success_pressed: str
    warning: str
    warning_hover: str
    warning_pressed: str
    error: str
    error_hover: str
    error_pressed: str
    info: str

    # Cores específicas
    accent: str
    accent_hover: str
    accent_pressed: str
    selection: str
    shadow: str

    # Cores secundárias
    secondary: str
    secondary_hover: str
    secondary_pressed: str


# Tema Dark (atual)
DARK_THEME: Final[ColorPalette] = ColorPalette(
    # Primary
    primary="#007ACC",
    primary_hover="#1E90FF",
    primary_pressed="#005A9E",

    # Background
    background="#1E1E1E",
    background_secondary="#252526",
    background_tertiary="#2D2D30",

    # Surface
    surface="#2D2D30",
    surface_hover="#3E3E42",

    # Text
    text_primary="#CCCCCC",
    text_secondary="#888888",
    text_disabled="#555555",

    # Border
    border="#3E3E42",
    border_focus="#007ACC",

    # Status
    success="#4EC9B0",
    success_hover="#3EA090",
    success_pressed="#2E7A6E",
    warning="#FFCC02",
    warning_hover="#E6B800",
    warning_pressed="#CC9900",
    error="#F44747",
    error_hover="#D13B3B",
    error_pressed="#A82E2E",
    info="#75BEFF",

    # Specific
    accent="#569CD6",
    accent_hover="#4AA3D0",
    accent_pressed="#3E86B3",
    selection="#094771",
    shadow="rgba(0, 0, 0, 0.5)",

    # Secondary
    secondary="#5F6368",
    secondary_hover="#7A7F85",
    secondary_pressed="#4A4F54"
)


# Tema Light (novo) - Cards claros e lúcidos
LIGHT_THEME: Final[ColorPalette] = ColorPalette(
    # Primary
    primary="#0078D4",
    primary_hover="#106EBE",
    primary_pressed="#005A9E",

    # Background - tudo claro e consistente
    background="#FAFAFA",           # Fundo principal levemente off-white
    background_secondary="#FFFFFF",  # Cards brancos puros
    background_tertiary="#FFFFFF",   # Sem variação, tudo branco

    # Surface - também claro
    surface="#FFFFFF",
    surface_hover="#F8F9FA",  # Hover muito sutil

    # Text
    text_primary="#1A1A1A",
    text_secondary="#6C757D",
    text_disabled="#ADB5BD",

    # Border - bordas sutis
    border="#E9ECEF",      # Borda muito sutil
    border_focus="#0078D4",

    # Status
    success="#28A745",
    success_hover="#218838",
    success_pressed="#1E7E34",
    warning="#FFC107",
    warning_hover="#E0A800",
    warning_pressed="#D39E00",
    error="#DC3545",
    error_hover="#C82333",
    error_pressed="#BD2130",
    info="#17A2B8",

    # Specific
    accent="#0078D4",
    accent_hover="#106EBE",
    accent_pressed="#005A9E",
    selection="#D4E9F7",  # Seleção azul clarinho
    shadow="rgba(0, 0, 0, 0.08)",  # Sombra muito sutil

    # Secondary - cinzas claros
    secondary="#DEE2E6",
    secondary_hover="#CED4DA",
    secondary_pressed="#ADB5BD"
)
