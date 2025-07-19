The AutoQAGPT is controlled by the main() function, which coordinates the entire pipeline from HTML extraction to test execution. This function manages the overall workflow, maintains data consistency, and handles errors at each stage.

The process begins by prompting the user to enter a website URL. The fetch-html() function retrieves the HTML content. If the URL is valid and the server responds correctly, the function returns the content as a BeautifulSoup object. Otherwise, error handling is triggered to stop or retry the process. The HTML is then parsed using the parse-html() function, which extracts key elements such as titles, headings, links, and images. These elements form the input for test generation.

The parsed output is passed to the generate-selenium-code() function, where a detailed prompt is constructed and embedded directly in the code. This prompt is sent to the GPT-4 API along with the structured data. GPT-4 returns Selenium test code based on the instructions in the prompt.

The raw output is refined through three post-processing steps. First, clean-selenium-code() removes unwanted text using regular expressions. Then, format-selenium-code() uses autopep8 to apply Python style formatting. Finally, remove-lines-after-quit() ensures the script ends cleanly after the browser is closed.

The cleaned and formatted script is saved as a .py file named generated-test.py. The execute-selenium-code() function is then called to launch the Chrome browser, run the test script, and log the results. Any runtime errors are caught and printed, allowing the pipeline to continue running. At the end, the terminal shows a summary of test performance, serving as a simple reporting method.
This workflow demonstrates how the framework maintains tight integration between all components while preserving modular independence, thereby facilitating robustness and extensibility.
