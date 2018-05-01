function sendHttpPost(subject, message){
   var payload =
   {
     "tickets" : [{
         "subject": subject,
         "comment": message
   };

   var params =
   {
     "method" : "post",
     "payload" : payload
   };
   UrlFetchApp.fetch(<<API GatewayのURL>>, params);
}

function myFunction(){
  var ticket_sbj = メールのタイトル
  var ticket_msg = メールの本文;
  response = sendHttpPost(ticket_sbj, ticket_msg);
  Logger.log(response.getContentText());
}

function gmail_fw(){
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var sent = 0;
  var start = 0;
  var max = 5;
  var search = 'is:unread';
  var fw_addr = sheet.getRange("C3").getValue();
  var threads = GmailApp.search(search, start, max);
  var label = GmailApp.getUserLabelByName("FWed");

  for (var i in threads) {
    var thread = threads[i];
    var msgs = thread.getMessages();

    for(var m in msgs){
      var msg = msgs[m];
      var from = msg.getFrom();
      var subject = msg.getSubject();
      var body = msg.getPlainBody().replace(/\r/g, "").replace(/\n\n/g, "\n").replace(/\n\n/g, "\n");
      var body = "From:" + from + "\n" + "Subj:" + subject + "\n\n" + body;

      GmailApp.sendEmail(fw_addr, subject, body);
      sent += 1;
      if (sent % 10 == 0) {
        Utilities.sleep(3000);
      }
    }
    Utilities.sleep(1000);
  }
  label.addToThreads(threads);
}
