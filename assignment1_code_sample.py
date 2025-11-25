from __future__ import annotations

import os
import smtplib
import ssl
from email.message import EmailMessage
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pymysql


DB_HOST = os.getenv("DB_HOST", "")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "mydatabase")

API_URL = "https://secure-api.example.com/get-data"


def get_user_input() -> str:
    """
    Prompt the user for their name.
    Returns:
        str: Cleaned user input.
    """
    return input("Enter your name: ").strip()


def send_email(to_email: str, subject: str, body: str) -> None:
    """
    Send an email using secure SMTP.

    Args:
        to_email (str): Recipient email address.
        subject (str): Email subject.
        body (str): Email content.
    """
    msg = EmailMessage()
    msg["From"] = "noreply@example.com"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    context = ssl.create_default_context()
    smtp_user = "noreply@example.com"
    smtp_pass = os.getenv("SMTP_PASSWORD", "")

    try:
        with smtplib.SMTP_SSL("smtp.example.com", 465, context=context) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    except OSError as error:
        print(f"Email error: {error}")


def get_data() -> str:
    """
    Fetch data from a secure HTTPS API.

    Returns:
        str: API response data or empty string on error.
    """
    try:
        request = Request(API_URL, headers={"User-Agent": "SecureClient"})
        with urlopen(request, timeout=10) as response:
            return response.read().decode("utf-8")
    except (HTTPError, URLError, TimeoutError) as error:
        print(f"API fetch error: {error}")
        return ""


def save_to_db(data: str) -> None:
    """
    Save data to a MySQL database securely using parameterized SQL.

    Args:
        data (str): Data to insert.
    """
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
        )

        with connection.cursor() as cursor:
            query = "INSERT INTO mytable (column1, column2) VALUES (%s, %s)"
            cursor.execute(query, (data, "Another Value"))
            connection.commit()
    except pymysql.MySQLError as error:
        print(f"Database error: {error}")
    finally:
        try:
            connection.close()
        except NameError:
            pass


def main() -> None:
    """Main application entrypoint."""
    user_value = get_user_input()
    api_data = get_data()

    if api_data:
        save_to_db(api_data)

    email_body = f"User entered: {user_value}"
    send_email("admin@example.com", "User Input Received", email_body)


if __name__ == "__main__":
    main()
