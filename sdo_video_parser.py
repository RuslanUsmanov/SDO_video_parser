import requests
from bs4 import BeautifulSoup

def get_video(id, url, path, session):
    response = session.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    name =  soup.title.string
    for character in r'\/:*?"<>|':
        name = name.replace(character, ' ')
    filename = path + str(id) + '. ' + name + '.mp4'
    print("Downloading " + name)
    video_link = soup.source['src']
    response = session.get(video_link, stream = True)
    with open(filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size = 1024*1024):
            if chunk: 
                file.write(chunk)
    print("Done!")

def get_videocontent(url, username, password, path):
    urls = []

    # Create new session
    session = requests.Session()
    # Get authentication page
    response = session.get(url)
    # Parse it
    soup = BeautifulSoup(response.content, 'html.parser')
    # Prepare payload for POST-request
    payload = {
        'username': username, 
        'password':password,
        'anchor':soup.find('input', {'name': 'anchor'})['value'],
        'logintoken':soup.find('input', {'name': 'logintoken'})['value']
        }
    # Authorize
    session.post(url, data=payload)

    # Get course page
    response = session.get(url)
    # Parse it
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find urls for video files and add them to url list
    for a in soup.find_all("a", class_='aalink'):
        if 'videolecture' in a['href']:
            urls.append(a['href'])
    # Get videos from urls
    for url in urls:
        get_video(urls.index(url) + 1, url, path, session)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Загрузка видеоконтента из СДО')
    parser.add_argument('--url', metavar='https://somesite.com/course/view.php?id=X', type=str, nargs='?', help='Ссылка на курс', required=True)
    parser.add_argument('--login', metavar='foo', type=str, nargs='?', help='Ваш логин', required=True)
    parser.add_argument('--password', metavar='bar', type=str, nargs='?', help='Ваш пароль', required=True)
    parser.add_argument('--dir', metavar='../dir_to_save/', type=str, nargs='?', help='Имя директории, в которой будут сохраняться файлы', required=True) 

    args = parser.parse_args()
 
    if (args.url and args.login and args.password and args.dir):
        get_videocontent(args.url, args.login, args.password, args.dir)
    else:
        parser.print_help()