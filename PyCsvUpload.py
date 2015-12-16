import SimpleHTTPServer
import SocketServer
import cgi
import cgitb; cgitb.enable()
import sys, os
import csv
import time
import traceback


class CsvHelper:
  def CsvToHtml(self, filePath):
    strout = '<table>'
    rownum = 0;
    with open(filePath,'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
          strout = strout + '<tr>'
          if rownum == 0:
            for column in row:
              strout = strout + '<th>' + column + '</th>'
          else:
            for column in row:
              strout = strout + '<th>' + column + '</th>'
          strout += '</tr>'
          rownum = rownum + 1

    strout += '</table>'
    return strout


class CsvUploadWebHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

  UPLOAD_DIR='tmp'
  CSV_FORM_FIELD_NAME="csvupload"
  def do_OPTION():
    if self.path in ('*'):
      self.send_header('Access-Control-Allow-Origin', '*')
      self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
      self.send_header('Access-Control-Allow-Headers', 'X-Requested-With')
      
  def do_GET(self):
    print "CsvUploadWebHandler is on Work! Cheers!"
    return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
    
  def do_POST(self):
    basepath = self.translate_path(self.path)
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.end_headers()
    form = cgi.FieldStorage(
      fp=self.rfile,
      headers=self.headers,
      environ={'REQUEST_METHOD':'POST',
          'CONTENT_TYPE':self.headers['Content-Type']})
    print "Posted form values are: "+ str(form)
    try:
        fpath=self._save_uploaded_file(form,self.CSV_FORM_FIELD_NAME,self.UPLOAD_DIR)
        
        hlpr= CsvHelper()
        self.wfile.write('<html><head><title>Python server demo</title></head><body>')
        if fpath is not None:
          self.wfile.write(hlpr.CsvToHtml(fpath))
          print 'Your file is uploaded to %s',fpath
        else:
          self.wfile.write('<table><tr><th style="color:red;font-weight:bold">Nothing was uploaded. Check the console for the errors</th></tr></table>')
        self.wfile.write('</body></html>')
        self.wfile.close()
    except Exception:
        self.wfile.write(traceback.format_exc(sys.exc_info()))
        return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
  
  def _save_uploaded_file (self,form,form_field, upload_dir):
    basepath = self.translate_path(self.path)
    fileitem = form[form_field]
    if not fileitem.file: 
        print('no fileitem.file')
        return
    fnm= '%r-%s' % (int(time.time()), fileitem.filename)
    if not fnm.endswith('.csv'):
        print('This is not a csv file')
        return
    fpath=os.path.join(basepath,upload_dir, fnm)
    print('Your file was uploaded here: %s',fpath)
    fout = file(fpath, 'wb')
    while 1:
        chunk = fileitem.file.read(100000)
        if not chunk: break
        fout.write(chunk)
    fout.close()
    return fpath

    
Handler = CsvUploadWebHandler

httpd = SocketServer.TCPServer(("",8000),Handler)

httpd.serve_forever()
