from pathlib import Path
import pandas as pd
import yaml

# ================= CONFIG =================

def load_config(path: str | Path = "config.yaml") -> dict:
    """Carga config.yaml desde la raíz del proyecto."""
    path = Path(path)
    if not path.exists():
        alt = Path("..") / "config.yaml"
        if alt.exists():
            path = alt
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def read_from_config(cfg: dict, key: str, base_key: str = "data_txt", **read_kwargs) -> pd.DataFrame:
    """Carga un dataset usando config.yaml."""
    base = Path(cfg["paths"][base_key])
    fname = cfg["files"][key]
    return pd.read_csv(base / fname, **read_kwargs)

# ================= CLEANING =================

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia nombres de columnas: minúsculas y _ en lugar de espacios."""
    df = df.copy()
    df.columns = (
        df.columns.str.strip().str.lower()
                  .str.replace(" ", "_")
                  .str.replace("-", "_")
    )
    return df

def null_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve % de nulos por columna."""
    s = df.isna().mean().sort_values(ascending=False)
    return s.to_frame("null_rate")

def value_counts_top(df: pd.DataFrame, col: str, n: int = 10) -> pd.DataFrame:
    """Top N categorías de una columna (incluye NaN)."""
    return df[col].value_counts(dropna=False).head(n).rename_axis(col).to_frame("count")
