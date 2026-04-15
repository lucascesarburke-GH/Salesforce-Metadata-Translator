Salesforce AI Translation Tool
Project Overview
This tool automates the process of translating Salesforce Field Labels. It reads an "Outdated and untranslated" .stf file exported from the Salesforce Translation Workbench, uses AI to translate the labels while respecting Salesforce’s 40-character limit, and generates a new .stf file ready for import.

Prerequisites
Python Version: Python 3.8 or higher is required.

OpenAI Account: A valid API key with available credits.

Setup Instructions
Install Dependencies:
Open your terminal and install the required OpenAI library:
"pip install openai"

Set Environment Variable:
The script looks for an environment variable named OPENAI_API_KEY.

Windows: setx OPENAI_API_KEY "your-key-here"

Mac/Linux: export OPENAI_API_KEY="your-key-here"

How to get an OpenAI API Key
Navigate to the OpenAI Platform.
Sign in and go to Settings > API Keys.
Click "Create new secret key".
Copy the key immediately; you cannot view it again once the dialog closes.
Ensure your account has a credit balance in the Billing section to enable API requests.

File Format Documentation
The script utilizes Salesforce Translation Files (.stf).

Input File: Must be named starting with "Outdated and untranslated".

Structure: A tab-separated text file containing a KEY (unique metadata identifier) and a LABEL (the text to translate).

Encoding: Output files are encoded in UTF-8 for Salesforce compatibility.

Usage Example
Export: Download the "Outdated and untranslated" file from Salesforce and place it in the script's folder.

Run:
python sf_ai_translation.py
Select Language: Enter a supported target language (e.g., "spanish") when prompted.

Import: Review the generated .stf file and upload it back to the Salesforce Translation Workbench.