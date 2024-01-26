from math import sin
from operator import methodcaller
import Database, os, random, time, sys
import json
import InteligenciaArtificial
from instagrapi import Client
from instagrapi.exceptions import ProxyAddressIsBlocked, ClientError, LoginRequired

class Instagram:
    #Dados da conta
    sConta    = None
    sSenha    = None

    #Dados para interação
    aHashtags = []
    aPerfis   = []

    #Dados da tela 
    oTela = None

    #Atributos da classe
    sErro         = None
    oConexaoBanco = None
    bContaAtiva   = False
    oConta        = None
    iInteracoes   = 0
    
    def __init__(self, oTela):
        self.setLayout(oTela)
        self.setDadosConta()
        
    def setHashtags(self, aHashtags):
        self.aHashtags = aHashtags

    def setPerfis(self, aPerfis):
        self.aPerfis = aPerfis    

    def setLayout(self, oTela):
        self.oTela = oTela

    def lerConfiguracaoBanco(self) :
        return self.lerConteudoArquivo('database')

    def lerConteudoArquivo(self, sNomeArquivo) :
        try:
            with open(f"data/{sNomeArquivo}", 'r') as arquivo:
                return json.load(arquivo)

        except Exception as sErro:
            self.sErro = sErro
    
    def conectarBanco(self) :
        oInformacoesConectaBanco = self.lerConfiguracaoBanco()

        if (oInformacoesConectaBanco) :
            self.oConexaoBanco    = Database.Database(
                sBanco   = oInformacoesConectaBanco['banco'], 
                sHost    = oInformacoesConectaBanco['host'],
                sSenha   = oInformacoesConectaBanco['senha'],
                sUsuario = oInformacoesConectaBanco['usuario']
            )
            self.oConexaoBanco.conecta()
        else :
            self.log(f'Erro ao ler arquivo de configuração. Entre em contato com o suporta, informando o código de erro: A1. Error: {self.sErro}')
            exit()

    def buscaDadosContaUsuario(self) :
        oRetorno = self.oConexaoBanco.consulta(f"""
            SELECT CASE inetipo_plano 
                       WHEN 1 THEN (inedata_contratacao + INTERVAL 1 MONTH > NOW())
                       WHEN 2 THEN (inedata_contratacao + INTERVAL 3 MONTH > NOW())
                       WHEN 3 THEN (inedata_contratacao + INTERVAL 6 MONTH > NOW())
                       WHEN 4 THEN (inedata_contratacao + INTERVAL 12 MONTH > NOW())
                       ELSE 0
                   END AS plano_valido
              FROM InstaEngaged   
             WHERE inecliente_acesso = '{self.oTela.campo_id_acesso.get()}'
               AND inecliente_acesso_senha = '{self.oTela.campo_senha.get()}'
        """)

        if(oRetorno == None) :
            raise ContaNaoEncontrada('Conta InstaEngaged não encontrada! Favor verifique suas credenciais!')
        elif(oRetorno[0] != 1) :
            raise UsuarioInativo('Período InstaEngaged expirado! Favor entre em contato para renovar seu plano!')
        else :
            return True

    def setDadosContaInstaEngaged(self) :
        try:
            self.buscaDadosContaUsuario()
            self.bContaAtiva = True

        except ContaNaoEncontrada as e:
            self.oTela.adicionarTextoConsole(e)
            self.log(e)
        except UsuarioInativo as e:
            self.log(e)    
            self.oTela.adicionarTextoConsole(e)
        except Exception as sErro:
            self.log(f'Erro BD: {sErro}')
            self.oTela.adicionarTextoConsole(sErro)

    def setDadosConta(self):
        self.conectarBanco()
        self.setDadosContaInstaEngaged()

    def doLogin(self, sUsuario, sSenha):
        username       = sUsuario
        password       = sSenha
        bRealizouLogin = False

        oInstagram = Client(delay_range = [2, 8]) # Delay de requisições para dar uma mascarada
        '''oInstagram.set_device(
            {
                "app_version": "312.1.0.34.111.0.0.18.120",
                "android_version": 31,
                "android_release": "12.0",
                "dpi": "400dpi",
                "resolution": "1080x2400",
                "manufacturer": "Xiaomi",
                "device": "phoenix",
                "model": "Redmi Note 11T",
                "cpu": "mt6893",
                "version_code": "168361634"
            }
        )

        oInstagram.set_user_agent("Instagram 312.1.0.34.117.1.0.30.120 Android (31/12.0; 400dpi; 1080x2400; Xiaomi; Redmi Note 11T; phoenix; MediaTek Dimensity 8100; pt_BR; 168361634)")
        '''
        oInstagram.set_country('BR')
        oInstagram.set_country_code(55)
        oInstagram.set_locale('pt_BR')
        oInstagram.set_timezone_offset(-10800)

        if(self.hasInfoLogin(username)) :
            self.log("Existem informações de login salvas. Tentando login com sessão já logada!")

            oInstagram.load_settings(f"data/session_{username}.json") # Informações de uma sessão previamente existente

            try:
                bRealizouLogin = oInstagram.login(username, password)
                oInstagram.get_timeline_feed() # atualiza o feed
                self.oConta = oInstagram
            
            except ProxyAddressIsBlocked :
                os.remove(f"data/session_{username}.json")
                self.log('''
                    Usuário e senha incorreta, ou seu IP está inabilidade temporariamente. \n
                    Verifique suas credenciais do Instagram e tente novamente mais tarde.
                ''')
                exit()
                
            except ClientError as sErro:
                self.log('Não foi possível utilizar a sessão salva para login.')
                self.oTela.removerArquivo(f"session_{username}.json")
                self.doLogin(sUsuario, sSenha)

            except Exception as xErro:
                self.oTela.removerArquivo(f"session_{username}.json")
                self.log(f"Erro ao realizar login. Erro: {xErro}. Type of error: {type(xErro)}")
                exit()
            
        else:
            self.log("Realizando novo login para e criando nova sessão!")
            
            try:
                self.log('Login com nova sessão')
                bRealizouLogin = oInstagram.login(username, password)
                self.guardaInformacoesSessao(username, oInstagram.get_settings())
                self.oConta    = oInstagram

            except ProxyAddressIsBlocked :
                self.oTela.removerArquivo(f"session_{username}")
                self.log('''
                    Usuário e senha incorreta, ou seu IP está inabilidade temporariamente. \n
                    Verifique suas credenciais do Instagram e tente novamente mais tarde.
                ''')
            except Exception as sErro:
                self.log(type(sErro))

        return bRealizouLogin
    
    def hasInfoLogin(self, sUsuario):
        arquivo = f"data/session_{sUsuario}.json"

        if(os.path.exists(arquivo)):
            arquivo_aberto = open(arquivo, "r")
            aLinhas = arquivo_aberto.readlines()
            arquivo_aberto.close()
            return (len(aLinhas) > 0)
    
        return False

    def guardaInformacoesSessao(self, sUsuario, sTextoSalvar) :
        with open(f"data/session_{sUsuario}.json", "w") as fp:
            json.dump(sTextoSalvar, fp, indent=3)

            self.log('Salvas as informações de login')

    def interagir(self) :
        self.log('Iniciando interações. 🚀')

        if(self.aPerfis):
            self.interagirPerfis()

        if(self.aHashtags):
            self.interagirHashtags()

        self.log('Processo finalizado!')
 
    def interagirHashtags(self) :
        aHashtags = self.aHashtags.split(',')

        for sHashTag in aHashtags :
            sHashTag = sHashTag.strip()

            aPostsHashTag = self.buscaPostsHashtags(sHashTag)
            for i, oPost in enumerate(aPostsHashTag) :
                self.adicionarComentario(oPost)
                #self.enviarDirect(oPost)
                self.curtirPost(oPost)
   
    def interagirPerfis(self) :
        aPerfis = self.aPerfis.split(',')

        for sPerfil in aPerfis :
            sPerfil = sPerfil.strip()

            oDadosPerfilBase = self.getInformacoesUsuarioPorArroba(sPerfil)
            self.aguardarSegundos(5, 10)

            if(oDadosPerfilBase) :
                if (oDadosPerfilBase.is_private) :
                    self.log(f'Perfil privado {sPerfil}')
                    self.seguirUsuario(oDadosPerfilBase)
                    self.aguardarSegundos()
                    continue

                aSeguidoresInteragir = self.getSeguidoresDoPerfil(oDadosPerfilBase)
                self.aguardarSegundos()

                if(aSeguidoresInteragir) :
                    for iIdPerfil in aSeguidoresInteragir:
                        oDadosPerfilInteragir = self.getInformacoesUsuarioPorId(iIdPerfil)                
                        self.aguardarSegundos()

                        if(oDadosPerfilInteragir) :
                            self.seguirUsuario(oDadosPerfilInteragir)
                            self.aguardarSegundos()
                            aStories = self.getStoriesDoUsuario(iIdPerfil)
                            for oStory in aStories :
                                self.curtirStory(oStory)
                                self.aguardarSegundos(2, 5)

                            oPostsPerfilInteragir = self.getPostsUsuario(iIdPerfil)
                            for i, oPost in enumerate(oPostsPerfilInteragir) :
                                self.adicionarComentario(oPost)
                                #self.enviarDirect(oPost)
                                self.curtirPost(oPost)
                else:
                    self.log(f'Não encontrados seguidores do perfil: {sPerfil}')
            else :
                self.log(f'Não encontrados dados do perfil: {sPerfil}')

    def getInformacoesUsuarioPorId(self, iId):
        try:
            self.log((f'Buscando dados do perfil por ID: {iId}'))
            oPerfil = self.oConta.user_info(iId)
            return oPerfil
        
        except ClientError as sErro:
            self.log (f'Você deve logar novamente. Use seu instagram normalmente e apenas execute este automatizador dentro de no mínimo um dia')
            self.log (f'Encerrando a aplicação e limpando os dados da sessão de login')
            self.oTela.removerArquivo(f"session_{self.oTela.campo_usuario_instagram.get()}")
        except LoginRequired as sErro:
            self.log (f'Você deve logar novamente. Use seu instagram normalmente e apenas execute este automatizador dentro de no mínimo um dia')
            self.log (f'Encerrando a aplicação e limpando os dados da sessão de login')
            self.oTela.removerArquivo(f"session_{self.oTela.campo_usuario_instagram.get()}")
            exit()
        except Exception as sErro :
            self.log (f'Você deve logar novamente. Use seu instagram normalmente e apenas execute este automatizador dentro de no mínimo um dia')
            self.log (f'Encerrando a aplicação e limpando os dados da sessão de login')
            self.oTela.removerArquivo(f"session_{self.oTela.campo_usuario_instagram.get()}")

    def getInformacoesUsuarioPorArroba(self, sPerfil) :
        try:
            self.log((f'Buscando dados do perfil por @: {sPerfil}'))
            return self.oConta.user_info_by_username(sPerfil)
        except Exception as sErro :
            self.log(sErro)
            self.log(f'Erro ao buscar dados do perfil por @. Perfil inexistente ou bloqueado. Erro: {sErro}')

    def getSeguidoresDoPerfil(self, oPerfil) :
        try :
            self.log(f'Buscando seguidores do perfil: {oPerfil.username}')
            
            aSeguidoresInteragir = self.oConta.user_followers(oPerfil.pk, False, 30)
            aSeguidoresInteragir = list(aSeguidoresInteragir.keys())
            random.shuffle(aSeguidoresInteragir)
            return aSeguidoresInteragir
        except Exception as sErro: 
            self.log(f'Erro ao buscar os seguidores do perfil: {oPerfil.username}')

    def getPostsUsuario(self, iIdPerfil) :
        try: 
            return self.oConta.user_medias(user_id = iIdPerfil, amount = 3)
        except Exception as sErro:
            self.log(f'Erro ao buscar posts. Erro: {sErro}')
            
    def getStoriesDoUsuario(self, iUsuario) :
        try:
            self.log(f"Buscando stories")
            return self.oConta.user_stories(iUsuario)
        except Exception as sErro :
            self.log(f"Erro os buscar stories. Erro: {sErro}")

    def curtirStory(self, oStory) :
        if self.oTela.var_curtidas_storys.get() :
            try:
                self.oConta.story_like(oStory.id)
                self.log(f"Curtindo o story {oStory.id}")
                self.contaInteracao()
            except Exception as sErro:
                self.log(f"Erro ao curtir story id {oStory.id}: {sErro}")

    def aguardarSegundos(self, iMinimo = 30, iMaximo = 100):
        intervalo = random.uniform(iMinimo, iMaximo)
        self.log(f'Aguardando {intervalo} segundos')
        time.sleep(intervalo)

    def seguirUsuario(self, oUsuario) :
        if self.oTela.var_seguir.get() :
            try:
                if (self.oTela.iLimiteDiarioSeguir > 0) :
                    self.oConta.user_follow(oUsuario.pk)
                    self.oTela.iLimiteDiarioSeguir -= 1
                    self.log(f'Seguindo usuário {oUsuario.username}')
                    self.contaInteracao()

            except LoginRequired as sErro:
                self.log (f'Você deve logar novamente. Use seu instagram normalmente e apenas execute este automatizador dentro de no mínimo um dia')
                self.log (f'Encerrando a aplicação e limpando os dados da sessão de login')
                self.oTela.removerArquivo(f"session_{self.oTela.campo_usuario_instagram.get()}")
                exit()
            except Exception as sErro:
                self.log(type(sErro))
                self.log(f"Falha ao seguir o usuário {oUsuario.username}. Erro: {sErro}")

    def curtirPost(self, oPost) :
        if self.oTela.var_curtidas_posts.get() :
            try:
                if(self.oTela.iLimiteDiarioCurtir > 0) :
                    self.oConta.media_like(oPost.id)
                    self.oTela.iLimiteDiarioCurtir -= 1
                    self.aguardarSegundos()
                    self.log(f"Curtido post")
                    self.contaInteracao()
            except Exception as sErro:
                self.log(f"Não foi possível curtir o post: {sErro}")

    def buscaPostsHashtags(self, sHashtag) :
        self.log(f"Procurando posts recentes sobre a hashtag: {sHashtag}")

        try:
            aPosts = self.oConta.hashtag_medias_top(sHashtag, 20)
            self.log(f"Encontrados {len(aPosts)} posts recentes sobre a hashtag: {sHashtag}")
            return aPosts
        except Exception as sErro:
            message = self.oConta.last_json["feedback_message"]
            print(message)
            print(f"Erro ao buscar as hashtags: {sErro}")
        
        return None
    
    def log(self, sTexto) :
        print(sTexto)
        self.oTela.aMensagemConsole.append(sTexto)
        self.oTela.adicionarTextoConsole(sTexto)

    def adicionarComentario(self, oPost):
        if self.oTela.campo_comentarios.get() :
            try:
                if not oPost.comments_disabled :
                    sLegenda = oPost.caption_text

                    try :
                        oIa = InteligenciaArtificial.InteligenciaArtificial()
                        sComentario = oIa.getComentario(sLegenda)
                        self.contaInteracao()
                    except Exception:
                        self.log('Não foi possível obter um comentário via Inteligência artificial, utilizando um comentário genérico.')
                        sComentario = self.getComentarioAleatorio()

                    self.log(f"Adicionando um comentário em um post. Comentário: {sComentario}")
                    self.oConta.media_comment(oPost.id, sComentario)
                    #self.marcarPostComoLido(oPost)
            except Exception as sErro:
                self.log(f"Não foi possível comentar o post: {sErro}")

            self.aguardarSegundos()

    def getComentarioAleatorio(self) :
        aComentarios = [
            "Ótimo post, muito informativo!",
            "Adorei a abordagem do assunto.",
            "Que interessante, nunca tinha pensado nisso.",
            "Excelente conteúdo, parabéns!",
            "Estou ansioso por mais posts como esse.",
            "Esse é um ponto de vista interessante.",
            "Muito bem explicado, facilitou meu entendimento.",
            "Gostaria de ver mais informações sobre esse tema.",
            "Concordo totalmente, ótima análise.",
            "Inspirador! Obrigado por compartilhar.",
        ]

        return random.choice(aComentarios) 
    
    def getMensagem(self) : # alterar para vir da tela
        return "Oiii, tudo bem? Sou estou crescendo minha conta. Você pode me ajudar, me seguindo? Ah, eu já estou seguindo você :D"

    def marcarPostComoLido(self, oPost):  
        try:
            self.oConta.media_seen(oPost.id)
            self.log('Marcando o post como lido!')
            self.contaInteracao()
        except Exception as sErro:
            self.log(f"Não foi possível marcar o post como lido: {sErro}")

        self.aguardarSegundos()

    def enviarDirect(self, oPost) :
        try:
            sMensagem = self.getMensagem()
            oPerfil = self.oConta.user_id_from_username(oPost.user.username)
            print(oPerfil)        
            self.oConta.direct_send(text=sMensagem, user_ids=[oPerfil])
            self.log(f"Enviando direct para o usuário {oPost.pk}")
            self.contaInteracao()
        except Exception as sErro:
            self.log(f"Não foi possível enviar o direct. Erro: {sErro}. Tipo:{type(sErro)}")

        self.aguardarSegundos()
    
    def curtirComentario(self, oPost):
        try:
            print("Curtindo um comentário em um post")
            self.contaInteracao()
        except Exception as sErro:
            self.log(f"Erro ao curtir um comentário. Erro:{sErro}")

        self.aguardarSegundos()

    def contaInteracao(self):
        self.iInteracoes += 1

        if(self.iInteracoes > 15):
            self.log('Chegamos a 15 interações. Vamos aguardar de 9 a 15 minutos para não levar bloq.')
            self.aguardarSegundos(500, 900)
            self.iInteracoes = 0


class UsuarioInativo(Exception):
    pass

class ContaNaoEncontrada(Exception):
    pass