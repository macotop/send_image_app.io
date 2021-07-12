import sys, os
sys.path.append('../')
import model
sys.path.append('../')
from model import animalmodel
from pathlib import Path
from glob import glob

from django.shortcuts import render, redirect
from .forms import ImageForm, LoginForm, SignUpForm
from .models import ModelFile, _user_profile_avator_upload_to

import torch
import torchvision
import numpy as np
from torchvision import transforms
from torchvision import datasets
from PIL import Image

# django.contrib.auth.views: ユーザ認証に関するモジュールが定義
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate

# def index(request):
#     return render(request, 'send_image_app/index.html')

@login_required
def classify(request):
    if request.method == 'POST':
        # ImageFormの中のPOSTとFILESを受け取る必要がある
        form = ImageForm(request.POST, request.FILES)
        # 検証結果問題なければ保存
        if form.is_valid():
            form.save()
            # ファイル名のハッシュ化
            # 画像の保存されるディレクトリを指定
            path = Path("media/documents")
            # 指定したディレクトリ直下の全てのファイルを取ってくる
            all_files = list(path.glob("*"))
            # 全てのファイルパスに対して、更新時刻を付加
            file_updates = {file_path: os.stat(file_path).st_mtime for file_path in all_files}
            # 更新時刻が最も新しいファイルを格納
            newest_file_path = max(file_updates, key=file_updates.get)
            return inference(request, newest_file_path)
    else:
        # 画像がPOSTで送信されていない場合
        form = ImageForm()
        return render(request, 'send_image_app/index.html', {'form':form})

def inference(request, newest_file_path):
    # データ変換用変数定義
    transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    # データ前処理
    image_data = transform(Image.open(newest_file_path)).unsqueeze(0)

    # インスタンス化
    net = model.animalmodel.Net().eval()
    # 学習済みモデルの重みの読み込み
    net.load_state_dict(torch.load('model/animal.pt'))

    # 推測
    with torch.no_grad():
        y = net(image_data)
        y_proba = y.softmax(dim=-1)
        y = torch.argmax(y, dim=1)

    # 動物情報の表示
    if y == 0:
        animal_name = "ゾウ"
        information = "ゾウの耳が大きい理由は、体温調節のためです。ゾウの耳には血管が多くあり、それを冷やすことで体の体温を冷やします。"
    elif y == 1:
        animal_name = "ライオン"
        information = "ライオンの狩りは、20回に1回ほどの成功率だと言われています。また、ライオンが狩りに出るのは24時間のうち3〜5時間ほどだけだと言われています。"
    elif y == 2:
        animal_name = "ホッキョクグマ"
        information = "ホッキョクグマの毛は無色透明。小さな穴がたくさん空いており、毛の中心部分は空洞になっています。"
    elif y == 3:
        animal_name = "シマウマ"
        information = "シマウマは「モー」と鳴きます。牛の鳴き声に非常に近い声を発します。"

    # DB内の最新のデータ
    modelfile = ModelFile.objects.order_by('id').reverse()[0]
    modelfile.proba = np.array(y_proba.max()*100)
    modelfile.result = y
    modelfile.animal_name = animal_name
    modelfile.information = information
    modelfile.save()

    return render(request, 'send_image_app/classify.html', {
        'newest_file_path':newest_file_path, 'y':np.array(y[0]), 
        'y_proba':np.array(y_proba.max()*100), 'information':information,
        'animal_name':animal_name
        })

class Login(LoginView):
    form_class = LoginForm
    template_name = 'send_image_app/login.html'

class Logout(LogoutView):
    template_name = 'send_image_app/base.html'

def signup(request):
    if request.method=='POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            new_user = authenticate(username=username, password=password)
            if new_user is not None:
                login(request, new_user)
                return redirect('classify')
    else:
        form = SignUpForm()
        return render(request, 'send_image_app/signup.html', {'form':form})