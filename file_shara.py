#!/usr/local/bin/python3.3
import os
import glob
from datetime import datetime

from flask import Flask, render_template, request, redirect
from flask import send_from_directory
from werkzeug.contrib.fixers import ProxyFix

import config


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

UPLOAD_FOLDER = config.UPLOAD_FOLDER
NOT_ALLOWED_EXTENSIONS = config.NOT_ALLOWED_EXTENSIONS


###############################################################################
# main
###############################################################################
@app.route('/', methods=['POST', 'GET'])
def down():
    os.chdir(UPLOAD_FOLDER)
    files = glob.glob("*.*")  # lint:ok
    LIST = []
    TEXT = ''

    if request.method == 'POST':
        ufile = request.files['file']
        if ufile and allowed_file(ufile.filename):
            filename = ufile.filename
            #filename = secure_filename(file.filename)
            filename = valid_name(filename)
            ufile.save(os.path.join(UPLOAD_FOLDER, filename))
            return redirect('/')

        if ufile and not allowed_file(ufile.filename):
            TEXT = 'Заборонені формати файлів: ' + str(NOT_ALLOWED_EXTENSIONS)

    LEN_DIR = len(UPLOAD_FOLDER) + 1
    for (vFOLDER, b, vFILES) in os.walk(UPLOAD_FOLDER):
        vFOLDER += ('/')
        for ufile in vFILES:
            LIST.append([vFOLDER[LEN_DIR:] + ufile,
                os.path.getsize(vFOLDER + '/' + ufile),
                datetime.fromtimestamp(os.path.getctime(
                    vFOLDER + '/' + ufile)).strftime('%Y-%m-%d %H:%M:%S'),
                datetime.fromtimestamp(os.path.getmtime(
                    vFOLDER + '/' + ufile)).strftime('%Y-%m-%d %H:%M:%S')])
    return render_template('download.html',
                           files=LIST,
                           text=TEXT,
                           diskSIZE=disk_usage(os.getcwd())
                           )


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/delete/<filename>', methods=['POST'])
def delete(filename):
    if os.path.exists(UPLOAD_FOLDER + '/' + filename):
        os.remove(UPLOAD_FOLDER + '/' + filename)
    return redirect('/')


###############################################################################
# FUNCTIONS
###############################################################################
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() not in NOT_ALLOWED_EXTENSIONS


def valid_name(filename):
    new_filename = filename.replace('/', '_')
    new_filename = new_filename.replace('\\', '_')
    return new_filename


def disk_usage(path):
    if hasattr(os, 'statvfs'):  # POSIX
        st = os.statvfs(path)
        #free = st.f_bavail * st.f_frsize
        total = st.f_blocks * st.f_frsize
        used = (st.f_blocks - st.f_bfree) * st.f_frsize
        #return str(str(used) + '/' + str(total) + 'Mb')
        return str(bytes2human(used) + '/' + bytes2human(total))

    elif os.name == 'nt':       # Windows
        import ctypes
        import sys
        _, total, free = ctypes.c_ulonglong(), ctypes.c_ulonglong(), \
                           ctypes.c_ulonglong()
        if sys.version_info >= (3,) or isinstance(path, unicode):
            fun = ctypes.windll.kernel32.GetDiskFreeSpaceExW
        else:
            fun = ctypes.windll.kernel32.GetDiskFreeSpaceExA
        ret = fun(path,
                  ctypes.byref(_),
                  ctypes.byref(total),
                  ctypes.byref(free)
                  )
        if ret == 0:
            raise ctypes.WinError()
        used = total.value - free.value
        return str(bytes2human(used) + '/' + bytes2human(total.value))
        #return str( str(round(used/1024/1024, 2) ) + '/' +
        #            str(round(total.value/1024/1024, 2)) + 'Mb')
    else:
        raise NotImplementedError("platform not supported")


def bytes2human(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.2f%s' % (value, s)
    return "%sB" % n


###############################################################################
# error
###############################################################################
@app.errorhandler(404)
def err_not_found(error):
    return 'WTF 404, %s, спробуй ще' % error


@app.errorhandler(500)
def err_server(error):
    return 'WTF 500, %s' % error

#---------------------------------------------
if __name__ == "__main__":
    app.run(host=config.HOST_IP,
            port=config.HOST_PORT,
            debug=config.DEBUG
            )