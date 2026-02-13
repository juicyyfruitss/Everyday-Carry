from postmarker.core import PostmarkClient

postmark = PostmarkClient(server_token = "d7499ce1-f3d0-4f2b-aa85-1ca332eb1e8c")

senderemail = "dlr060@email.latech.edu"
useremail = 'jjl034@email.latech.edu'

postmark.emails.send(
From = senderemail,
To = useremail,
Subject = "Item left behind",
HtmlBody="<strong>This is a test email sent via Postmark + Python!</strong>",
TextBody = "Hello World"
)

