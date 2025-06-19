import pyodbc
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import request
from flask_mail import Mail, Message
from flask import redirect, url_for,   render_template,  flash
import secrets
import re
import bcrypt
import requests
from bs4 import BeautifulSoup
import datetime

import logging

app = Flask(__name__)
app.secret_key = 'XXXX'




# Configurações de conexão
server = 'XXXX'
database = 'XXX'
username = 'XXX'
password = 'XXX'
driver = 'XXXX'

# Conexão com o banco de dados
connection_string = f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}'
conn = pyodbc.connect(connection_string)




login_manager = LoginManager()
login_manager.init_app(app)

# Configuração do servidor SMTP para envio de e-mails
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Substitua pelo seu servidor SMTP
app.config['MAIL_PORT'] = 465  # Porta do servidor SMTP (normalmente 465 para SSL/TLS)
app.config['MAIL_USERNAME'] = 'XXXX'  # Seu e-mail
app.config['MAIL_PASSWORD'] = 'XXX'  # Sua senha do e-mail
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id



@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def load_user(user_id):
    return User.query.get(int(user_id))


def authenticate_user(email, senha):


    try:

        cursor = conn.cursor()

        # Recupera o hash da senha e o ID do usuário do banco de dados
        cursor.execute("SELECT id, senha FROM Usuarios WHERE email=?", (email,))
        row = cursor.fetchone()

        conn.close()

        if row:
            user_id, hashed_password = row
            senha_bytes = senha.encode('utf-8')

            # Converte o hash da senha para bytes, se necessário
            hashed_password_bytes = hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password

            if bcrypt.checkpw(senha_bytes, hashed_password_bytes):
                return user_id  # Retorna o ID do usuário se a senha corresponder
            else:
                return None
        else:
            return None

    except pyodbc.Error as e:
        print(f"Erro na conexão: {e}")
        return None




@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:  # Verifica se o usuário já está autenticado
        return render_template('login2.html')

    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        user_id = authenticate_user(email, senha)

        if user_id:
            user = User(user_id)
            login_user(user)
            return redirect(url_for('index'))

        return render_template('login.html', error='E-mail e senha não conferem!')

    return render_template('login.html', error='')






@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))




@app.errorhandler(401)
def unauthorized(error):
    return redirect(url_for('login'))

########## recuperação de senha

def verificar_email(email):


    try:

        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM Usuarios WHERE email=?", (email,))
        row = cursor.fetchone()

        conn.close()

        return row[0] > 0  # Retorna True se o e-mail estiver presente no banco de dados

    except pyodbc.Error as e:
        print(f"E-mail não encontrado {e}")
        return False









# Recuperar senha




@app.route('/email_nao_encontrado')
def email_nao_encontrado():
    # Aqui você pode adicionar qualquer lógica necessária antes de renderizar o template
    return render_template('senha_redefinida.html')  # Substitua pelo nome do seu template HTML



@app.route('/confirmacao_envio_email')
def confirmacao_envio_email():
    # Aqui você pode adicionar qualquer lógica necessária antes de renderizar o template
    return render_template('confirmacao_envio_email.html')  # Substitua pelo nome do seu template HTML


def atualizar_token(email, token):

    try:

        cursor = conn.cursor()

        # Atualiza o token na tabela de usuários associada ao e-mail
        cursor.execute("UPDATE Usuarios SET token = ? WHERE email = ?", (token, email))
        conn.commit()
        conn.close()

    except pyodbc.Error as e:
        print(f"Erro ao atualizar o token: {e}")

@app.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form['email']
        if verificar_email(email):
            token = secrets.token_urlsafe(16)
            atualizar_token(email, token)  # Chamada para atualizar o token na base de dados
            msg = Message('Ferramenta Pessoa Juridica',
                          sender='XXXXXX', recipients=[email])
            msg.body = f"Para redefinir sua senha, acesse o link: {url_for('redefinir_senha', token=token, _external=True)}"
            mail.send(msg)
            return redirect(url_for('confirmacao_envio_email'))
        else:
            return render_template('email_nao_encontrado.html')
    return render_template('recuperar_senha.html')


def get_email_by_token( token):


    try:

        cursor = conn.cursor()

        # Consulta ao banco de dados para obter o e-mail associado ao token
        cursor.execute("SELECT email FROM Usuarios WHERE token = ?", (token,))
        row = cursor.fetchone()

        conn.close()

        return row[0] if row else None # Retorna o e-mail associado ao token ou None se não encontrado

    except pyodbc.Error as e:
        print(f"Erro ao obter o email associado ao token: {e}")
        return None

# Verificação do formato da nova senha
def validar_senha(nova_senha):
    if len(nova_senha) < 8:
        return False
    if re.search(r'\d', nova_senha) is None:
        return False
    if re.search(r'[a-zA-Z]', nova_senha) is None:
        return False
    return True

def update_password_in_database(email, nova_senha):


    try:

        cursor = conn.cursor()

        # Gera um hash da nova senha
        hashed_password = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt())

        # Atualiza a senha no banco de dados para o e-mail fornecido
        cursor.execute("UPDATE Usuarios SET senha=? WHERE email=?", (hashed_password, email))
        conn.commit()
        conn.close()

    except pyodbc.Error as e:
        print(f"Erro ao atualizar a senha: {e}")


# Redefinir senha
@app.route('/senha_redefinida')
def senha_redefinida():
    # Aqui você pode adicionar qualquer lógica necessária antes de renderizar o template
    return render_template('senha_redefinida.html')  # Substitua pelo nome do seu template HTML

@app.route('/expirado')
def expirado():
    # Aqui você pode adicionar qualquer lógica necessária antes de renderizar o template
    return render_template('expirado.html')  # Substitua pelo nome do seu template HTML



@app.route('/redefinir_senha/<token>', methods=['GET', 'POST'])


def redefinir_senha(token=None):

    if request.method == 'POST':
        nova_senha = request.form['nova_senha']

        email = get_email_by_token(token)  # Obtém o email associado ao token
        if email is not  None:

            if validar_senha(nova_senha):  # Condição do if corrigida

                if email:
                    update_password_in_database(email, nova_senha)  # Atualiza a senha
                    return render_template('senha_redefinida.html')
                else:
                    message = 'Não foi possível redefinir a senha'
                    return render_template('redefinir_senha.html', token=token, error=message)

            else:
                message = 'A senha deve ter no mínimo 8 caracteres, uma letra e um número.'
                return render_template('redefinir_senha.html', token=token, error=message)

        else:

            return render_template('expirado.html')

    return render_template('redefinir_senha.html', token=token)

################################# fim de redefinição de senha ############

#############index##########




@app.route('/index')
@login_required
def index():
    ###### Menu Padrao
    try:
        if current_user.is_authenticated:
            user_id = current_user.id  # Obtém o ID do usuário logado
            print(user_id)
            cursor = conn.cursor()
             # Inclua o campo 'PA' na sua consulta
            cursor.execute("SELECT perfil, cooperativa, PA FROM Usuarios WHERE id=?", (user_id,))
            user_data = cursor.fetchone()



            if user_data:
                perfil = user_data[0]
                cooperativa = user_data[1]
                pa = user_data[2]  # Recupera o valor de 'PA'

                if perfil == 'master' and cooperativa in (
                    'XXXXXX'
                ):
                    perfil = "master"
                else:
                    perfil = "padrao"

                print(f"User ID: {user_id}")
                print(f"Perfil: {perfil}")
                print(f"Cooperativa: {cooperativa}")
                print(f"PA: {pa}")
                conn.close()

                return render_template('index.html', perfil=perfil, cooperativa=cooperativa, pa=pa)

    except pyodbc.Error as e:
        print(f"Ocorreu um erro na conexão: {e}")
        return render_template('erro.html', error_message=f"Ocorreu um erro na conexão: {e}")
            #####FIM DE MENU PADRAO










if __name__ == '__main__':
    app.run(debug=True)



    #servidor heroku
