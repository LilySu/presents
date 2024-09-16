from crewai_tools import BaseTool
from shop_presents.tools.play import login_to_amazon
import os
from dotenv import load_dotenv
from pathlib import Path

class AmazonTool(BaseTool):
    name: str = "Amazon Login Tool"
    description: str = (
        "A tool to log into an Amazon account using credentials from .env file. "
        "This tool uses Playwright to automate the login process and "
        "returns the result of the login attempt."
    )

    def _run(self) -> str:
        # Find the .env file in the parent directory of shop_presents
        current_dir = Path(__file__).resolve().parent
        shop_presents_dir = current_dir
        while shop_presents_dir.name != 'shop_presents' or 'src' in shop_presents_dir.parts:
            shop_presents_dir = shop_presents_dir.parent
            if shop_presents_dir == shop_presents_dir.parent:  # reached root
                return "Error: Could not find the shop_presents directory."

        dotenv_path = shop_presents_dir.parent / '.env'

        print(f"Looking for .env file at: {dotenv_path}")  # Debug print

        # Load environment variables from .env file
        load_dotenv(dotenv_path)

        # Get credentials from environment variables
        email = os.getenv("EMAIL")
        password = os.getenv("PASSWORD")

        if not email or not password:
            return f"Error: EMAIL and PASSWORD must be set in the .env file. Looked for .env at: {dotenv_path}"

        try:
            # Call the login_to_amazon function
            login_to_amazon(email, password)
            return "Login process completed. Check the console output and screenshots for details."
        except Exception as e:
            return f"An error occurred during the login process: {str(e)}"

if __name__ == "__main__":
    login_tool = AmazonTool()
    result = login_tool._run()
    print(result)