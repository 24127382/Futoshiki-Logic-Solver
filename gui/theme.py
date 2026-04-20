"""
Theme Module: Centralized color palette and styling constants
=============================================================
Modern Dark theme inspired by VS Code / GitHub Dark.
All visual constants live here so the look is consistent across the app.
"""

from __future__ import annotations


class Palette:
    """Modern Dark color palette."""

    # Base surfaces
    BG_BASE = "#0D1117"          # Window background (deepest)
    BG_SURFACE = "#161B22"       # Panels / sidebar
    BG_ELEVATED = "#1F2531"      # Cards, elevated widgets
    BG_INPUT = "#0B0F15"         # Entry / input fields
    BG_HOVER = "#242C3A"         # Hover state

    # Borders
    BORDER = "#30363D"
    BORDER_STRONG = "#484F58"
    BORDER_FOCUS = "#4F8DFF"

    # Text
    TEXT_PRIMARY = "#E6EDF3"
    TEXT_SECONDARY = "#8B949E"
    TEXT_MUTED = "#6E7681"
    TEXT_DISABLED = "#484F58"

    # Accents
    ACCENT = "#4F8DFF"           # Primary brand blue
    ACCENT_HOVER = "#3B7AE8"
    ACCENT_SOFT = "#1E3A6F"      # Muted accent fill

    SUCCESS = "#3FB950"
    SUCCESS_SOFT = "#1C3021"
    WARNING = "#D29922"
    WARNING_SOFT = "#3B2E10"
    ERROR = "#F85149"
    ERROR_SOFT = "#3A1A1C"
    INFO = "#58A6FF"

    # Gradient helpers (used for headers)
    GRADIENT_FROM = "#4F8DFF"
    GRADIENT_TO = "#A371F7"

    # Cell-specific
    CELL_PREFILLED = "#1F2937"       # Background for cells locked by puzzle
    CELL_SOLVED = "#162A20"          # Background for newly solved cells
    CELL_ERROR = "#3A1A1C"           # Background for invalid cells
    CELL_FOCUS_RING = "#4F8DFF"
    CELL_TEXT = "#E6EDF3"
    CELL_TEXT_PREFILLED = "#F8FAFC"
    CELL_TEXT_SOLVED = "#3FB950"


class Typography:
    """Font families and sizes."""

    FAMILY = "Segoe UI"
    FAMILY_MONO = "Cascadia Mono"

    SIZE_XS = 10
    SIZE_SM = 11
    SIZE_MD = 12
    SIZE_LG = 14
    SIZE_XL = 16
    SIZE_2XL = 20
    SIZE_3XL = 28

    # (family, size, weight)
    @staticmethod
    def title() -> tuple:
        return (Typography.FAMILY, Typography.SIZE_3XL, "bold")

    @staticmethod
    def heading() -> tuple:
        return (Typography.FAMILY, Typography.SIZE_XL, "bold")

    @staticmethod
    def subheading() -> tuple:
        return (Typography.FAMILY, Typography.SIZE_LG, "bold")

    @staticmethod
    def body() -> tuple:
        return (Typography.FAMILY, Typography.SIZE_MD, "normal")

    @staticmethod
    def body_bold() -> tuple:
        return (Typography.FAMILY, Typography.SIZE_MD, "bold")

    @staticmethod
    def small() -> tuple:
        return (Typography.FAMILY, Typography.SIZE_SM, "normal")

    @staticmethod
    def mono() -> tuple:
        return (Typography.FAMILY_MONO, Typography.SIZE_SM, "normal")

    @staticmethod
    def cell(grid_size: int) -> tuple:
        # Scale cell font with grid size so 9x9 stays readable
        size = 22 if grid_size <= 4 else 20 if grid_size <= 6 else 18 if grid_size <= 8 else 16
        return (Typography.FAMILY, size, "bold")

    @staticmethod
    def constraint(grid_size: int) -> tuple:
        size = 18 if grid_size <= 4 else 16 if grid_size <= 6 else 14 if grid_size <= 8 else 12
        return (Typography.FAMILY, size, "bold")


class Spacing:
    """Standard spacing units (pixels)."""

    XS = 2
    SM = 4
    MD = 8
    LG = 12
    XL = 16
    XXL = 24
    XXXL = 32


class Radii:
    """Corner radius standards."""

    SM = 4
    MD = 6
    LG = 8
    XL = 12
    PILL = 999


def cell_size_for(grid_size: int) -> int:
    """Pick a sensible pixel size for each cell based on grid size."""
    if grid_size <= 4:
        return 64
    if grid_size <= 5:
        return 58
    if grid_size <= 6:
        return 52
    if grid_size <= 7:
        return 48
    if grid_size <= 8:
        return 44
    return 40  # 9x9


def constraint_size_for(grid_size: int) -> int:
    """Width (or height) of the constraint gap between cells."""
    if grid_size <= 5:
        return 28
    if grid_size <= 7:
        return 24
    return 22
