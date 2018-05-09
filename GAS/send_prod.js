function sendHttpPost(mail_list){
  Logger.log(mail_list);
  var input = {"mail_list": mail_list};
  //Logger.log(JSON.stringify(input));
  //var jsonData = {"input": "{" + input + "}", "name": "test", "stateMachineArn": "arn:aws:states:ap-northeast-1:148615456970:stateMachine:Zendesk_create_tickets"};
  //var payload = JSON.stringify(jsonData);
  var formData = '{"input": "{\\\"mail_list\\\":' + mail_list + '}", "name": "test", "stateMachineArn": "arn:aws:states:ap-northeast-1:148615456970:stateMachine:Zendesk_create_tickets"}';
  Logger.log(formData);

  var options ={
    'method' : 'post',
    'contentType': 'application/json',
    'payload' : formData,
    'muteHttpExceptions' : true
  };
  var url = 'ーーー'
  var response = UrlFetchApp.fetch(url, options);
  Logger.log(response.getContentText());
};

function gmail_fw(){
  var start = 0;
  var max = 5;
  var search = 'in:inbox';
  var threads = GmailApp.search(search, start, max);
  // var label = GmailApp.getUserLabelByName('FWed');
  var mail_list = [];
    for (var i in threads) {
      var thread = threads[i];
      var msgs = thread.getMessages();
        for(var m in msgs){
          var hash = {};
          var msg = msgs[m];
          //hash.from = msg.getFrom();
          hash.subject = msg.getSubject();
          hash.body = msg.getPlainBody().replace(/\r/g, '').replace(/\n\n/g, '\n').replace(/\n\n/g, '\n');
          mail_list.push(hash);
        }
        Utilities.sleep(1000);
      };
      Logger.log(mail_list);
      var str_list = JSON.stringify(mail_list).replace(/\'/g, "\"").replace(/\\\"/g, "\"").replace(/\"/g, "\\\"").replace(/\"\"/g, "\"");
      //Logger.log(str_list);
      sendHttpPost(str_list);
      // label.addToThreads(threads);
    var date = Utilities.formatDate(new Date(), "JST", "yyyy-MM-dd'T'HH:mm:ss'Z'");
    var text = date + '  Zendeskフィルタリング用メールアドレスからの転送起票に失敗しました。\nエラー内容:honyahonya'
    var jsonData = {"text": text};
    var payload = JSON.stringify(jsonData);
    var options = {
      'method' : 'post',
      'contentType': 'application/json',
      "payload": payload};
    //var response = UrlFetchApp.fetch('ーーー', options);
    //Logger.log(response.getContentText());
}
