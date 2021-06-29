from django.urls import path
from . import views
# settings.py上にある変数を呼び出す等する時に使う
from django.conf import settings
# static : メディアファイルなどを用いる際に使う
from django.conf.urls.static import static

urlpatterns = [
    # path('index/', views.index, name='index'),
    path('', views.classify, name='classify'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
]

# メディアファイルの場所を指定
# document_rootで指定された場所にアップロードされた画像が保存されていく
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)