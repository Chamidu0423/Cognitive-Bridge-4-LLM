# Cognitive Bridge: AI Interoperability Suite

This application provides an automated framework for facilitating dialectical interactions between different AI models. It uses Selenium to control web browsers and simulate conversations between supported AI platforms, allowing for iterative analysis and synthesis of topics.

## Features

* Support for multiple AI models: ChatGPT (OpenAI), Gemini (Google), Grok (xAI), and DeepSeek (R1/V3)
* Configurable termination conditions: semantic-based (wait for "ALL DONE") or iteration-based
* Real-time logging and status monitoring
* User-friendly graphical interface built with CustomTkinter

## Requirements

* Python 3.8 or higher
* Google Chrome browser
* Windows operating system (due to Chrome debugging setup)

## Installation

1. Install the required Python packages:

   ```
   pip install selenium customtkinter packaging pillow pyperclip webdriver-manager
   ```

2. Ensure Google Chrome is installed on your system.

## Setup

1. Launch Chrome in debug mode using Command Prompt (not PowerShell):

   ```
   start chrome --remote-debugging-port=9222 --user-data-dir="C:\selenium\ChromeProfile"
   ```

   This opens a Chrome instance that the application can control. Keep this window open during operation.

2. Open the application by running:

   ```
   python SeleniumBridge.py
   ```

## Usage

1. In the application window, select the Initiator Model and Respondent Model from the dropdown menus.

2. Choose the termination protocol:
   * Semantic Termination: The process continues until one model outputs "ALL DONE"
   * Iterative Termination: Specify the maximum number of cycles

3. Enter your initial prompt in the System Instruction field.

4. Click "INITIALIZE SESSION" to start the automation.

5. Monitor progress in the Command Console tab. The application will automatically switch between browser tabs and exchange messages between the selected models.

6. Use "TERMINATE" to stop the process at any time.

## Safety and Security

**Important Security Warning:** Do not use your personal or primary accounts with this application. Automated interactions may trigger anti-bot mechanisms on AI platforms. Always use secondary or throwaway accounts to avoid potential account restrictions or bans.

## Troubleshooting

* If the application cannot connect to Chrome, ensure the debug port (9222) is active and the Chrome window remains open.
* Verify that the correct selectors are configured for each AI model in the code if new versions change the interface.
* Check the logs in the Command Console for detailed error messages.

## License

This project is provided as-is for educational and research purposes. Use responsibly and in accordance with the terms of service of the AI platforms involved.