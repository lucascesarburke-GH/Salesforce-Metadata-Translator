# SF Python translation project
import os
from datetime import date
from datetime import datetime
from openai import OpenAI
import ast
import sys
import glob
openai_API_Key = os.getenv("OPENAI_API_KEY")
if openai_API_Key is None:
    raise ValueError("OpenAI API key is not set in environment variables.")
client = OpenAI(api_key=openai_API_Key)


def get_English_Field_Labels():
    search_pattern = "Outdated and untranslated*"
    matching_files = glob.glob(search_pattern)
    if matching_files:
        matching_files.sort(key=os.path.getmtime)
        File_Untranslated = matching_files[-1]
    else:
        print("No 'Outdated and untranslated' files identified in root folder. Please export the appropriate file from your SF instance as outlined in setup instructions and try again.")
        sys.exit()

    FullKeyandLabelList = []
    try:
        with open(File_Untranslated, "r", encoding='utf-8') as file2:
            for line in file2:
                line = line.strip()
                if not line or line.startswith("#") or line.startswith("KEY\tLABEL"):
                    continue
                if not line.startswith(("CustomField.", "StandardField.")):
                    continue
                if '\t' in line:
                    KeyAndLabelsplt = line.split('\t')
                    if len(KeyAndLabelsplt) == 2:
                        KeyandKLbelTuple = tuple(KeyAndLabelsplt)
                        FullKeyandLabelList.append(KeyandKLbelTuple)
                    else:
                        continue
        return FullKeyandLabelList
    except FileNotFoundError:
        print(f"LBError: The file '{File_Untranslated}' was not found.")


def translate_batch(UntranslatedLabelList, target_language):
    original_language = "English"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",
                "content": f"""You are a Salesforce translation tool. You are translating Salesforce field labels from {original_language} to {target_language}.
                Rules: > 1. Return ONLY a valid Python list of tuples.
                2. Each tuple must be (original_key, translated_label).
                3. Keep the key EXACTLY as provided.
                4. Translated labels must be 40 characters or less.
                5. Do not include markdown code blocks (```), conversational filler, or explanations."""
             },
            {"role": "user", "content": f"Translate the label portion of these tuples: {UntranslatedLabelList}. Do not translate HTML tags. Ensure the output is a single Python-parsable list."
             }
        ],
        temperature=0.1
    )
    raw_ai_message_content = response.choices[0].message.content
    FullTranslatedKeyandLabelList = []
    FullTranslatedKeyandLabelList = ast.literal_eval(raw_ai_message_content)
    return (FullTranslatedKeyandLabelList)


def validate_and_truncate(MainFullTranslatedKeyandLabelList):
    Validatedlist = []
    for translation in MainFullTranslatedKeyandLabelList:
        key = translation[0]
        label = translation[1]
        Length = (len(label))
        if Length >= 41:
            strippedlabel = label[:40].strip()
            print("Warning: translated label as returned by AI for lebl with API name:", {key}, "and translated label of: ", {
                  label}, "exceeds 40 character SF limit and has been truncated to fit.", "Please  review this translation before uploading to Salesforce.")
            Validatedlist.append((key, strippedlabel))
        else:
            Validatedlist.append((key, label))
            Validatedlist = MainFullTranslatedKeyandLabelList
    return Validatedlist


def create_upload_file(ValidatedList, target_language, language_code):

    datetoday = date.today()
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    file_name = f"{target_language}_sf_automated_translations_{timestamp}.stf"
    print(f"Creating STF upload file with name: {file_name}")
    with open(file_name, 'x', encoding='utf-8') as file:
        header = (f"#Automated translation file creation\n"
                  f"# Language: {target_language}\n"
                  f"Language code: {language_code}\n"
                  f"Type: Outdated and untranslated\n"
                  f"Translation type: Metadata\n"
                  f"\n"
                  f"# KEY\tLABEL\n"
                  f"\n")
        file.write(header)
        for translationtuple in ValidatedList:
            key = translationtuple[0]
            label = translationtuple[1]
            translationstring = f"\n{key}\t{label}"
            file.write(translationstring)


# language library for file encoding
language_map = {
    "english": "en_US",
    "english_uk": "en_GB",
    "chinese": "zh_CN",
    "chinese_traditional": "zh_TW",
    "spanish": "es",
    "spanish_mexico": "es_MX",
    "portuguese": "pt_BR",
    "portuguese_portugal": "pt_PT",
    "german": "de",
    "french": "fr",
    "japanese": "ja",
    "korean": "ko",
    "dutch": "nl_NL",
    "russian": "ru",
    "thai": "th",
    "swedish": "sv",
    "danish": "da",
    "finnish": "fi",
    "norwegian": "no"
}
# Main


print("Welcome to field label translator.")
UntranslatedLabelsList = get_English_Field_Labels()
print("Sending the following batch to API for translation:", UntranslatedLabelsList)
while True:
    target_language = input(
        "What language would you like to translate to from English? Please reply with only the name of the target language:").strip().lower()
    if target_language in language_map:
        language_code = language_map[target_language]
        break
    else:
        print(f"Invalid language entered, please enter one of the following: english, english_uk, chinese, chinese_traditional, spanish, spanish_mexico, portuguese, portuguese_portugal, german, french, japanese, korean, dutch, russian, thai, swedish, danish, finnish, norwegian.")


MainFullTranslatedKeyandLabelList = []
for batch in range(0, len(UntranslatedLabelsList), 50):
    batchedEnglishTuples = UntranslatedLabelsList[batch:batch+50]
    BatchFullTranslatedKeyandLabelList = translate_batch(
        batchedEnglishTuples, target_language)
    MainFullTranslatedKeyandLabelList.extend(
        BatchFullTranslatedKeyandLabelList)
ValidatedTranslations = validate_and_truncate(
    MainFullTranslatedKeyandLabelList)
print("The following translated labels were received from AI API call:",
      ValidatedTranslations)
create_upload_file(ValidatedTranslations, target_language, language_code)
