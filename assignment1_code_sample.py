import os
import smtplib
import ssl
import pymysql
from email.message import EmailMessage
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


# Database credentials should come from environment variables
DB_HOST = os.getenv("DB_HOST", "")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "mydatabase")

# Secure HTTPS API endpoint
API_URL = "https://secure-api.example.com/get-data"


def get_user_input() -> str:
    """Prompt user for their name safely."""
    name = input("Enter your name: ").strip()
    return name


def send_email(to_email: str, subject: str, body: str) -> None:
    """
    Send an email using secure SMTP.
    Replaces insecure os.system() mail command.
    """
    try:
        msg = EmailMessage()
        msg["From"] = "noreply@example.com"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        context = ssl.create_default_context()

        smtp_user = "noreply@example.com"
        smtp_pass = os.getenv("SMTP_PASSWORD", "")

        with smtplib.SMTP_SSL("smtp.example.com", 465, context=context) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

    except Exception as error:
        print(f"Email send error: {error}")


def get_data() -> str:
    """Fetch data from secure HTTPS API with proper error handling."""
    try:
        req = Request(API_URL, headers={"User-Agent": "SecureClient"})
        with urlopen(req, timeout=10) as response:
            return response.read().decode("utf-8")

    except (HTTPError, URLError, TimeoutError) as error:
        print(f"Error fetching API data: {error}")
        return ""


def save_to_db(data: str) -> None:
    """
    Save data to MySQL database using parameterized SQL
    to prevent SQL injection.
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
        if "connection" in locals():
            connection.close()


def main() -> None:
    """Main application entry point."""
    user_value = get_user_input()
    api_data = get_data()

    if api_data:
        save_to_db(api_data)

    send_email(
        "admin@example.com",
        "User Input Received",
        f"User entered: {user_value}",
    )


if __name__ == "__main__":
    main()
