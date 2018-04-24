import feedparser
import html2text
import sys
import time
import os
from pathlib import Path
home = str(Path.home())

if len(sys.argv) < 2:
    folderlocation = home+"/DATA_DECRYPTED/RSS/rss.txt";
else:
    folderlocation = sys.argv[1];
if len(sys.argv) < 3: 
    maildir_inbox_location = home+"/MAILDIR/one/INBOX";
else:
    maildir_inbox_location = sys.argv[2];

with open(folderlocation) as f:
    lines=f.read().splitlines()
    out_lines=lines
    line_nr=0
    for line in lines:
        line_nr += 1
        url = line.split(" ")[1].rstrip();
        note =""
        try:
            note="["+line.split(" ",2)[2].rstrip()+"] "
        except:
            pass
        print("checking: "+url)
        uid_time=time.time()
        uid_nr=0
        if url != "":
            d=feedparser.parse(url);
            ###
            
            line_splitted=line.split(" ")
            if len(line_splitted) > 2:
                h_content = line_splitted[0]
            else:
                h_content = 0

            #
            """
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
            """

            try:
                temp_highest=float(h_content)
            except:
                temp_highest=0
                h_content=0
                pass

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
                with open(maildir_inbox_location+"/new/"+str(uid_time)+"_"+str(uid_nr), "w", encoding="utf-8") as m:

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
            
            #with open(history_file_location, "w") as h:
            #    h.write(str(temp_highest))
            #TODO test test test 

            out=line.split(" ",1)
            out[0] = str(temp_highest)
            out = ' '.join(out)
            out_lines[line_nr-1] = out
            os.system("echo '"+'\r\n'.join(out_lines)+"' > "+folderlocation)
        print(str(uid_nr)+" found!");
