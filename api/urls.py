from django.urls import path

from api import views

urlpatterns = [
    path('video/<str:video>', views.get_video),
    path('clip-image/<str:image>', views.get_clip_image),
    path('video-url/', views.get_videoURL),
    path('login/<str:email>', views.user_login),
    path('subclip/<str:video>/<int:endTime>', views.get_subclip),
        path('get-video/', views.get_video_name),
    path('save-subclip/', views.save_subclip),
    path('save-subclip-and-evaluation/', views.save_subclip_and_evaluation),
    path('update-subclip/', views.update_clip),
    path('update-subclip-and-evaluation/', views.update_clip_and_evaluation),
    path('subclip-list/', views.get_subclip_list),
    path('registration/', views.register_user),
    path('reset-time/', views.reset_start_time),
        #path('videolist/', views.get_video_list)
    path('remove-file/', views.remove_clip_file),
    path('segments-for-evaluation/<str:logUser>', views.segments_for_evaluation),
    path('finish-segmentation/', views.finish_segmentation),
        path('analize/', views.get_analize),
        path('evaluation/', views.get_evaluation),
    path('add-video/', views.add_video),
    path('split-with-json/', views.split_with_json)
]
