from dotenv import load_dotenv
# 環境変数のロード
load_dotenv()
from googleapis.gmail.readonly import get_emails_by_keyword
from googleapis.gmail.send import send_email


print(get_emails_by_keyword("中島聡 古田"))
send_email("newtons.boiled.clock@gmail.com","test1","test2")