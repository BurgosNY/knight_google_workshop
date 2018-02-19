import requests

# Apenas para deixar os dados escondidos
import os
from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())


airtable_api = os.environ.get('AIRTABLE_KEY')
airtable_fonte_api_url = 'https://api.airtable.com/v0/appCmmcOxNBLaO89F/Table%201'
facebook_token = os.environ.get('FACEBOOK_TOKEN')


def dados_airtable(url, api_key):
    url = f'{airtable_fonte_api_url}?api_key={airtable_api}'
    requisicao = requests.get(url)
    veiculos = requisicao.json()
    dados = []
    for v in veiculos['records']:
        dados.append(v['fields'])
    return dados


def get_feed(page_id, facebook_token):
    url = f'https://graph.facebook.com/v2.11/{page_id}/feed?access_token={facebook_token}'
    feed = requests.get(url).json()['data']
    lista_de_posts = []
    for entrada in feed:
        lista_de_posts.append(entrada['id'])
    return lista_de_posts


def get_post_stats(post_id, facebook_token):
    # Pegar os dados individuais
    fields = 'attachments,comments.summary(true),created_time,description,link,message,permalink_url,shares,type'
    url = f'https://graph.facebook.com/v2.11/{post_id}?fields={fields}&access_token={facebook_token}'
    r = requests.get(url).json()
    return r


def get_objects(page):
    posts = get_feed(page, facebook_token)
    dados = []
    for post in posts:
        info = get_post_stats(post, facebook_token)
        dados.append(info)
    for d in dados:
        if tem_intervencao(d) is not None:
            adicionar_linha(tem_intervencao(d))


# for loop com diferentes páginas (print)
def tem_intervencao(post):
    if 'message' in post:
        if 'intervenção' in post['message']:
            return {"mensagem": post['message'],
                    "link": post['permalink_url']}


def adicionar_linha(novos_dados):
    airtable_destino_api_url = 'https://api.airtable.com/v0/appS6w7do1Xy0skha/Table%201'
    headers = {"Authorization": f'Bearer {airtable_api}'}
    new_content = {"fields": novos_dados}
    s = requests.post(airtable_destino_api_url, json=new_content, headers=headers)
    print('dados_acrescentados')


if __name__ == '__main__':
    dados = dados_airtable(airtable_fonte_api_url, airtable_api)
    for dado in dados:
        get_objects(dado['facebook_id'])
