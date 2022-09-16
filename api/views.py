# from django.http import HttpResponse, Http404, HttpResponseNotFound
import json
import mimetypes
import os
import cv2

from django.http import HttpResponse, Http404, JsonResponse
from rest_framework.decorators import api_view
from api.models import User, Video, Segment, Analize, Evaluation
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from pytube import YouTube

PATH_SEGMENTS = os.path.dirname(os.path.abspath(__file__)) + '/../data/segments/'
PATH_IMAGES = os.path.dirname(os.path.abspath(__file__)) + '/../data/images/'
PATH_VIDEO = os.path.dirname(os.path.abspath(__file__)) + '/../data/'
VIDEO_URL = 'http://127.0.0.1:8000/api/video/'
IMAGE_URL = 'http://127.0.0.1:8000/api/clip-image/'
loggedUser = ''
startTime = 0
temporaryStartTime = 0
isClip = 'clip-'
subClipName = ''
videoName = ''


@api_view(['GET'])
def get_video(request, video):
    """This method aims to display the required video or segment"""

    global isClip, startTime, PATH_SEGMENTS, PATH_VIDEO
    if isClip in video:
        PATH = PATH_SEGMENTS + str(video) + '.mp4'
    else:
        PATH = PATH_VIDEO + '/../data/' + str(video) + '.mp4'
        startTime = 0
    try:
        with open(PATH, 'rb') as path:
            # Set the mime type
            mime_type, _ = mimetypes.guess_type(PATH)

            # Set the return value of the HttpResponse
            response = HttpResponse(path, content_type='video/mp4')

            # Set the HTTP header for sending to browser
            response['Content-Disposition'] = "inline; filename=%s"

            return response

    except FileNotFoundError:
        raise Http404("Video not found")


@api_view(['GET'])
def get_videoURL(request):
    """This method aims to return the required video or segment url"""

    global videoName, VIDEO_URL
    videoName = get_video_name()
    if videoName == 'none':
        responseData = {
            'data': {
                'video': videoName,
                'url': videoName
            }
        }
    else:
        responseData = {
            'data': {
                'video': videoName,
                'url': VIDEO_URL + str(videoName)
            }
        }

    return JsonResponse(responseData)


def get_video_name():
    """This method aims to search the video to be returned
        1. check if there are segmented videos
            1.1. if there are not segmented videos, but there are saved segments, delete all segments
                 (the last user did not save the split operation)
            1.2. else, return a video that was not segmented"""

    global PATH_SEGMENTS, PATH_IMAGES
    segmentedVideo = Analize.objects.filter()
    segVidList = list(segmentedVideo)
    video = Video.objects.filter()
    videoList = list(video)
    if segVidList.__len__() == 0:
        segment = Segment.objects.filter()
        segmentList = list(segment)
        if segmentList.__len__() > 0:
            dirSegments = PATH_SEGMENTS
            dirImages = PATH_IMAGES
            segment.delete()
            for f in os.listdir(dirSegments):
                os.remove(os.path.join(dirSegments, f))
            for f in os.listdir(dirImages):
                os.remove(os.path.join(dirImages, f))

        return videoList[0].name
    else:
        returnList = []
        for segVid in segVidList:
            for vid in videoList:
                if segVid.video_id != vid.identifier:
                    Segment.objects.filter(video_ref=vid.identifier).delete()
                    dirSegments = PATH_SEGMENTS
                    dirImages = PATH_IMAGES
                    for f in os.listdir(dirSegments):
                        if vid.name in f:
                            os.remove(os.path.join(dirSegments, f))
                    for f in os.listdir(dirImages):
                        if vid.name in f:
                            os.remove(os.path.join(dirImages, f))
                    returnList.append(vid)
        if returnList.__len__() > 0:
            return returnList[0].name
        else:
            return 'none'


@api_view(['GET'])
def user_login(request, email):
    """This method aims to check if passed email exist on db for return encrypted password"""

    global loggedUser
    loggedUser = email
    user = User.objects.values_list('password', flat=True).filter(email=str(email))
    userPw = list(user)
    isAdmin = User.objects.values_list('admin', flat=True).filter(email=str(email))
    admin = list(isAdmin)
    if userPw.__len__() == 1:
        responseData = {
            'data': {
                'response': userPw,
                'admin': admin
            }
        }
    else:
        userPw.append('Error')
        admin.append('false')
        responseData = {
            'data': {
                'response': userPw,
                'admin': admin
            }
        }
    return JsonResponse(responseData)


# ADD USER
# model = User(name='Ciao', surname='Ciao', email='ciao@gmail.com')
# model.save()

# REMOVE USER
# model = User.objects.filter(identifier = 2)
# model.delete()


# EXTRACT SUBCLIP VIDEO
@api_view(['GET'])
def get_subclip(request, video, endTime):
    """This method aims to create subclip and thumbnail from original video"""

    # FFMPEG
    # https://stackoverflow.com/questions/37317140/cutting-out-a-portion-of-video-python
    global startTime, subClipName, videoName, temporaryStartTime, PATH_SEGMENTS, PATH_VIDEO, PATH_IMAGES, VIDEO_URL
    file = PATH_VIDEO + str(video) + '.mp4'
    # ffmpeg_extract_subclip("full_video.mp4", start_seconds, end_seconds, targetname="cut_video.mp4")
    videoName = str(video)
    endTime = endTime
    temporaryStartTime = startTime
    if endTime > temporaryStartTime:
        subClipName = 'clip-' + str(video) + str(startTime) + '-' + str(endTime)
        ffmpeg_extract_subclip(file, startTime, endTime, targetname=PATH_SEGMENTS + subClipName + '.mp4')

        os.system('ffmpeg -i ' + str(file) + ' -ss ' + str(startTime) +
                  ' -vframes 1 ' + PATH_IMAGES +
                  str(subClipName) + '.jpg')

        startTime = endTime

        responseData = {
            'data': {
                'video': subClipName,
                'url': VIDEO_URL + str(subClipName)
            }
        }

    return JsonResponse(responseData)


@api_view(['GET'])
def remove_clip_file(request):
    """This method aims to delete subclip and thumbnail, because user not saved the operation"""

    global subClipName, PATH_SEGMENTS, PATH_IMAGES
    os.remove(PATH_SEGMENTS + subClipName + '.mp4')
    os.remove(PATH_IMAGES + subClipName + '.jpg')


@api_view(['GET'])
def reset_start_time(request):
    """This method aims to take the last subclip saved start time, because user not saved the operation"""

    global startTime, temporaryStartTime
    startTime = temporaryStartTime


@api_view(['POST'])
def save_subclip(request):
    """This method aims to save subclip, with name, reference video, creator and type of evaluation"""

    global loggedUser, videoName, subClipName
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    type = body['type']
    loggedUser = body['logged-user']
    user = User.objects.get(email=loggedUser)
    video = Video.objects.get(name=videoName)
    model = Segment(name=subClipName, video_ref=video, creator=user, type_val=type)
    model.save()

    responseData = {
        'data': {
            'response': 'Subclip added'
        }
    }
    return JsonResponse(responseData)


@api_view(['POST'])
def save_subclip_and_evaluation(request):
    """This method aims to save subclip if user insert type of evaluation,
    it will also be stored in the general list of evaluation"""

    global loggedUser, videoName, subClipName
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    type = body['type']
    loggedUser = body['logged-user']
    user = User.objects.get(email=loggedUser)
    video = Video.objects.get(name=videoName)
    model = Segment(name=subClipName, video_ref=video, creator=user, type_val=type)
    model.save()
    segment = Segment.objects.get(name=subClipName)
    evaluation = Evaluation(user=user, segment_ref=segment, type_val=type)
    evaluation.save()
    eval = Evaluation.objects.filter()

    responseData = {
        'data': {
            'response': 'Subclip and evaluation added'
        }
    }
    return JsonResponse(responseData)


@api_view(['GET'])
def get_subclip_list(request):
    """This method aims to return all subclip of required video"""

    global videoName, VIDEO_URL, IMAGE_URL
    # videoName = 'videoTest'

    # user = User.objects.get(email=loggedUser)
    video = Video.objects.get(name=videoName)

    # Is not important who create segments of this video
    # subclipModels = Segment.objects.filter(video_ref_id=video.identifier, creator_id=user.identifier)

    subclipModels = Segment.objects.filter(video_ref_id=video.identifier)
    subclipList = list(subclipModels.values())
    prepare_json = {"list": [{"sub-clip": clip['name'],
                              "clip-url": VIDEO_URL + clip['name'],
                              "clip-type": clip['type_val'],
                              "clip-image": IMAGE_URL + clip['name']}
                             for clip in subclipList]}

    json_to_load = json.dumps(prepare_json)
    responseData = json.loads(json_to_load)
    return JsonResponse(responseData, safe=False)


@api_view(['GET'])
def segments_for_evaluation(request, logUser):
    """This method aims to return all subclip of required video for evaluation
        1. if the logged user is the creator of the subclip and if there is at least one unanalyzed clip,
           all the subclip of that video will be returned so that he can all be analyzed again
        2. else, all the subclip of random segmented video will be returned so that he can all be analyzed"""

    # controlla se ci sono elementi in analize, se ci sono allora restituisci i segmenti del video in analize
    responseList = []
    controlSegList = []
    global loggedUser, VIDEO_URL, IMAGE_URL
    loggedUser = str(logUser)
    user = User.objects.get(email=loggedUser)
    segmentedVideo = Segment.objects.filter(creator=user)
    segmentedVideoId = list(segmentedVideo)
    if segmentedVideoId.__len__() > 0:
        for seg in segmentedVideoId:
            if seg.type_val == "ANALIZE IT!":
                controlSegList.append(seg)
        if controlSegList.__len__() > 0:
            segmentedVideo = Segment.objects.filter(creator=user, video_ref=controlSegList[0].video_ref.identifier)
            responseList = list(segmentedVideo.values())
            prepare_json = {"list": [{"sub-clip": clip['name'],
                                      "clip-url": VIDEO_URL + clip['name'],
                                      "clip-type": clip['type_val'],
                                      "clip-image": IMAGE_URL + clip['name']}
                                     for clip in responseList],
                            "creator": 'yes'}

            json_to_load = json.dumps(prepare_json)
            responseData = json.loads(json_to_load)
            return JsonResponse(responseData, safe=False)
        else:
            responseData = {
                'list': []
            }
            return JsonResponse(responseData)
    else:
        listSegmentedVideo = []
        segmentList = []
        segmentedVideo = Segment.objects.values_list('video_ref', flat=True).filter()
        segmentedVideoId = list(segmentedVideo)
        for seg_video in segmentedVideoId:
            video = Video.objects.get(identifier=seg_video)
            listSegmentedVideo.append(video.identifier)
        listVideoId = list(dict.fromkeys(listSegmentedVideo))
        segment = Segment.objects.filter(video_ref=listVideoId[0])
        segmentList = list(segment.values())
        prepare_json = {"list": [{"sub-clip": clip['name'],
                                  "clip-url": VIDEO_URL + clip['name'],
                                  "clip-type": 'ANALIZE IT!',
                                  "clip-image": IMAGE_URL + clip['name']}
                                 for clip in segmentList],
                        'creator': 'no'}

        json_to_load = json.dumps(prepare_json)
        responseData = json.loads(json_to_load)
        return JsonResponse(responseData, safe=False)


@api_view(['POST'])
def update_clip(request):
    """This method aims to update required subclip evaluation"""

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    name = body['name']
    type = body['type']
    Segment.objects.filter(name=name).update(type_val=type)

    responseData = {
        'data': {
            'response': 'Subclip updated'
        }
    }
    return JsonResponse(responseData)


@api_view(['POST'])
def update_clip_and_evaluation(request):
    """This method aims to update subclip if user insert type of evaluation,
    it will also be stored in the general list of evaluation"""

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    user = body['user']
    segment = body['name']
    type = body['type']
    userModel = User.objects.get(email=user)
    segmentModel = Segment.objects.get(name=segment)
    Segment.objects.filter(name=segment).update(type_val=type)
    evaluation = Evaluation.objects.filter(segment_ref=segmentModel, user=userModel)
    evaluationList = list(evaluation)
    if evaluationList.__len__() > 0:
        Evaluation.objects.filter(segment_ref=segmentModel, user=userModel).update(type_val=type)
    else:
        evaluation = Evaluation(user=userModel, segment_ref=segmentModel, type_val=type)
        evaluation.save()

    eval = Evaluation.objects.filter()
    responseData = {
        'data': {
            'response': 'Subclip and evaluation updated'
        }
    }
    return JsonResponse(responseData)


@api_view(['GET'])
def get_clip_image(request, image):
    """This method aims to return the required video tumblnail or segment url"""

    global PATH_IMAGES
    PATH = PATH_IMAGES + str(image) + '.jpg'

    try:
        with open(PATH, 'rb') as path:
            # Set the mime type
            mime_type, _ = mimetypes.guess_type(PATH)

            # Set the return value of the HttpResponse
            response = HttpResponse(path, content_type=mime_type)

            # Set the HTTP header for sending to browser
            response['Content-Disposition'] = "inline; filename=%s" % image

            # return response
            return response

    except FileNotFoundError:
        raise Http404("Image not found")


@api_view(['POST'])
def register_user(request):
    """This method aims to register the new user, checking if that email already exists"""

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    name = body['name']
    surname = body['surname']
    email = body['email']
    password = body['password']
    user = User.objects.values_list('email', flat=True).filter()
    userList = list(user)
    check = 1
    for user in userList:
        if user != email:
            check = 1
        else:
            check = 0
    if check == 1:
        model = User(name=name, surname=surname, email=email, password=password)
        model.save()

    responseData = {
        'data': {
            'response': email + ' registered!'
        }
    }
    return JsonResponse(responseData)


@api_view(['POST'])
def finish_segmentation(request):
    """This method aims to save that the required video has been segmented"""

    global loggedUser, videoName
    # ADD VIDEO ANALIZATION FROM USER
    user = User.objects.get(email=loggedUser)
    video = Video.objects.get(name=videoName)
    model = Analize(user=user, video=video)
    model.save()

    responseData = {
        'data': {
            'response': 'finish segmentation'
        }
    }
    return JsonResponse(responseData)


@api_view(['POST'])
def add_video(request):
    """This method aims to add new video by YouTube url"""

    global PATH_VIDEO
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    url = body['url']
    name = body['name']
    fileName = name.replace(" ", "")
    YouTube(url).streams.get_highest_resolution().download(
        output_path=PATH_VIDEO, filename=str(fileName) + '.mp4')
    model = Video(name=fileName)
    model.save()
    responseData = {
        'data': {
            'response': 'added'
        }
    }
    return JsonResponse(responseData)

    # prova video
    # https://www.youtube.com/watch?v=MyjBKCSTQOk

    yt = YouTube(url)
    # print(yt.captions.get('en-US').xml_captions)
    print(yt.captions)
    # en_caption_data = yt.captions['a.en']
    # srt_format = en_caption_data.xml_caption_to_srt(en_caption_data.xml_captions)
    # print(srt_format)


@api_view(['POST'])
def split_with_json(request):
    """This method aims to segment the required by specific file json,
    the start and end times of each clip that the user wants to create will be passed, the file name will be
    generated automatically using the name of the uploaded video"""

    global startTime, subClipName, videoName, temporaryStartTime, loggedUser, PATH_SEGMENTS, PATH_IMAGES
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    jsonFile = json.dumps(body['file']['segments'])
    segmentList = json.loads(jsonFile)
    file = os.path.dirname(os.path.abspath(__file__)) + '/../data/' + str(videoName) + '.mp4'
    for segment in segmentList:
        endTime = segment['end-time']
        temporaryStartTime = segment['start-time']
        if endTime > temporaryStartTime:
            subClipName = 'clip-' + str(videoName) + str(segment['start-time']) + '-' + str(endTime)
            ffmpeg_extract_subclip(file, startTime, endTime, targetname=PATH_SEGMENTS + subClipName + '.mp4')
            os.system('ffmpeg -i ' + str(file) + ' -ss ' + str(startTime) +' -vframes 1 ' + PATH_IMAGES +
                      str(subClipName) + '.jpg')
            startTime = endTime

        user = User.objects.get(email=loggedUser)
        video = Video.objects.get(name=videoName)
        model = Segment(name=subClipName, video_ref=video, creator=user, type_val='ANALIZE IT!')
        model.save()
    responseData = {
        'data': {
            'response': 'segment with json'
        }
    }
    return JsonResponse(responseData)


@api_view(['GET'])
def get_analize(request):
    # Analize.objects.filter().delete()
    analize = Analize.objects.filter()
    analizeList = list(analize.values())

    responseData = {
        'data': {
            'response': analizeList
        }
    }
    return JsonResponse(responseData)


@api_view(['GET'])
def get_evaluation(request):
    eval = Evaluation.objects.filter()
    evalList = list(eval.values())

    responseData = {
        'data': {
            'response': evalList
        }
    }
    return JsonResponse(responseData)
