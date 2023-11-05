import os, re, sys, requests
from pprint import pprint
from bs4 import BeautifulSoup
import pandas as pd

class NotifyWebsiteUpdate():
    def __init__(self, url:str, logfile_basedir:str, logfile_path_dict:dict) -> None:
        self.url = url
        self.logfile_path_dict = logfile_path_dict
        self.logfile_basedir = logfile_basedir

    def get_now_page_df_dict(self) -> dict:
        """URLを入力すると、requests実行時点での「重要なお知らせ」と「最新情報」の二つを辞書に格納して吐き出す
        単体で動く

        Args (インスタンス変数): self.url (str): 情報を取得したいURL。ここでは山形大学のHP。

        Returns:
            now_page_df_dict (dict):
                要素一つ目："important"
                    データ取得時点での「重要ニュース」を格納したDataFrame。
                    columnsは["confirmed", "title", "URL", "date"]
                要素二つ目："news"
                    データ取得時点での「最新ニュース」を格納したDataFrame。
                    columnsは["confirmed", "title", "URL", "date", "category"]
        Returns (インスタンス変数): self.now_page_df_dict (dict): 上に同じ。
        """
        print("URLからデータを取得しています...")
        r = requests.get(self.url)
        soup = BeautifulSoup(r.content, "html.parser")

        important_content_soupls = soup.find(id="home-important").find_all("li")
        news_content_soupls = soup.find(id="box-tab-news").find(class_="news-list").find_all("li")
        contents_dict = {"important":important_content_soupls, "news":news_content_soupls}

        now_page_df_dict = {}
        for section_name, content_soupls in contents_dict.items():
            contentls = []
            if section_name == "important":
                contentls = [["confirmed", "title", "URL", "date"]]
                for content_soup in content_soupls:
                    url_temp = str(content_soup.find("a").get("href"))
                    if url_temp[0:4] == "/jp/":
                        url_temp = self.url + url_temp[4:]
                    contentls.append([
                        False,                                  # confirmed confirm_news()で使いたいラベル
                        content_soup.find(class_="title").text, # title
                        url_temp,                               # URL
                        content_soup.find(class_="date").text,  # date
                        ])
            elif section_name == "news":
                contentls = [["confirmed", "title", "URL", "date", "category"]]
                for content_soup in content_soupls:
                    url_temp = str(content_soup.find("a").get("href"))
                    if url_temp[0:4] == "/jp/":
                        url_temp = self.url + url_temp[4:]
                    contentls.append([
                        False,                                  # confirmed
                        content_soup.find(class_="title").text, # title
                        url_temp,                               # URL
                        content_soup.find(class_="date").text,  # date
                        content_soup.find(class_=re.compile("category")).text, # category 「重要なお知らせ」と違い、こちらにはcategoryもある
                        ])
            else:
                print("get_now_dfでセクション名エラー")
                quit()

            # pprint(contentls)
            df_content = pd.DataFrame(contentls[1:], columns=contentls[0])
            now_page_df_dict[section_name] = df_content

        self.now_page_df_dict = now_page_df_dict
        return now_page_df_dict
        # print(now_page_df_dict)

    def compare_now_and_last_page(self) -> dict:
        """最新の「重要なお知らせ」と「最新情報」の二つが格納された辞書と、logファイルのpathを受け取ると、現在と過去の「重要なお知らせ」と「最新情報」のデータを比較して最新部分をそれぞれ辞書に格納し吐き出す
        self.get_now_page_df_dict()の実行が必要

        Args (インスタンス変数):
            self.now_page_df_dict (dict): self.get_now_page_df_dict()で生成。
            self.logfile_path_dict (dict) : これまでのページ履歴を記録したcsvファイルのパス(str)を格納した辞書。

        Returns:
            differences_df_dict (dict): requests時点での各section(重要なお知らせ、最新情報)の新規追加部分を格納したDataFrameを格納した辞書。logファイルが存在しない場合、Noneを返す。
                要素一つ目："important"
                    「重要なお知らせ」の新規追加部分を格納したDataFrame。
                    columnsは["confirmed", "title", "URL", "date"]
                要素二つ目："news"
                    「最新情報」の新規追加部分を格納したDataFrame。
                    columnsは["confirmed", "title", "URL", "date", "category"]
        Returns (インスタンス変数): self.differences_df_dict (dict): 上に同じ。
        """
        now_page_df_dict = self.now_page_df_dict
        logfile_path_dict = self.logfile_path_dict

        if not os.path.exists(logfile_path_dict["important"])\
            or not os.path.exists(logfile_path_dict["news"]):
            self.differences_df_dict = None
            return self.differences_df_dict # differences
        else:
            keyls = list(logfile_path_dict.keys())
            lastls = []
            nowls = []
            for path in logfile_path_dict.values():
                df = pd.read_csv(path)
                lastls.append(df)
            for df in now_page_df_dict.values():
                nowls.append(df)

            # differences_df_dict = ["importantの追加要素(DataFrame)", "newsの追加要素(DataFrame)", "その他確認するsectionを増やす場合もここに追加要素(DataFrame)"]
            differences_df_dict = {}
            for i, temp_zip in enumerate(zip(nowls, lastls)):
                section_name = keyls[i]
                df_now, df_last = temp_zip[0], temp_zip[1]
                result = []
                for index, row_series in df_now.iterrows(): # index:int, row_series:pd.Series
                    if row_series["title"] == df_last["title"][0]:
                        break
                    result.append(row_series.values.tolist())
                df_result = pd.DataFrame(result, columns=df_now.columns.values)
                differences_df_dict[section_name] = df_result
            self.differences_df_dict = differences_df_dict
            # pprint(differences_df_dict)
            return differences_df_dict

    def make_log(self) -> None:
        """新規追加部分があった場合それをlogファイルに追加
        self.get_now_page_df_dict(), compare_now_and_last_page()の実行が必要

        Args (インスタンス変数):
            self.differences_df_dict (dict): self.compare_now_and_last_page()で生成。
            self.now_page_df_dict (dict): self.get_now_page_df_dict()で生成。
            self.logfile_path_dict (dict): self.__init__()で生成。self.compare_now_and_last_page()のArgsに記載。
            self.logfile_basedir (str): self.__init__()で生成。logを保存しておくフォルダのパス。os.makedirsで使う。
        """
        differences_df_dict = self.differences_df_dict
        now_page_df_dict = self.now_page_df_dict
        logfile_path_dict = self.logfile_path_dict

        os.makedirs(f"./{self.logfile_basedir}", exist_ok=True)

        if differences_df_dict == None:
            # 今のページをcsvファイルに記録
            for section_name, path in logfile_path_dict.items():
                now_page_df_dict[section_name].to_csv(path, index=False)
        else:
            for section_name, diff_df in differences_df_dict.items():
                log_csv_path = logfile_path_dict[section_name]
                log_df = pd.read_csv(log_csv_path)
                if not diff_df.empty:
                    new_log_df = pd.concat([diff_df, log_df], axis=0)
                    new_log_df.to_csv(log_csv_path, index=False)

    def notify_updates(self) -> None:
        """前回実行時点から新規に追加された記事の情報を一覧表示する
        self.get_now_page_df_dict(), compare_now_and_last_page()の実行が必要

        Args (インスタンス変数):
            self.differences_df_dict (dict): self.compare_now_and_last_page()で生成。
        """
        differences_df_dict = self.differences_df_dict

        if differences_df_dict == None:
            print("logファイルが存在しないため、新しく作成されました。")
        else:
            for section_name, diff_df in differences_df_dict.items():
                if section_name == "important":
                    print("〇重要なお知らせ\n")
                elif section_name == "news":
                    print("〇新着情報\n")
                else:
                    print("notify_updatesでセクション名エラー")
                    quit()

                if diff_df.empty:
                    print("最新の項目はありません\n")
                else:
                    print(f"最新の項目が{len(diff_df)}件あります\n")
                    if section_name == "important":
                        for index, row in diff_df.iterrows():
                            print(f"{row['date']} {row['title']}\n{row['URL']}\n")
                    elif section_name == "news":
                        for index, row in diff_df.iterrows():
                            print(f"[{row['category']}]{row['date']} {row['title']}\n{row['URL']}\n")

    def confirm_news(self) -> None:
        """まだ確認していない記事を一覧表示し、確認した記事の番号をcui形式で受け取りlogファイルに反映する
        単体で動く

        Args (インスタンス変数):
            self.logfile_path_dict (dict): self.__init__()で生成。self.compare_now_and_last_page()のArgsに記載
        """
        logfile_path_dict = self.logfile_path_dict
        logfile_pathls = list(logfile_path_dict.values())
        log_dfls = [pd.read_csv(path) for path in logfile_pathls]

        need_confirm_list = []
        for section_i, log_df in enumerate(log_dfls):
            for df_i, row_series in log_df.iterrows():
                if row_series["confirmed"] == False:
                    need_confirm_list.append([section_i, df_i, row_series])

        print("〇未確認の記事を一覧表示します\n")
        if need_confirm_list == []:
            print("全て確認済みです")
            # input("Enterキーを押してください>>")
            quit()
        for i, article_info in enumerate(need_confirm_list):
            if i != 0:
                if article_info[0] != need_confirm_list[0]: # セクションが変わったときに一行空白
                    print()
            if article_info[0] == 0:
                short_secname = "重要"
            elif article_info[0] == 1:
                short_secname = "新着"
            else:
                print("confirm_newsでセクション名エラー")
                quit()
            article_series = article_info[2]
            print(f"i:{i} [{short_secname}] {article_series['date']} {article_series['title']}")

        print("\n記事を確認済みにし次回以降表示させないためには、「i:(番号)」と表示されている番号(半角数字)を確認の上、\
                \n>>del (番号) (番号) (番号) ...(複数選択可)\
                \nのように入力しEnterキーを押してください。番号と番号の間には半角スペースが必要です。\
                \n全ての項目を確認済みにするには、\
                \n>>del all\
                \nと入力しEnterキーを押してください。\
                \n何も変更を加える点が無い場合は、何も入力せずにEnterキーを押してください。")

        loop_flag = False
        while loop_flag == False:
            raw_command = input("\n入力してください>>")
            if raw_command == "":
                quit()
            command = list(map(str, raw_command.split()))
            if command[0] == "del":
                if command[1] == "all":
                    del_list = list(range(len(need_confirm_list)))
                    loop_flag = True
                    print("\n全ての項目を確認済みにします。")
                else:
                    command_indexls = list(set(command[1:]))
                    command_indexls = list(map(int, command_indexls))
                    del_list = []
                    try:
                        for command_index in command_indexls:
                            if command_index in range(len(need_confirm_list)):
                                # print(command_index)
                                del_list.append(command_index)
                        loop_flag = True
                        del_list = sorted(del_list)
                        print("\n次の項目を確認済みにします。")
                    except ValueError:
                        print("del以降の入力値は半角数字のみ可能です") # Error
                for i in del_list:
                    section_i = need_confirm_list[i][0]
                    df_i = need_confirm_list[i][1]
                    log_dfls[section_i].iat[df_i, 0] = True
                    log_series = log_dfls[section_i].iloc[df_i]
                    print(f"i:{i} {log_series['date']} {log_series['title']}")
                for log_df, logfile_path in zip(log_dfls, logfile_pathls):
                    log_df.to_csv(logfile_path, index=False)
            else:
                print("入力が間違っています") # Error


    def run(self):
        self.get_now_page_df_dict()
        self.compare_now_and_last_page()
        self.make_log()
        self.notify_updates()
        self.confirm_news()

if __name__ == "__main__":
    url = "https://www.yamagata-u.ac.jp/jp/"
    logfile_basedir = "univ_hp_history"
    logfile_path_dict = {"important":"univ_hp_history/important_history.csv",
                        "news":"univ_hp_history/news_history.csv"}
    yamagata_univ = NotifyWebsiteUpdate(url, logfile_basedir, logfile_path_dict)
    yamagata_univ.run()