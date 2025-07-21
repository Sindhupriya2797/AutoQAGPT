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
openai.api_key = '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'

# Fetching HTML content from the URL
def fetch_html(url):
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')

# Parsing the HTML to extract all the elements
def parse_html(soup):
    parsed_data = {
        'title': soup.title.string if soup.title else "No title found",
        'links': [a['href'] for a in soup.find_all('a', href=True)],
        'headings': {f"h{level}": [h.text.strip() for h in soup.find_all(f"h{level}")] for level in range(1, 7)},
        'images': [img['src'] for img in soup.find_all('img', src=True)],

    }
    return parsed_data

# Generating Selenium code using OpenAI
def generate_selenium_code(url, parsed_data):
    prompt = (
        f"Generate robust Selenium Python code based on the following parsed HTML data:\n\n"
        f"URL: {url}\n\n"
        f"Parsed Data:\n{json.dumps(parsed_data, indent=2)[:1000]}...\n\n"
        f"Instructions:\n"
        f"1. Write at least 30 test cases to verify elements like titles, headings, and images. Write test cases for links at the end.\n"
        f"2. Number each test case sequentially (e.g., Test 1, Test 2, ..., Test 10) and ensure they are executed in order.\n"
        f"3. Automate each test case and provide the complete Selenium Python code. If links are present, click on any 2 links and verify navigation.\n"
        f"4. Use ChromeDriver setup with ChromeOptions, but exclude the '--headless' argument.\n"
        f"5. Include code to maximize the Chrome window and use time.sleep() to wait for elements to load.\n"
        f"6. Use 'find_element(By.X)' instead of deprecated 'find_element_by_*' methods.\n"
        f"7. Execute all test cases one by one in the Chrome browser in the same order as written.\n"
        f"8. Log the result (Pass/Fail) of each test case right beside the test case number and description.\n"
        f"9. Ensure the numbering is strictly in ascending order without skipping or repeating numbers.\n"
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating Selenium code: {e}")
        return None

# Setting up Chrome browser for testing
def setup_chrome():
    options = Options()
    # Explicitly ensure no "--headless" argument is used
    driver = webdriver.Chrome(options=options)
    return driver

# Cleaning and formating the generated code using autopep8
def format_selenium_code(selenium_code):
    formatted_code = autopep8.fix_code(selenium_code)
    return formatted_code

# Removing unwanted sections using regex
def clean_selenium_code(code):
    unwanted_patterns = [
        r"Here is a sample Selenium Python code based on the parsed HTML data and instructions provided:\s*",
        r"Here is a sample Selenium Python code based on the parsed HTML data and instructions:\s*",
        r"Here is the Selenium Python code based on the instructions:\s*",
        r"Here is a sample Selenium Python code that follows the instructions:\s*",
        r"Here is a sample Selenium Python code to automate the test cases based on the parsed HTML data:\s*",
        r"Here is the Selenium Python code for the given instructions:\s*",
        r"Here is the Selenium Python code based on the parsed HTML data:\s*",
        r"Here is the Selenium Python code based on the parsed HTML data and instructions:\s*",
        r"Here is the Selenium Python code based on your instructions:\s*",
        r"Here is a sample Selenium Python code based on your instructions:\s*",
        r"Here is the Selenium Python code based on the given instructions:\s*",
        r"python",
        r"",
        r"python",
        r"\n```",
        r"```",
        r"Please replace '/path/to/chromedriver' with the actual path of your ChromeDriver\..?tests in the browser without actually opening it\.\s",
        r"This script checks the number of elements like titles, links, headings, images, and buttons\..?prints that the test failed\.\s",
        r"Please note that this is a basic script\..?more detailed assertions\(e\.g\., checking the text of headings, the URLs of links, etc\)\.\s"
    ]
    for pattern in unwanted_patterns:
        code = re.sub(pattern, '', code, flags=re.DOTALL)
    return code

# Removing lines after driver.quit()
def remove_lines_after_quit(code):
    lines = code.splitlines()
    for i, line in enumerate(lines):
        if 'driver.quit()' in line:
            return '\n'.join(lines[:i + 1])
    print("No driver.quit() statement found.")
    return code

# Executing generated Selenium code
def execute_selenium_code(selenium_code, url):
    cleaned_code = clean_selenium_code(selenium_code)
    formatted_code = format_selenium_code(cleaned_code)
    final_code = remove_lines_after_quit(formatted_code)

    with open("generated_test.py", "w") as file:
        file.write(final_code)
    print("\n   Selenium Test Script Saved  \n")

    print("\n   Running Selenium Tests:  ")
    os.system("python generated_test.py")

# Main function
def main():
    url = input("Enter the URL to parse and test: ").strip()
    print("\n  Fetching and Parsing HTML:")
    soup = fetch_html(url)
    parsed_data = parse_html(soup)
    print("\n  Parsed Data is: \n", json.dumps(parsed_data, indent=2))

    print("\n  Generating Selenium Code:")
    selenium_code = generate_selenium_code(url, parsed_data)
    if selenium_code:
        print("\n  Generated Selenium Code:  \n", selenium_code)
        print("\n   Setting up Chrome and Running Tests:  ")
        execute_selenium_code(selenium_code, url)
    else:
        print("Failed to generate Selenium code.")

if __name__ == "__main__":
    main()