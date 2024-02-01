from datetime import date


def get_date_string() -> str:
    """This function creates a date.

    Returns
    -------
    str
        Returns the current date in Year-Month-Day format
    """
    return date.today().strftime("%Y-%m-%d")
