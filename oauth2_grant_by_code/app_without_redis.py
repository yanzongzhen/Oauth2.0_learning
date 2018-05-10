import base64
import random
import time
from flask import Flask, request, redirect

app = Flask(__name__)

host = 'http://localhost:5000'
client_id = '123456'

redirect_uri = host + '/client/passport'
auth_redirect_uri = []
auth_code = {}
users = {}

def gen_token(uid):
    token = base64.b64encode(
        (':'.join([str(uid), str(random.random()), str(time.time() + 7200)])).encode())
    users[uid] = token
    return token


def gen_auth_code(uri):
    code = random.randint(0, 10000)
    auth_code[code] = uri
    return code


def verify_token(token):
    _token = base64.b64decode(token).decode()
    if users.get(_token.split(':')[0]) == token.encode():
        return 1
    if float(_token.split(':')[-1]) >= time.time():
        return 1
    else:
        return 0


@app.route('/',methods=['POST', 'GET'])
def index():
    html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="X-UA-Compatible" content="ie=edge">
            <title>Index</title>
            <style>
                a {
                    text-decoration: none;
                    font-size: 26px;
                    color:skyblue;
                }
            </style>
        </head>
        <body>
            <div class="contaniner" style="text-align:center">
                <div class="links" style="text-align:center">
                    <a href="/client">登陆认证</a>
                </div>
            </div>
        </body>
        </html>  
    """
    return html


@app.route('/client', methods=['POST', 'GET'])
def client():
    html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="X-UA-Compatible" content="ie=edge">
            <title>客户认证</title>
            <style>
                button {
                    font-size: 16px;
                    color: white;
                    background-color: grey;
                    border-radius: 3px;
                }
            </style>
        </head>
        <body>
            <h3>是否同意认证？</h3>
            <form action="/client/login">
                <button type="submit">确认</button>
                <button onclick="alert('取消')">取消</button>
            </form>
        </body>
        </html>
    """
    return html


@app.route('/client/login', methods=['POST', 'GET'])
def client_login():
    uri = host + \
        '/oauth?response_type=code&client_id=%s&redirect_uri=%s' % (client_id, redirect_uri)
    return redirect(uri)


@app.route('/oauth', methods=['POST', 'GET'])
def oauth():
    html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="X-UA-Compatible" content="ie=edge">
            <title>获取token</title>
            <style>
                div {
                    text-align: center
                }
                .tokens {
                    margin-top: 20px;
                }
                a {
                    text-decoration: none;
                    font-size: 26px;
                    color: skyblue;
                }
                span {
                    font-size: 20px;
                    color: grey;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="tokens" >
                    <span>您的Token:</span><span>%s</span>
                </div>
                <div class="links">
                    <a href="/data?token=%s">获取数据</a>
                </div>
            </div>
        </body>
        </html>    
    """
    if request.args.get('response_type') == 'code':
        uri = request.args.get('redirect_uri')
        redirect_url = uri + '?code=%s' % gen_auth_code(uri)
        return redirect(redirect_url)
    elif request.args.get('grant_type') == 'authorization_code':
        if auth_code.get(int(request.args.get('code'))
                         ) == request.args.get('redirect_uri'):
            token = gen_token(int(request.args.get('client_id')))
            return html % (token.decode(),token.decode())


@app.route('/client/passport', methods=['POST', 'GET'])
def client_passport():
    code = request.args.get('code')
    uri = host + '/oauth?grant_type=authorization_code&code=%s&redirect_uri=%s&client_id=%s' % (
        code, redirect_uri, client_id)
    return redirect(uri)


@app.route('/data', methods=['POST', 'GET'])
def test():
    token = request.args.get('token')
    if verify_token(token) == 1:
        html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="X-UA-Compatible" content="ie=edge">
                <title>数据资源管理</title>
                <style>
            
                </style>
            </head>
            <body>
                <table width="40%" align="center" border="solid">
                    <tr align="center">
                        <th>时间</th>
                        <th>数据</th>
                        <th>操作</th>
                    </tr>
                    <tr align="center">
                        <td>2018.05.09</td>
                        <td>啦啦啦啦</td>
                        <td>del</td>
                    </tr>
                    <tr align="center">
                        <td>2018.05.09</td>
                        <td>啦啦啦啦</td>
                        <td>del</td>
                    </tr>
                    <tr align="center">
                        <td>2018.05.09</td>
                        <td>啦啦啦啦</td>
                        <td>del</td>
                    </tr>
                </table>
            </body>
            </html>
        """
        return html

    else:
        return 'error'


if __name__ == '__main__':
    app.run(debug=True)
