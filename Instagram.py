from instagrapi import Client
import random, datetime, os, json

'''
Documentação: https://subzeroid.github.io/instagrapi/
              https://github.com/subzeroid/instagrapi
'''
class Instagram:

    # Constantes
    ARQUIVO_LOGIN = "infologin.txt"
    HASHTAGS      = ["voudeturas", "teste"] # Isso aqui deve virar config
    ACOES_POST    = ['curtir', 'comentar']
    ACOES_CONTA   = ['seguir']


    # Atributos
    usuario            = None
    senha              = None
    loginSalvo         = False
    api                = None
    loginRealizado     = False
    postsInteracao     = []
    quantidadeInteacao = 5
    perfil             = None

    def __init__(self) -> None:
        print("##################################################")
        print(f"########### Robô KE iniciado às: {datetime.datetime.now()} ##############")
        print("##################################################")
        
        self.usuario = input("Qual usuário deseja utilizar?  ")
        self.setLoginSalvo()
        self.api = Client(delay_range = [2, 8]) # Delay de requisições para dar uma mascarada configurar


    def interagir(self):

        # Busca os posts
        for sHashTag in self.HASHTAGS :
            self.setPostsInteracao(sHashTag)
        
        for oInformacoesPost in self.postsInteracao:
            getattr(self.api, self.getMetodo())(oInformacoesPost)

    def curtir(self, oPost, sHashtag):
        oDadosMedia = oPost.dict()

        try:
            self.api.media_like(oDadosMedia['id'])
            print(f"Curtido post")
        except Exception as sErro:
            print("Não foi possível curtir o post. Erro: ", sErro)
        
    def comentar(self, oPost): # funcional
        aComentarios = ["Post legal", "Legal", "Bom", "Post bem interessante", "huuum"] # isso aqui virá do Google Bard
        sComentario  = random.choice(aComentarios)

        try:
            print(f"Adicionando um comentário em um post. Comentário: {sComentario}")
            
            oDadosMedia  = oPost.dict()
            self.api.media_comment(oDadosMedia['id'], sComentario)
        except Exception as sErro:
            print("Não foi possível comentar o post:", sErro)

    def getInformacoesUsuario(self, sUsername):
        try: 
            self.perfil = self.api.user_info_by_username(sUsername)
        except Exception as sErro:
            print(f"Erro ao buscar informações do perfil: {sErro}")
        

    def setPostsInteracao(self, sHashTag) :
        print(f"Procurando posts recentes sobre a hashtag: {sHashTag}")

        try:
            self.postsInteracao.extend(self.api.hashtag_medias_top(sHashTag, self.quantidadeInteacao))
            print(f"Encontrados {len(self.postsInteracao)} posts recentes sobre a hashtag: {sHashTag}")

        except Exception as sErro:
            print(f"Erro ao buscar as hashtags: {sErro}")

    def getMetodoAleatorio(self):
        sMetodo = random.choice(self.ACOES_POST)
        print('Ação a executar: ', sMetodo)

    def setLoginSalvo(self) :
        sArquivo = f"session_{self.usuario}.json"

        if(os.path.exists(sArquivo)) :
            arquivo_aberto = open(sArquivo, "r")
            aLinhas = arquivo_aberto.readlines()
            arquivo_aberto.close()
            self.loginSalvo = (len(aLinhas) > 0)
        else:
            print(f"Sem informações de login salvas!")

    '''
    Refatorar esse método!
    Separar as ações ~ Boas práticas
    '''
    def fazLogin(self):
        if(self.loginSalvo) :
            try:
                print("Existem informações de login salvas. Tentando login com sessão já logada!")
                self.api.load_settings(f"session_{self.usuario}.json") # Informações de uma sessão previamente existente
                self.loginRealizado = self.api.login(self.usuario, self.senha)
                self.api.get_timeline_feed() # atualiza o feed
                print('Login realizado com informações de sessão salvas!')

            except Exception as sErro:
                os.remove(f"session_{self.usuario}.json")
                print(f"Erro ao realizar login. Erro: {sErro}")
        
        else:
            print("Não tem informações de login salvas. Tentando login para crição de nova sessão!")
            
            try:
                print('Login com nova sessão')
                self.loginRealizado = self.api.login(self.usuario, self.senha)

                sConfigJson = self.api.get_settings()
                oArquivo = open(f"session_{self.usuario}.json", "w")
                json.dump(sConfigJson, oArquivo)
                oArquivo.close()

                print("Criando arquivo para armazenar a sessão!")

                with open(f"session_{self.usuario}.json", "w") as fp:
                    json.dump(sConfigJson, fp, indent=3)

                print('Salvas as informações de login')

            except Exception as sErro:
                print(f"Erro ao realizar login: {sErro}")
    

insta = Instagram()
insta.getInformacoesUsuario('kelvineger')