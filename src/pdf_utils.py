# Utilitario para convertir las fechas extraidas del PDF a un objeto datetime

import datetime
import logging
import re

from unidecode import unidecode

logger = logging.getLogger(__name__)


def convert_date(date_string, debug=False):
    """
    Utility to convert dates extracted from PDF to datetime object
    :param date_string:
    :param debug: enables detailed debug
    :return:
    """
    date_regex = r"^D:(\d{4})(\d{2})((\d{2}))?((\d{2})((\d{2})((\d{2}))?)?([zZ]?([+-]?\d{2}(:?\d{2})?)?)?)?$"

    cleaned_text = date_string.replace("'", "").replace("´", "").replace("`", "")
    if debug:
        logger.debug(
            f"datetime.convert()\toriginal_text: {date_string}\tclean_text: {cleaned_text}."
        )
    match = re.match(date_regex, cleaned_text)
    if not match:
        if debug:
            logger.debug("datetime.convert()\t No Match")
        return None

    year = int(match.group(1))
    month = int(match.group(2))
    day = int(match.group(4)) if match.group(4) else 1
    hour = int(match.group(6)) if match.group(6) else 0
    minute = int(match.group(8)) if match.group(8) else 0
    second = int(match.group(10)) if match.group(10) else 0
    if debug:
        logger.debug(
            f"year: {year}, month: {month}, day: {day}, hour: {hour}, minute: {minute}, second: {second}"
        )

    if match.group(12):
        tz_offset = match.group(12)[1:]
        if ":" in tz_offset:
            tz_offset_hours, tz_offset_minutes = tz_offset.split(":")
            tz_offset_hours = int(tz_offset_hours)
            tz_offset_minutes = int(tz_offset_minutes)
        else:
            tz_offset_minutes = 0
            if len(tz_offset) >= 2:
                tz_offset_hours = int(tz_offset[:2])
            else:
                tz_offset_hours = int(tz_offset)
            if len(tz_offset) >= 4:
                tz_offset_minutes = int(tz_offset[2:4])

        if debug:
            logger.debug(
                f"tz_offset: {tz_offset}, len: {len(tz_offset)}, tz_offset_hours:{tz_offset_hours}, tz_offset_minutes:{tz_offset_minutes}"
            )
        if match.group(12)[0] == "-":
            tz_offset_hours *= -1

        tzinfo = datetime.timezone(
            datetime.timedelta(hours=tz_offset_hours, minutes=tz_offset_minutes)
        )
    else:
        tzinfo = None

    return datetime.datetime(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second,
        tzinfo=tzinfo,
    )


def sanityze(text):
    # Replace accented characters with normal versions in only the leading letters of A-Z
    text = unidecode(text)
    # Replace repeated characters
    text = clean_repeted_chars(text)
    # Replace special characters
    text = text.replace("/uni00A0", " ")
    text = text.replace("/G84/G84", "- ")
    # Removing leading and trailing blanks
    text = text.strip()

    return text


def clean_repeted_chars(text):
    text = re.sub(r"\t+", "\t", text)
    text = re.sub(r" +", " ", text)
    text = re.sub(r"\n+", "\n", text)
    return text


def clean_text(text):
    text = sanityze(text)
    text = clean_index_text(text)
    text = clean_repeated_text_structures(text)
    text = join_separated_words(text)
    return text


def clean_repeated_text_structures(text):
    text = re.sub(r"\n\s+\n+", "\n", text)
    text = re.sub(r"\s+\n+", "\n", text)
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r"-{2,}", "-", text)
    text = re.sub(r"_{2,}", "_", text)
    text = clean_repeted_chars(text)
    return text


def clean_index_text(text):
    # This pattern searches for lines containing a title followed by repeated characters and a page number.
    # Sample text
    """
    Índice

    Introducción ..................... 1

    Capítulo 1: Conceptos Básicos
    1.1 Definiciones ................. 5
    1.2 Historia ..................... 8

    Capítulo 2: Aplicaciones Prácticas
    2.1 Caso de estudio 1 ............ 15
    2.2 Caso de estudio 2 ............ 22

    Conclusiones ..................... 30

    Bibliografía ..................... 32

    :param text: text to fix
    :return:
    """
    pattern = r"(.*?)\s*([.\s_-]{3,})\s*(\d+)"

    def process_match(match):
        title = match.group(1).strip()
        page_num = match.group(3)
        # Si el título está vacío o solo contiene números, lo ignoramos y devolvemos la línea original sin cambios
        if not title or title.isdigit():
            return match.group(0)
        # De lo contario devolvemos el patron:
        return f"{title}: {page_num}.\n"

    # Aplicar el reemplazo solo a las líneas que coincidan con el patrón
    lines = text.split("\n")
    processed_lines = [re.sub(pattern, process_match, line) for line in lines]

    return "\n".join(processed_lines)


def join_separated_words(text):
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
    return text
