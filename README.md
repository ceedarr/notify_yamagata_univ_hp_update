# yamagata_univ_hp_notify_1.1.py 

山形大学のホームページに新着記事があった際にそれを通知するPythonプログラムです。Windowsの場合、このプログラムを動かすbatプログラムをタスクスケジューラで定期的に起動することを想定しています。

## プログラムの流れ
1. 入力されたurlの実行時点でのhtmlデータをrequestsにより取得し必要な情報をDataFrameに格納
2. 実行時点での情報(DataFrame)と前回実行した時点での情報(csv読み取り→Dataframe)を比較し新規追加部分をDataFrameに格納
3. 新規追加部分をlogファイル(**_history.csv)に追記
4. 新規追加部分をプロンプトに表示(ユーザーが見る部分)
5. 新規に追加された記事を確認したかどうかの入力をユーザーから受け取り、確認した場合はTrue, 未確認の場合はFalseをlogファイルに記録

## 実行方法
コマンドプロンプトなどのコンソールで"python yamagata_univ_hp_notify_1.1.py"などとすると動きます。(Pythonインストール必須)

## インターフェース
・CUI\
・「プログラムの流れ」の5.のところで入力を要求します。入力方法はプログラム実行時に表示される説明文に記載しています。

## プログラムの構造
NotifyWebsiteUpdateクラスからなっています。メソッドは以下の通りです：\
__init__()\
get_now_page_df_dict()\
compare_now_and_last_page()\
make_log()\
notify_updates()\
confirm_news()\
run()

if __name__ == "__main__"内のyamagata_univ.run()で実行しています。

## activate_yamagata_univ_hp_notify.batを使用する方法
C:\Users\Public\env311\Scripts\python.exeで実行する前提のプログラムですが、venv環境が無い・使わない場合は"call C:\Users\Public\env311\Scripts\activate.bat"を削除してください。
