import feedparser
import html2text
import sys
import time
from pathlib import Path
home = str(Path.home())

if len(sys.argv) < 2:
    folderlocation = home+"/DATA/RSS";
else:
    folderlocation = sys.argv[1];
if len(sys.argv) < 3: 
    maildir_inbox_location = home+"/MAILDIR/one/INBOX";
else:
    maildir_inbox_location = sys.argv[2];

with open(folderlocation+"/rss.txt") as f:
    for line in f:
        url = line.split(" ")[0].rstrip();
        note =""
        try:
            note="["+line.split(" ",1)[1].rstrip()+"] "
        except:
            pass
        print("checking: "+url)
        uid_time=time.time()
        uid_nr=0
        if url != "":
            d=feedparser.parse(url);
            history_file_location = folderlocation+"/last_checked/"+url.replace("https://","").replace("http://","").replace("/","_");
            h_content = "0";
            try:
                with open(history_file_location) as h:
                    for line in h:
                        try:
                            h_content=float(line)
                            break
                        except:
                            pass

                    #h_content = h.read();
            except:
                pass

            temp_highest=float(h_content)
            for entry in d.entries:
                try:
                    published_parsed=entry.published_parsed
                except:
                    published_parsed=entry.updated_parsed

                if time.mktime(published_parsed) >= temp_highest:
                    temp_highest = time.mktime(published_parsed)

                if time.mktime(published_parsed) <= float(h_content):
                    break

                #TODO mailbox in the new
                uid_nr += 1
                m = open(maildir_inbox_location+"/new/"+str(uid_time)+"_"+str(uid_nr), "w", encoding="utf-8")

                date=time.struct_time(published_parsed)
                # Thu Feb 23 19:58:21 2017
                days=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
                months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                datestring=days[date.tm_wday]+" "+months[date.tm_mon-1]+" "+str(date.tm_mday)+" "+str(date.tm_hour)+":"+str(date.tm_min)+":"+str(date.tm_sec)+" "+str(date.tm_year)
                m.write("From RSS "+datestring+"\n");
                m.write("Date: "+datestring+"\n");
                m.write("From: "+d.feed.title+"\n");
                m.write("Subject: "+note+entry.title+"\n");
                m.write("Content-Type: text/plain; charset=UTF-8"+"\n")
                m.write("\n")
                m.write(entry.title+"\n")
                try:
                    m.write("ORIGINAL ARTICLE LINK @ "+entry.link+"\n")
                except:
                    pass
                m.write("\n")
                try:
                    m.write(html2text.html2text(entry.summary))
                except:
                    pass
                m.close()
            
            h = open(history_file_location, "w")
            h.write(str(temp_highest))
            h.close()
        print(str(uid_nr)+" found!");
