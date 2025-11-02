import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import openai
import os
import autopep8
import re



# Setting API key
openai.api_key = 'Paste your OpenAI API key here'

# Fetching HTML content from the URL
def fetch_html(url):
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')


# parse_html()
def parse_html(soup):
    """
    Parses the HTML content and extracts static and interactive elements,
    including forms, inputs, buttons, and selects.
    """
    parsed_data = {
        'title': soup.title.string.strip() if soup.title and soup.title.string else "No title found",

        # Links (<a>)
        'links': [a['href'] for a in soup.find_all('a', href=True)],

        # Headings (h1–h6)
        'headings': {
            f"h{level}": [h.get_text(strip=True) for h in soup.find_all(f"h{level}")]
            for level in range(1, 7)
        },

        # Images (<img>)
        'images': [img['src'] for img in soup.find_all('img', src=True)],

        # Forms (<form>)
        'forms': [
            {
                'action': form.get('action'),
                'method': form.get('method'),
                'id': form.get('id'),
                'name': form.get('name')
            }
            for form in soup.find_all('form')
        ],

        # Input fields (<input>)
        'inputs': [
            {
                'type': inp.get('type'),
                'name': inp.get('name'),
                'id': inp.get('id'),
                'placeholder': inp.get('placeholder')
            }
            for inp in soup.find_all('input')
        ],

        # Buttons (<button>)
        'buttons': [
            {
                'text': btn.get_text(strip=True),
                'type': btn.get('type'),
                'id': btn.get('id'),
                'name': btn.get('name')
            }
            for btn in soup.find_all('button')
        ],

        # Select dropdowns (<select>)
        'selects': [
            {
                'name': sel.get('name'),
                'id': sel.get('id'),
                'options': [opt.get_text(strip=True) for opt in sel.find_all('option')]
            }
            for sel in soup.find_all('select')
        ]
    }

    return parsed_data


# generate_selenium_code()
def generate_selenium_code(url, parsed_data):
    """
    Sends structured HTML data to the LLM and requests clean, executable Python Selenium code only.
    The model is explicitly instructed to output raw Python code with no extra text or Markdown.
    """
    prompt = (
        f"-You are a **strict code generator**. Your output must contain ONLY executable Python code, "
        f"-with no explanations, comments, or markdown fences.\n\n"
        f"-Generate Selenium Python test code for the following parsed HTML data.\n\n"
        f"-URL: {url}\n\n"
        f"-Parsed Data:\n{json.dumps(parsed_data, indent=2)[:2000]}...\n\n"
        f"-Instructions:\n"
        f"-Add test for javascript based webelements also"
        f"-Automate each test case using Selenium 4+ syntax.\n"
        f"-**Use only 'find_element(By.<LOCATOR>, value)' and 'find_elements(By.<LOCATOR>, value)'** — never use deprecated 'find_element_by_*' or 'find_elements_by_*' methods.\n"
        f"-Import 'By' from 'selenium.webdriver.common.by' at the top of the code.\n"
        f"- Open the page using ChromeDriver (not headless) and maximise the window.\n"
        f"- Add time.sleep() where ever needed"
        f"- Create 30 sequential test cases that interact with the elements (titles, headings, images, links, forms, inputs, buttons, and selects).\n"
        f"- Each test should include realistic user actions (typing, clicking, submitting, selecting options) with time.sleep() between actions.\n"
        f"- Log each test as 'Test X Passed/Failed' directly in the console.\n"
        f"- Include 'driver.quit()' at the end of the script.\n"
        f"- Do NOT include markdown (```) or any descriptive text before or after the code.\n"
        f"- The entire output must be syntactically valid Python — ready to run as-is.\n"

    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Senior Selenium Automation Tester with 10+ years of experience "
                        "in Python and QA automation. Your job is to generate perfect, executable "
                        "Python Selenium test scripts — no markdown, no explanations, only clean code."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1800,
        )

        code_output = response.choices[0].message.content.strip()

        # Remove markdown fences if any
        code_output = re.sub(r"^```(?:python)?", "", code_output, flags=re.MULTILINE).strip()
        code_output = re.sub(r"```$", "", code_output, flags=re.MULTILINE).strip()

        match = re.search(r"(?m)^(from\s+\S+\s+import\s+\S+|import\s+\S+)", code_output)
        if match:
            code_output = code_output[match.start():]

        # Keep all lines up to and including driver.quit()
        match_end = re.search(r"driver\.quit\(\)", code_output)
        if match_end:
            code_output = code_output[: match_end.end()]

        return code_output.strip()

    except Exception as e:
        print(f"Error generating Selenium code: {e}")
        return None





# Setting up Chrome browser for testing
def setup_chrome():
    options = Options()
    driver = webdriver.Chrome(options=options)
    return driver


# Formatting and cleaning the generated code
def format_selenium_code(selenium_code):
    return autopep8.fix_code(selenium_code)


def clean_selenium_code(code):
    unwanted_patterns = [
        r"Here is.*?Selenium Python code.*?:\s*",
        r"```python", r"```",
        r"Please replace.*?chromedriver.*?\s",
        r"This script checks.*?assertions.*?\s",
    ]
    for pattern in unwanted_patterns:
        code = re.sub(pattern, '', code, flags=re.DOTALL)
    return code


def remove_lines_after_quit(code):
    lines = code.splitlines()
    for i, line in enumerate(lines):
        if 'driver.quit()' in line:
            return '\n'.join(lines[:i + 1])
    return code


# Executing generated Selenium code
def execute_selenium_code(selenium_code, url):
    cleaned_code = clean_selenium_code(selenium_code)
    formatted_code = format_selenium_code(cleaned_code)
    final_code = remove_lines_after_quit(formatted_code)

    with open("generated_test.py", "w") as file:
        file.write(final_code)
    print("\n Selenium Test Script Saved as generated_test.py")

    print("\n Running Selenium Tests...\n")
    os.system("python generated_test.py")


# Main function
def main():
    url = input("Enter the URL to parse and test: ").strip()
    print("\n Fetching and Parsing HTML...")
    soup = fetch_html(url)
    parsed_data = parse_html(soup)
    print("\n Parsed Data:\n", json.dumps(parsed_data, indent=2))

    print("\n Generating Selenium Code via LLM...")
    selenium_code = generate_selenium_code(url, parsed_data)

    if selenium_code:
        print("\n Generated Selenium Code:\n", selenium_code[:800], "...\n")
        execute_selenium_code(selenium_code, url)
    else:
        print("Failed to generate Selenium code.")


if __name__ == "__main__":
    main()
