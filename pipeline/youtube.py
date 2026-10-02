"""YouTube: one-time auth (local), upload (publisher bot), stats (analyst bot).
  python pipeline/youtube.py auth client_secret.json   -> opens browser, stores token as GitHub secret YT_TOKEN
  python pipeline/youtube.py upload <dir with episode.mp4, short.mp4, thumbnail.jpg, captions.srt, metadata.json>
  python pipeline/youtube.py stats docs/analytics.json"""
import datetime as dt, json, os, subprocess, sys

SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube.force-ssl',
          'https://www.googleapis.com/auth/yt-analytics.readonly']
PUBLISH_HOUR_UTC = 17  # ~1pm US Eastern / 6pm UK, after school


def creds():
    from google.oauth2.credentials import Credentials
    return Credentials.from_authorized_user_info(json.loads(os.environ['YT_TOKEN']), SCOPES)


def yt(api='youtube', v='v3'):
    from googleapiclient.discovery import build
    return build(api, v, credentials=creds(), cache_discovery=False)


def auth(secret_file):
    from google_auth_oauthlib.flow import InstalledAppFlow
    c = InstalledAppFlow.from_client_secrets_file(secret_file, SCOPES).run_local_server(port=0, prompt='consent')
    subprocess.run(['gh', 'secret', 'set', 'YT_TOKEN'], input=c.to_json(), text=True, check=True)
    subprocess.run(['gh', 'variable', 'set', 'AUTO_UPLOAD', '--body', 'false'], check=True)
    print('Saved YouTube login as GitHub secret YT_TOKEN. Analytics will start tonight.\n'
          'After Google approves your API audit, run:  gh variable set AUTO_UPLOAD --body true')


def next_slot(y):
    uploads = y.channels().list(part='contentDetails', mine=True).execute()['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    ids = [i['contentDetails']['videoId'] for i in y.playlistItems().list(part='contentDetails', playlistId=uploads, maxResults=20).execute().get('items', [])]
    times = [v['status'].get('publishAt') for v in y.videos().list(part='status', id=','.join(ids)).execute().get('items', [])] if ids else []
    now = dt.datetime.now(dt.timezone.utc)
    day = (now + dt.timedelta(hours=3)).date()
    if now + dt.timedelta(hours=3) > dt.datetime.combine(day, dt.time(PUBLISH_HOUR_UTC), dt.timezone.utc): day += dt.timedelta(days=1)
    booked = [dt.datetime.fromisoformat(t.replace('Z', '+00:00')).date() for t in times if t]
    if booked and day <= max(booked): day = max(booked) + dt.timedelta(days=1)
    return dt.datetime.combine(day, dt.time(PUBLISH_HOUR_UTC), dt.timezone.utc)


def insert(y, path, title, desc, tags, when):
    from googleapiclient.http import MediaFileUpload
    body = dict(snippet=dict(title=title, description=desc, tags=tags, categoryId='1', defaultLanguage='en', defaultAudioLanguage='en'),
                status=dict(privacyStatus='private', publishAt=when.isoformat().replace('+00:00', 'Z'),
                            selfDeclaredMadeForKids=True, containsSyntheticMedia=False, embeddable=True, license='youtube'))
    req = y.videos().insert(part='snippet,status', body=body, media_body=MediaFileUpload(path, chunksize=16 * 1024 * 1024, resumable=True))
    resp = None
    while resp is None: _, resp = req.next_chunk()
    return resp['id']


def upload(d):
    from googleapiclient.http import MediaFileUpload
    y, m = yt(), json.load(open(f'{d}/metadata.json', encoding='utf-8'))
    when = next_slot(y)
    vid = insert(y, f'{d}/episode.mp4', m['title'], m['description'], m['tags'], when)
    y.thumbnails().set(videoId=vid, media_body=MediaFileUpload(f'{d}/thumbnail.jpg')).execute()
    y.captions().insert(part='snippet', body=dict(snippet=dict(videoId=vid, language='en', name='English')),
                        media_body=MediaFileUpload(f'{d}/captions.srt', mimetype='application/octet-stream')).execute()
    sid = insert(y, f'{d}/short.mp4', m['short_title'], m['short_description'] + f'\n\nWatch the full episode: https://youtu.be/{vid}',
                 m['tags'], when + dt.timedelta(hours=3))
    print(json.dumps(dict(video=vid, short=sid, publish_at=when.isoformat())))


def stats(dst):
    y = yt()
    ch = y.channels().list(part='snippet,statistics,contentDetails', mine=True).execute()['items'][0]
    uploads = ch['contentDetails']['relatedPlaylists']['uploads']
    ids = [i['contentDetails']['videoId'] for i in y.playlistItems().list(part='contentDetails', playlistId=uploads, maxResults=50).execute().get('items', [])]
    vids = y.videos().list(part='snippet,statistics,status,contentDetails', id=','.join(ids)).execute().get('items', []) if ids else []
    ya, today = yt('youtubeAnalytics', 'v2'), dt.date.today()
    per = {r[0]: r[1:] for r in ya.reports().query(ids='channel==MINE', startDate='2020-01-01', endDate=str(today), dimensions='video', sort='-views',
           metrics='views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage', maxResults=200).execute().get('rows', [])}
    daily = ya.reports().query(ids='channel==MINE', startDate=str(today - dt.timedelta(days=28)), endDate=str(today), dimensions='day',
                               metrics='views,estimatedMinutesWatched,subscribersGained').execute().get('rows', [])
    s = ch['statistics']
    json.dump(dict(
        updated=dt.datetime.now(dt.timezone.utc).isoformat(timespec='minutes'),
        channel=dict(title=ch['snippet']['title'], subs=int(s.get('subscriberCount', 0)), views=int(s.get('viewCount', 0)), videos=int(s.get('videoCount', 0))),
        daily=[dict(date=d, views=v, minutes=mn, subs=sg) for d, v, mn, sg in daily],
        videos=[dict(id=v['id'], title=v['snippet']['title'], published=v['status'].get('publishAt') or v['snippet']['publishedAt'],
                     privacy=v['status']['privacyStatus'], views=int(v['statistics'].get('viewCount', 0)), likes=int(v['statistics'].get('likeCount', 0)),
                     minutes=per.get(v['id'], [0, 0])[1], avg_view_sec=per.get(v['id'], [0, 0, 0])[2], avg_view_pct=per.get(v['id'], [0, 0, 0, 0])[3],
                     short='#shorts' in v['snippet']['title'].lower()) for v in vids]),
        open(dst, 'w'), indent=1)
    print(f'{len(vids)} videos, {s.get("subscriberCount")} subscribers')


if __name__ == '__main__':
    {'auth': auth, 'upload': upload, 'stats': stats}[sys.argv[1]](sys.argv[2])
