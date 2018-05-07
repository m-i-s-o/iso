function sendHttpPost(mail_list){
  Logger.log(mail_list);
  var formData = '{"mail_list": ' + mail_list + '}';
  var options ={
    'method' : 'post',
    'contentType': 'application/json',
    'payload' : formData,
    'muteHttpExceptions' : true
  };
  var url = 'https://i49ut1r3p8.execute-api.ap-northeast-1.amazonaws.com/dev/GAS'
  var response = UrlFetchApp.fetch(url, options);
  Logger.log(response.getContentText());
};

function gmail_fw(){
  var start = 0;
  var max = 3;
  var search = 'has:nouserlabels';
  var threads = GmailApp.search(search, start, max);
  var label = GmailApp.getUserLabelByName('FWed');
  var mail_list = [];

  try {
    for (var i in threads) {
      var thread = threads[i];
      var msgs = thread.getMessages();
        for(var m in msgs){
          var hash = {};
          var msg = msgs[m];
          hash.from = msg.getFrom();
          hash.subject = msg.getSubject();
          hash.body = msg.getPlainBody().replace(/\r/g, '').replace(/\n\n/g, '\n').replace(/\n\n/g, '\n');
          mail_list.push(hash);
        }
        Utilities.sleep(1000);
      }
      //Logger.log(mail_list);
      str_list = JSON.stringify(mail_list);
      sendHttpPost(str_list);
      label.addToThreads(threads);
    }
  catch (e) {
    Logger.log(e)
  }
}
  
