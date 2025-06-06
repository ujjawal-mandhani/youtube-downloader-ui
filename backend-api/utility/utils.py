import datetime
import bcrypt
import os
import jwt
import yt_dlp
from fastapi.responses import JSONResponse
import re
from datetime import datetime as dt
import ffmpeg


secret_value_jwt = os.getenv("SECRET_KEY")

def update_headers(resp):
  resp.headers['Access-Control-Allow-Origin'] = "*"
  resp.headers['Strict-Transport-Security'] = "max-age=31536000"
  resp.headers['X-Frame-Options'] = "DENY"
  resp.headers['Content-Security-Policy'] = "default-src 'none'"
  resp.headers['X-Content-Type-Options'] = "nosniff"
  #resp.headers['Content-Type'] = "application/json"
  return resp

def get_headers():
  headers = {}
  headers['Access-Control-Allow-Origin'] = "*"
  headers['Strict-Transport-Security'] = "max-age=31536000"
  headers['X-Frame-Options'] = "DENY"
  headers['Content-Security-Policy'] = "default-src 'none'"
  headers['X-Content-Type-Options'] = "nosniff"
  #resp.headers['Content-Type'] = "application/json"
  return headers

def get_date_time():
    return str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
  
def hash_password_func(password):
  salt = bcrypt.gensalt()
  hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
  return hashed_password.decode('utf-8')

def verify_password(password, hashed_password):
  provided_hash = bcrypt.hashpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
  if provided_hash.decode("utf-8") == hashed_password:
    return True
  else:
    return False

def generateJWTToken(payload_customerid):
  expiry_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
  payload = {
            "sub": "youtube-dlp-ui",
            "iss": "youtube-dlp-ui token generation",
            "customerid": payload_customerid,
            "exp": expiry_time
        }
  jwt_token = jwt.encode(payload, secret_value_jwt, algorithm="HS256")
  return jwt_token

def verifyJWTToken(jwt_token):
    try:
        payload = jwt.decode(jwt_token, secret_value_jwt, algorithms=["HS256"])
        customerid = payload.get('customerid')
        return 200, customerid
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return 400, "Token has expired"
    except jwt.InvalidTokenError:
        print("Invalid token")
        return 400, "Invalid token"
      
def build_response(message, status_code: int = 200):
    return JSONResponse(
        status_code=status_code,
        content=message,
        headers=get_headers()
    )

def list_video_details(video_url):
    ydl_opts = {
        'skip_download': True,
        'list_subs': True,
        'writeautomaticsub': True,
        'quiet': True
    }
    try:
      with yt_dlp.YoutubeDL(ydl_opts) as ydl:
          info_dict = ydl.extract_info(video_url, download=False)
          final_data = {
            "title": info_dict["title"]
          }
          subs_sets = set()
          for format in info_dict['formats']:
              final_data[format['format_id']] = {
                "ext": format['ext'],
                "resolution": format['resolution']
              }
          try:
              subs = info_dict["automatic_captions"]
              for sub in subs.keys():
                  for items in subs[sub]:
                      sub_item = sub + " " + ('' if items.get("name") == None else items.get("name"))
                      subs_sets.add(sub_item)
              final_data["subs"] = list(subs_sets)
          except:
              print('No Subs found')
          return 200, final_data
    except:
      return 400, None

def merge_video_audio(video_path, audio_path, output_path, sub_format):
    try:
      video = ffmpeg.input(video_path)
      audio = ffmpeg.input(audio_path)
      if sub_format:
        # Apply subtitles filter (burn subtitles into video)
        video = video.filter('subtitles', sub_format)
      # inputs = [video, audio]
      # if sub_format:
      #     subs = ffmpeg.input(sub_format)
      #     inputs.append(subs)
      # (
      #     ffmpeg
      #     .output(*inputs, output_path, c='copy')
      #     .run(overwrite_output=True)
      # )
      (
        ffmpeg
            .output(video, audio, output_path,
                    vcodec='libx264',  # re-encode video to burn subtitles
                    acodec='aac',       # encode audio (or 'copy' if compatible)
                    strict='experimental',  # to allow aac encoding
                    movflags='faststart')   # optional: better for web playback
            .run(overwrite_output=True)
      )
    except ffmpeg.Error as e:
      print("FFmpeg ERROR:")
      try:
          print("  Command:", getattr(e, 'cmd', 'Unavailable'))
          print("  Stdout:", e.stdout.decode() if e.stdout else "None")
          print("  Stderr:", e.stderr.decode() if e.stderr else "None")
      except Exception as inner:
          print("Error while printing FFmpeg error:", inner)
    except Exception as e:
        print("General Exception:", str(e))
        

def download_video_yt_dlp(array_format_code, customerid, sub_title_format='', output_path='/home/videos/'):
  output_path = output_path + str(customerid) + '/' + str(dt.now().strftime('%Y-%m-%d'))
  video_url = array_format_code["video_url"]
  flag_audio_video_checker = {
    "audio": 0,
    "video": 0
  }
  if sub_title_format in [None, '']:
    sub_title_format = ''
  title = array_format_code["title"].replace('"', '') ## Bug to remove code where title contains " double quote 
  if len(array_format_code["audio_video_formats"].items()) != 2 and not video_url.__contains__('instagram'):
    return 400, "Please select one Audio format and one video format"
  if video_url.__contains__('instagram') and len(array_format_code["audio_video_formats"].items()) != 1:
    return 400, "Please select only one format"
  for id, data in array_format_code["audio_video_formats"].items():
    pattern = r"^\d+x\d+$"
    if data["resolution"] == "audio only":
      flag_audio_video_checker["audio"] = flag_audio_video_checker["audio"] + 1
    if bool(re.match(pattern, data["resolution"])):
      flag_audio_video_checker["video"] = flag_audio_video_checker["video"] + 1
  if (flag_audio_video_checker["video"] != 1 or flag_audio_video_checker["video"] != 1) and not video_url.__contains__('instagram'):
    return 400, "Please select one Audio format and one video format"
  if video_url.__contains__('instagram') and flag_audio_video_checker["video"] != 1:
    return 400, "Please select one Audio format and one video format"
  for id, data in array_format_code["audio_video_formats"].items():
    print(id, data)
    format_code = id
    ext = data["ext"]
    options = {
        'format': format_code,
        "writesubtitles": True,
        "subtitleslangs": [sub_title_format.split(' ')[0]],
        "postprocessors": [
            {"key": "FFmpegSubtitlesConvertor", "format": "srt"}
        ],
        "writeautomaticsub": True,
        'outtmpl': f'{output_path}/{title}.{ext}'
    }
    try:
      if sub_title_format == '':
          for item in ["writesubtitles", "subtitleslangs", "postprocessors", "writeautomaticsub"]:
              options.pop(item)
      with yt_dlp.YoutubeDL(options) as ydl:
          ydl.download([video_url])
    except Exception as E:
      print(E)
      return 400, str(E)
  if not video_url.__contains__('instagram'):
    ffmpeg_string = "ffmpeg -y -i " + " -i ".join(list(map(lambda x:  f'"{output_path}/{title}.{x["ext"]}"', array_format_code["audio_video_formats"].values())))
    if sub_title_format != '':
      ffmpeg_string = ffmpeg_string + " -i " + f'"{output_path}/{title}.{sub_title_format.split(' ')[0]}.srt"'
      ffmpeg_final = f'{ffmpeg_string} -map 1:v:0 -map 0:a:0 -map 2:0 -c:v copy -c:a copy -c:s mov_text "{output_path}/{title}_updated.mp4"'
      rm_cmd = f'rm {" ".join(list(map(lambda x:  f'"{output_path}/{title}.{x["ext"]}"', array_format_code["audio_video_formats"].values())))} "{output_path}/{title}.{sub_title_format.split(' ')[0]}.srt"'
    else:
      ffmpeg_final = f'{ffmpeg_string} -c copy "{output_path}/{title}_updated.mp4"'
      rm_cmd = f'rm {" ".join(list(map(lambda x:  f'"{output_path}/{title}.{x["ext"]}"', array_format_code["audio_video_formats"].values())))}'
    print(ffmpeg_final)
    os.system(ffmpeg_final)
    # audio_video_details = list(map(lambda x:  f'{output_path}/{title}.{x["ext"]}', array_format_code["audio_video_formats"].values()))
    # print(":::::::::::::::::Merger", audio_video_details[0], audio_video_details[1], f"{output_path}/{title}_updated.mp4")
    # merge_video_audio(audio_video_details[0], audio_video_details[1], f"{output_path}/{title}_updated.mp4", f"{output_path}/{title}.{sub_title_format.split(' ')[0]}.srt")
    print(rm_cmd)
    os.system(rm_cmd)
    return 200, {
      "video_path": f"{output_path}/{title}_updated.mp4"
    }
  return 200, {
      "video_path": f"{output_path}/{title}.mp4"
    }