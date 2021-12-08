from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from auto_post_social_media import get_driver
import selenium
import time
from datetime import datetime
from pprint import pprint
import json
from bs4 import BeautifulSoup
import lxml
import re


def open_google_doc_on_driver(doc_id):
    global driver
    driver = get_driver(headless=False)
    driver.get(f"https://docs.google.com/document/d/{doc_id}/edit")
    while True:
        try:
            driver.page_source
            time.sleep(1)
        except selenium.common.exceptions.NoSuchWindowException:
            driver.quit()
            break
    print("END")


def create_google_doc(json_creads_dir, email):
    scope = ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive",
             'https://www.googleapis.com/auth/documents']
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_creads_dir, scope)
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {
        'name': 'My Report 3',
        'mimeType': 'application/vnd.google-apps.document'  # Modified
    }
    file = service.files().create(body=file_metadata,
                                  fields='id').execute()
    fileId = file.get('id')
    permission1 = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': email,  # Please set your email of Google account.
    }
    service.permissions().create(fileId=fileId, body=permission1).execute()
    return fileId


def get_needed_data_from_json():
    with open('json_text.json') as j_f:
        json_test = json.load(j_f)
    events = []
    for event in json_test:
        if event['eventType'] in ("Simulive Replay", "Webinar"):
            speaker = event['speakers'][0]
            e = {"short_event":{
                "date": datetime.strptime(event['startTime'], "%Y-%m-%dT%H:%M:%SZ").strftime('*%B %d, %Y') + '++bold++',
                "name": event['eventName'].replace('\n', '. '),
                "speaker": f"Presented by {speaker['name']}".replace('\n', '. ')
            },
            "full_event":{
                "date": datetime.strptime(event['startTime'], "%Y-%m-%dT%H:%M:%SZ").strftime('*%B %d, %Y') + '++bold++',
                "name": event['eventName'].replace('\n', '. ') + '++bold++',
                "speaker": f"Presented by {speaker['name']}".replace('\n', '. ') + '++bold++',
                "duration": f'Duration: {event["duration"]}++bold++\n',
                "description": event["description"],
                "creationDate": 'Originally Recorded '+ datetime.strptime(event["creationDate"], "%Y-%m-%dT%H:%M:%SZ").strftime('%B %d, %Y'),
                "speaker_bio_name": f"Presented by {speaker['name']}" + '++bold++' + '++line++' ,
                "speaker_bio": BeautifulSoup(speaker['bio'], 'lxml').text.replace("seehttp", "see http")
            }
            }
            events.append(e)
    events.sort(key=lambda event_date: datetime.strptime(event_date["short_event"]["date"], "*%B %d, %Y++bold++"))
    return events


def write_to_google_docs(json_creads_dir, fileId, events):
    scope = ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive",
             'https://www.googleapis.com/auth/documents']
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_creads_dir, scope)
    service = build('docs', 'v1', credentials=creds)
    short_events_text = ""
    full_events_text = ""
    for event in events:
        short_events_text += f'{event["short_event"]["date"]}\n{event["short_event"]["name"]}\n{event["short_event"]["speaker"]}\n\n'
        full_events_text += f'{event["full_event"]["date"]}\n{event["full_event"]["name"]}\n{event["full_event"]["speaker"]}' \
                            f'\n{event["full_event"]["duration"]}\n{event["full_event"]["description"]}\n\n{event["full_event"]["creationDate"]}' \
                            f'\n\n{event["full_event"]["speaker_bio_name"]}\n{event["full_event"]["speaker_bio"]}\n\n++new page++'
    full_events_text = full_events_text.replace('	<li>\n	', "++bullet++").replace('	<li>',"++bullet++").replace('	<li ', '++bullet++<li ')\
        .replace("&nbsp;", '').replace(':&nbsp; ', ' ').replace('ᐧ', '').replace('<p></p>', '').replace('<strong>', '++bold++')
    tmp = BeautifulSoup(full_events_text, 'lxml').text
    print(tmp)
    full_events_text = re.sub(r'\n\s*\n', '\n\n', tmp).strip().strip('++new page++')
    json_representation = [{
        'insertText': {
            'endOfSegmentLocation': {
                'segmentId': '',
            },
            'text': "\n++title++++bold++SUMMARY OF WEBINARS\n\n" + short_events_text + '++new page++'
                    + "\n++title++++bold++FULL DESCRIPTIONS OF WEBINARS & SPEAKER BIOS\n\n" + full_events_text
        },
    }]
    resp = service.documents().batchUpdate(
        documentId=fileId,
        body={
            'requests': json_representation
        }
    ).execute()
    print(resp)
    doc = service.documents().get(documentId=fileId).execute()
    doc_content = doc.get('body').get('content')
    pprint(doc_content)
    docs_style_updates = []
    page_break_offset = 0
    for element in doc_content:
        try:
            element_content = element['paragraph']['elements'][0]['textRun']['content']
            if '++title++' in element_content:
                docs_style_updates.append({
                    "updateParagraphStyle": {
                        'range': {
                            'startIndex': element['startIndex'] + page_break_offset,
                            'endIndex': element['endIndex'] + page_break_offset
                        },
                        "paragraphStyle": {
                        "alignment": "CENTER"
                        },
                        "fields": "alignment"
                    }
                }, )
                docs_style_updates.append({
                    "updateTextStyle": {
                        'range': {
                            'startIndex': element['startIndex'] + page_break_offset,
                            'endIndex': element['endIndex'] + page_break_offset
                        },
                        "fields": "fontSize",
                        "textStyle": {"fontSize": {"magnitude": 12, "unit": "pt"}},
                    }
                }, )
            if '++bold++' in element_content:
                docs_style_updates.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': element['startIndex'] + page_break_offset,
                        'endIndex': element['endIndex'] + page_break_offset
                    },
                    'textStyle': {
                        'bold': True,
                    },
                    'fields': 'bold'
                }
            },)
            if '++line++' in element_content:
                docs_style_updates.append({
                    'updateTextStyle': {
                        'range': {
                            'startIndex': element['startIndex'] + page_break_offset,
                            'endIndex': element['endIndex'] + page_break_offset
                        },
                        'textStyle': {
                            'underline': True,
                        },
                        'fields': 'underline'
                    }
                }, )
            if '++bullet++' in element_content:
                docs_style_updates.append({
                    "createParagraphBullets": {
                        'range': {
                            'startIndex': element['startIndex'] + page_break_offset,
                            'endIndex': element['endIndex'] + page_break_offset
                        },
                        "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
                    }
                }, )
            if '++new page++' in element_content:
                docs_style_updates.append({
                    'insertPageBreak': {
                        'location': {
                            'index': element['startIndex'] + page_break_offset,
                        },
                }})
                page_break_offset += 2
        except KeyError:
            pass
    service.documents().batchUpdate(
        documentId=fileId, body={'requests': docs_style_updates}).execute()
    replace_text_updates = [
        {
            'replaceAllText': {
                'containsText': {
                    'text': '++bold++',
                    'matchCase': 'true'
                },
                'replaceText': '',
            }},
        {
            'replaceAllText': {
                'containsText': {
                    'text': '++new page++',
                    'matchCase': 'true'
                },
                'replaceText': '',
            }},
        {
            'replaceAllText': {
                'containsText': {
                    'text': '++line++',
                    'matchCase': 'true'
                },
                'replaceText': '',
            }},
        {
            'replaceAllText': {
                'containsText': {
                    'text': '++bullet++',
                    'matchCase': 'true'
                },
                'replaceText': '',
            }},
        {
            'replaceAllText': {
                'containsText': {
                    'text': '++title++',
                    'matchCase': 'true'
                },
                'replaceText': '',
            }},
    ]
    service.documents().batchUpdate(documentId=fileId, body={'requests': replace_text_updates}).execute()


def write_to_google_calendar(evens):
    json_data = get_needed_data_from_json()
    scope = ['https://www.googleapis.com/auth/calendar']
    creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/macbook/Downloads/ss.json', scope)
    service = build('calendar', 'v3', credentials=creds)
    for event in evens:
        if event['eventType'] in ("Simulive Replay", "Webinar"):
            pprint(event)
            speaker = event['speakers'][0]
            event_ = {
                'summary': 'Google I/O 2015',
                'location': '800 Howard St., San Francisco, CA 94103', '2022-05-28T09:00:00-07:00'
                'description': event["description"],
                'start': {
                    'dateTime': event["startTime"],
                },
                'end': {
                    'dateTime': event["endTime"],
                },
            }
            # print(event_['start']['dateTime'])
            service.events().insert(calendarId='benharkatdjalil@gmail.com', body=event_).execute()
            break
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='benharkatdjalil@gmail.com', timeMin=datetime.utcnow().isoformat() + 'Z',
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event)


if __name__ == 'main':
    with open('json_text.json') as j_f:
        json_test = json.load(j_f)

    # need to get CalendarId and add the service email in https://calendar.google.com/calendar/u/0/r/settings/calendar/YmVuaGFya2F0ZGphbGlsQGdtYWlsLmNvbQ?sf=true
    write_to_google_calendar(json_test)


    # # doc_id = create_google_doc('/Users/macbook/Downloads/ss.json', 'benharkatdjalil@gmail.com')
    # events = get_needed_data_from_json()
    # doc_id = "1kfA1TzdqRPo83ad1EzA5mLHwmQ0Iy841YHR3pO6XLrA"
    # print("doc id", doc_id)
    # # open_google_doc_on_driver(doc_id)
    # write_to_google_docs('/Users/macbook/Downloads/ss.json', doc_id, events)
