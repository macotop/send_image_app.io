import os
import hashlib
from django.db import models
from datetime import date, datetime

# ファイル名のハッシュ化
def _user_profile_avator_upload_to(instance, filename):
    current_time = datetime.now()
    # ファイル毎に固有のパーツを結合
    pre_hash_name = '%s%s%s' % (instance.id, filename, current_time)
    # ファイル形式を抽出
    extension = str(filename).split('.')[-1]
    # hashlib.md5 : 与えられた値に対して適当な値を返す関数、.hexdigest() : 長さ32の文字列
    hs_filename = '%s.%s' % (hashlib.md5(pre_hash_name.encode()).hexdigest(), extension)
    # hash_file_name(hs_filename)
    # 保存先
    saved_path = 'documents/'
    return '%s%s' % (saved_path, hs_filename)

# DBのテーブルを定義
class ModelFile(models.Model):
    # ImageField : 画像のアップロードのみに使用されるフィールド
    # upload_to : 保存先を指定する
    image = models.ImageField(
        # 以下だとファイル名をそのまま格納することになる
        # upload_to = 'documents/'
        upload_to = _user_profile_avator_upload_to
        )

    id = models.AutoField(primary_key=True)
    
    # 予測結果
    result = models.IntegerField(blank=True, null=True)
    # proba : 予測確率が入る
    proba = models.FloatField(default=0.0)

    # データ送信日時
    registered_date = models.DateField(default=date.today())

    # 動物の名前
    animal_name = models.CharField(max_length=10, blank=True, null=True)

    # 動物の情報
    information = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        if self.proba == 0.0:
            # strftime : int型をstr型にしてフォーマットを整える。
            # 登録日、idのみ表示
            return '%s, %d' % (self.registered_date.strftime('%Y-%m-%d'), self.id)
        else:
            # 登録日、id、予測結果、動物名、信頼度を表示
            return '%s, %d, %d, %s, %d' % (self.registered_date.strftime('%Y-%m-%d'), self.id, self.result, self.animal_name, self.proba)