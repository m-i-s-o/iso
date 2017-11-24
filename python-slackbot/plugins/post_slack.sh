output=`python /Users/soypee/python-slackbot/plugins/get_kintai_events.py`
#echo $output
URL="https://slack.com/api/chat.postMessage?token=xoxb-203974687620-ISWIZ1xzHpda9q1q9LOHd51k&username=CS-kintai&icon_emoji=:denkyu2:&channel=ext-scratch&text="
curl_res=`curl $URL$output`


#if ${curl_res:6:4} = "true";then
#    curl "https://slack.com/api/chat.postMessage?token=xoxb-203974687620-ISWIZ1xzHpda9q1q9LOHd51k&username=kin-chan&icon_emoji=:denkyu2:&channel=times-iso&text=<@U4TB5L9NF>本日の勤怠報告:sumi:です。内容：$output"
#else
#    curl "https://slack.com/api/chat.postMessage?token=xoxb-203974687620-ISWIZ1xzHpda9q1q9LOHd51k&username=kin-chan&icon_emoji=:denkyu2:&channel=times-iso&text=<@U4TB5L9NF>なんらかの理由により勤怠報告ができませんでしたので、手動での投稿をお願いします。内容：$output"
#fi
