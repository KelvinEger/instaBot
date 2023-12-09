import random, json, datetime, os
from instagrapi import Client

'''
Documentação: https://github.com/subzeroid/instagrapi
'''

def hasInfoLogin(sUsername):
    arquivo = f"session_{sUsername}.json"

    if(os.path.exists(arquivo)):
        arquivo_aberto = open(arquivo, "r")
        aLinhas = arquivo_aberto.readlines()
        arquivo_aberto.close()
        return (len(aLinhas) > 0)
    
    return False
        

def doLogin():
    with open('infologin.txt', 'r') as arquivo:
        aLinhas = arquivo.readlines()

    username       = aLinhas[0]
    password       = aLinhas[1]
    bRealizouLogin = False

    oInstagram = Client(delay_range = [2, 8]) # Delay de requisições para dar uma mascarada

    if(hasInfoLogin(username)) :
        print("Existem informações de login salvas. Tentando login com sessão já logada!")

        oInstagram.load_settings(f"session_{username}.json") # Informações de uma sessão previamente existente

        try:
            bRealizouLogin = oInstagram.login(username, password)
        except Exception as xErro:
            print(f"Erro ao realizar login. Erro: {xErro}")
        
        if(bRealizouLogin):
            print('Login realizado com informações de sessão salvas!')
        
            try:
                oInstagram.get_timeline_feed()
            except Exception as xErro:
                print("Erro ao realizar login : ", xErro)
    
        else :
            print("Não foi possível reaalizar login com os dados salvos!")

    else:
        print("Não tem informações de login salvas. Tentando login para crição de nova sessão!")
        
        bRealizouLogin = oInstagram.login(username, password)

        if(bRealizouLogin):
            print('novo login realizado. Nova sessão')
            
            sConfigJson = oInstagram.get_settings()

            oArquivo = open(f"session_{username}.json", "w")
            json.dump(sConfigJson, oArquivo)
            oArquivo.close()

            print("Criando arquivo para armazenar a sessão!")

            with open(f"session_{username}.json", "w") as fp:
                #json.dump(sConfigJson, oArquivo)
                json.dump(sConfigJson, fp, indent=3)

            print('Salvas as informações de login')

    return oInstagram, bRealizouLogin
    
def getPrincipaisPostsBasedOnHashtag(oInstagram, sHashtag, iQuantidade = 2):
    print(f"Procurando posts recentes sobre a hashtag: {sHashtag}")
    printCurrentTime()
    aPosts = oInstagram.hashtag_medias_top("voudeturas", iQuantidade)
    print(f"Encontrados {len(aPosts)} posts recentes sobre a hashtag: {sHashtag}")

    return aPosts

def likePost(oInstagram, oPost, sHashtag):
    oDadosMedia = oPost.dict()

    try:
        oInstagram.media_like(oDadosMedia['id'])
        print(f"Curtido post numero {i+1} da hashtag {sHashtag}")
    except Exception as sErro:
        print("Não foi possível curtir o post:", sErro)

def markPostAsRead(oInstagram, oPost, sHashtag):
    oDadosMedia = oPost.dict()      
    try:
        oInstagram.media_seen(oDadosMedia['id'])
        print(f"Marcado como lido o post numero {i+1} da hashtag {sHashtag}")
    except Exception as sErro:
        print("Não foi possível marcar o post como lido:", sErro)

def getFollowersFromHashtagPost(oInstagram, oPost, iLimite = 1): # ta demorando bastante
    print("Buscando seguidores do usuário que postou a hashtag.")
    oDadosMedia = oPost.dict()
    oUsuario    = oDadosMedia['user']['pk']
    try:
        aSeguidores = oInstagram.user_followers(oUsuario, iLimite)
        a = aSeguidores
    except Exception as sErro:
        print("Errro ao buscar os seguidores do usuário que postou a hashtag.")
    
def commentOnPost(oInstagram, oPost): # funcional
    print("Adicionando um comentário em um post")

    aComentarios = ["Post legal", "Legal", "Bom", "Post bem interessante", "huuum"] # isso aqui virá do Google Bard
    sComentario  = random.choice(aComentarios)
    oDadosMedia  = oPost.dict()

    try:
        oInstagram.media_comment(oDadosMedia['id'], sComentario)
    except Exception as sErro:
        print("Não foi possível comentar o post:", sErro)

def likeAComentary():
    print("Curtindo um comentário em um post")

def printCurrentTime():
    print("Hora atual: ", datetime.datetime.now())




oInstagram, bLoginRealizado   = doLogin()
aHashtags    = ["life"] # Isso aqui deve virar config

if(bLoginRealizado):
    for sHashTag in aHashtags:
        printCurrentTime()
        aPostsHashTag = getPrincipaisPostsBasedOnHashtag(oInstagram, sHashTag, 2)
        printCurrentTime()
        for i, oPost in enumerate(aPostsHashTag):
            #likePost(oInstagram, oPost, sHashTag)
            #markPostAsRead(oInstagram, oPost, sHashTag)
            #getFollowersFromHashtagPost(oInstagram, oPost, 1) # ficou lento. Não da erro e não retorna

            #commentOnPost(oInstagram, oPost) # funcional
            printCurrentTime()