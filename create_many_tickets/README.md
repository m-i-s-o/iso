## 本スクリプトについて
* Python 3.6.1
* タグなどで絞り込んだZendesk組織に所属するユーザー全員に対して起票する際に使用するスクリプトです。

## スクリプト中で使用している外部モジュール
・・・実行環境へのインストールをお忘れなく
* configparser
* logging
* requests

## 使いかた
config_sample.iniをコピーしたconfig.iniを作成し、自分の環境に合わせて編集してください。
* [general]
  * ENV
    * 実行対象とするZendeskアカウントのセクションの指定
  * LOG_MODE
    * loggingのログ出力モード
  * API_LIMIT
    * 一括でAPIリクエストを送信する上限数
  * ticket_comment
    * 起票するチケットのコメント内容
      * サンプル1行目の「{0} {1}様」という表記は「（会社名）（ユーザー名）様」という表記になります。
      　コメント内で改行する場合はサンプルのようにiniファイル内で改行し、段落を下げればOKです。
        会社名・ユーザー名をコメント内容に挿入しない場合は `create_many_tickets.py` のL172で".format"以下をコメントアウトしてください。

* [Zendesk_param]
  * QUERY_PARAMS
    * 組織を絞り込む条件
      ・・・複数指定できます。タグの他にも作成された期間の指定などできます。
    　     参考）https://developer.zendesk.com/rest_api/docs/core/search#query-basics
  * TICKET_PARAM
    * チケットのメタ情報の指定
      ・・・サンプルに記載している以外にも、チケットに付けるタグなども指定できます。
           参考）https://developer.zendesk.com/rest_api/docs/core/tickets#json-format
* [Zendesk(アカウント名など任意の表記に変更してOK)]
  * URL
    * 既に入力されているURLサンプルのサブドメイン部分を変更してください。
  * ADDRESS
    * ログインユーザーのメールアドレス
  * TOKEN
    * APIのトークン
* Confluenceのこちらの記事もご参考にしていただけるかと思います。
  * https://serverworks.atlassian.net/wiki/x/AYDrDQ
