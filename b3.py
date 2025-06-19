import pyodbc
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import schedule
import time

server = 'xxxxxx'  # Seu servidor SQL
database = 'master'  # Seu banco de dados
conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()


##################b3
def buscar_dados_b3di():
    url = "https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-taxas-referenciais-bmf-ptBR.asp"
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    td_elements = soup.find_all("td")
    dadosdi = []
    linha_atual = []

    for td in td_elements:
        # Limpar e converter o conteúdo do <td> para float
        valor_texto = td.text.strip().replace(".", "").replace(",", ".")
        try:
            valor_float = float(valor_texto) if valor_texto else None
        except ValueError:
            # Caso o valor não possa ser convertido para float, defina como None ou trate de outra maneira
            valor_float = None

        linha_atual.append(valor_float)

        if len(linha_atual) == 3:
            dadosdi.append(linha_atual)
            linha_atual = []

    # Imprimir os dados extraídos


    return dadosdi


def buscar_dados_b3didata():
    url = "https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-taxas-referenciais-bmf-ptBR.asp"

    # Faça uma solicitação GET para obter o HTML da página
    response = requests.get(url)

    # Verifique se a solicitação foi bem-sucedida
    if response.status_code == 200:
        # Analise o HTML com BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Encontre o elemento <input> com id="Data"
        input_element = soup.find("input", {"id": "Data"})

        # Verifique se o elemento foi encontrado
        if input_element:
            # Extraia o valor do atributo "value"
            datadi_str = input_element.get("value")
            print(datadi_str)

            # Converta a string da data para um objeto datetime
            datadi = datadi_str
            print(datadi)

            return datadi
        else:
            return "Elemento não encontrado."
    else:
        return "Falha ao acessar a página."


################inserirDI


def inserir_dados_di(dadosdi):

    # Deletar dados existentes da tabela DI
    delete_query = 'DELETE FROM DI'
    cursor.execute(delete_query)
    conn.commit()

    # Verificar se há linhas na tabela DI
    check_query = 'SELECT COUNT(*) FROM DI'
    cursor.execute(check_query)
    row_count = cursor.fetchone()[0]

    if row_count == 0:
        # Se não houver linhas, crie as linhas necessárias
        create_rows_query = 'INSERT INTO DI (DIdias, DI252, DI360) VALUES (?, ?, ?)'
        for linha in dadosdi:
            cursor.execute(create_rows_query, linha[0], None, None)
             # Imprimir a linha que foi criada

    # Atualizar dados na tabela DI
    update_query = '''UPDATE DI SET DI252 = ?, DI360 = ? WHERE DIdias = ?'''
    for linha in dadosdi:
        cursor.execute(update_query, linha[1], linha[2], linha[0])
          # Imprimir a linha que foi atualizada

    conn.commit()
    conn.close()


########inserirdatadi
def inserir_dados_didata(datadi):



    update_query = '''UPDATE DI SET DIdata = ?'''
    cursor.execute(update_query, datadi)  # Insira a data diretamente

    conn.commit()
    conn.close()









######################################TABELA SELIC
def buscar_dados_b3selic(datadi):


    # Formatar a data no formato desejado: DD/MM/YYYY
    data_formatada = datetime.strptime(datadi, '%d/%m/%Y')

    # Formatar a data no formato alternativo: YYYYMMDD
    data_formatada_alternativa = data_formatada.strftime('%Y%m%d')

    # Montar a URL com a data atual
    url = f"https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-taxas-referenciais-bmf-ptBR.asp?Data={datadi}&Data1={data_formatada_alternativa}&slcTaxa=SLP"
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    td_elements = soup.find_all("td")
    dadosselic = []
    linha_atual = []

    for td in td_elements:
        # Limpar e converter o conteúdo do <td> para float
        valor_texto = td.text.strip().replace(".", "").replace(",", ".")
        try:
            valor_float = float(valor_texto) if valor_texto else None
        except ValueError:
            # Caso o valor não possa ser convertido para float, defina como None ou trate de outra maneira
            valor_float = None

        linha_atual.append(valor_float)

        if len(linha_atual) == 2:
            dadosselic.append(linha_atual)
            linha_atual = []

    # Imprimir os dados extraídos
    return dadosselic





def buscar_dados_b3selicdata(datadi):
    # Formatar a data no formato desejado: DD/MM/YYYY
    data_formatada = datetime.strptime(datadi, '%d/%m/%Y')

    # Formatar a data no formato alternativo: YYYYMMDD
    data_formatada_alternativa = data_formatada.strftime('%Y%m%d')

    # Montar a URL com a data atual
    url = f"https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-taxas-referenciais-bmf-ptBR.asp?Data={datadi}&Data1={data_formatada_alternativa}&slcTaxa=SLP"
    print(url)

    # Faça uma solicitação GET para obter o HTML da página
    response = requests.get(url)

    # Verifique se a solicitação foi bem-sucedida
    if response.status_code == 200:
        # Analise o HTML com BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Encontre o elemento <input> com id="Data"
        input_element = soup.find("input", {"id": "Data"})

        # Verifique se o elemento foi encontrado
        if input_element:
            # Extraia o valor do atributo "value"
            dataselic_str = input_element.get("value")

            # Converta a string da data para um objeto datetime
            dataselic = dataselic_str
            print(dataselic)

            return dataselic
        else:
            return "Elemento não encontrado."
    else:
        return "Falha ao acessar a página."





#inserirdadosselic


def inserir_dados_selic(dadosselic):


        # Deletar dados existentes da tabela DI
        delete_query = 'DELETE FROM selic'
        cursor.execute(delete_query)
        conn.commit()

        # Verificar se há linhas na tabela selic
        check_query = 'SELECT COUNT(*) FROM selic'
        cursor.execute(check_query)
        row_count = cursor.fetchone()[0]

        if row_count == 0:
            # Se não houver linhas, crie as linhas necessárias
            create_rows_query = 'INSERT INTO selic(SELICDIAS, SELIC252) VALUES (?, ?)'
            for linha in dadosselic:
                cursor.execute(create_rows_query, linha[0], None)
                print(f"Linha criada: {linha}")  # Imprimir a linha que foi criada

        # Atualizar dados na tabela DI
        update_query = '''UPDATE selic SET SELIC252 = ? WHERE SELICDIAS = ?'''
        for linha in dadosselic:
            cursor.execute(update_query, linha[1],  linha[0])
            print(f"Linha atualizada: {linha}")  # Imprimir a linha que foi atualizada

        conn.commit()
        conn.close()

def inserir_dados_selicdata(dataselic):
    update_query = '''UPDATE selic SET SELICDATA = ?'''
    cursor.execute(update_query, dataselic)  # Insira a data diretamente

    conn.commit()
    conn.close()

def tarefa_agendada():
    buscar_dados_b3di()
    buscar_dados_b3didata()
    dadosdi = buscar_dados_b3di()

    inserir_dados_di(dadosdi)

    datadi = buscar_dados_b3didata()
    inserir_dados_didata(datadi)


        #################selic
    buscar_dados_b3selic(datadi)
    buscar_dados_b3selicdata(datadi)
    dadosselic = buscar_dados_b3selic(datadi)

    inserir_dados_selic(dadosselic)

    dataselic = buscar_dados_b3selicdata(datadi)
    inserir_dados_selicdata(dataselic)

schedule.every().day.at("07:00").do(tarefa_agendada)

while True:
    # Executar tarefas pendentes
    schedule.run_pending()
    # Aguardar um minuto antes de verificar novamente
    time.sleep(60)