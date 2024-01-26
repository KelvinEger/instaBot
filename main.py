import random, json, datetime, os, time
import InteligenciaArtificial
import LayoutInstaEngaged
from instagrapi.exceptions import BadPassword

from instagrapi import Client

'''
Documentação: https://subzeroid.github.io/instagrapi/
              https://github.com/subzeroid/instagrapi
'''

def conectar_mysql(host, usuario, senha, banco_dados):
    try:
        # Conecta ao banco de dados MySQL
        conexao = mysql.connector.connect(
            host=host,
            user=usuario,
            password=senha,
            database=banco_dados
        )
        print("Conexão ao banco de dados MySQL bem-sucedida.")
        return conexao
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados MySQL: {e}")
        return None
    
def realizar_consulta(conexao, query):
    try:
        # Cria um objeto cursor
        cursor = conexao.cursor()

        # Executa a consulta
        cursor.execute(query)

        # Recupera os resultados
        resultado = cursor.fetchone()

        # Fecha o cursor
        cursor.close()

        return resultado

    except Exception as e:
        print(f"Erro ao realizar a consulta: {e}")
        return None

def hasInfoLogin(sUsername):
    arquivo = f"data/session_{sUsername}.json"

    if(os.path.exists(arquivo)):
        arquivo_aberto = open(arquivo, "r")
        aLinhas = arquivo_aberto.readlines()
        arquivo_aberto.close()
        return (len(aLinhas) > 0)
    
    return False
        
def doLogin():
    with open(ARQUIVO_LOGIN, 'r') as arquivo:
        aLinhas = arquivo.readlines()

    username       = aLinhas[0].strip()
    password       = aLinhas[1].strip()
    bRealizouLogin = False

    oInstagram = Client(delay_range = [2, 8]) # Delay de requisições para dar uma mascarada

    if(hasInfoLogin(username)) :
        print("Existem informações de login salvas. Tentando login com sessão já logada!")

        oInstagram.load_settings(f"data/session_{username}.json") # Informações de uma sessão previamente existente

        try:
            bRealizouLogin = oInstagram.login(username, password)
            oInstagram.get_timeline_feed() # atualiza o feed

            print('Login realizado com informações de sessão salvas!')
        except Exception as xErro:
            os.remove(f"data/session_{username}.json")
            print(f"Erro ao realizar login. Erro: {xErro}")
        
    else:
        print("Não tem informações de login salvas. Tentando login para crição de nova sessão!")
        
        try:
            print('Login com nova sessão')
            bRealizouLogin = oInstagram.login(username, password)

            if(not bRealizouLogin):
                print('não conseguiu realizar login')
                exit()

            sConfigJson = oInstagram.get_settings()
            oArquivo = open(f"data/session_{username}.json", "w")
            json.dump(sConfigJson, oArquivo)
            oArquivo.close()

            print("Criando arquivo para armazenar a sessão!")

            with open(f"data/session_{username}.json", "w") as fp:
                json.dump(sConfigJson, fp, indent=3)

            print('Salvas as informações de login')

        except BadPassword as sErro:
            print(f"Informações de login incorretas")
        except Exception as sErro:
            print(f"Erro ao realizar login: {sErro}")

    return oInstagram, bRealizouLogin
    
def getPrincipaisPostsBasedOnHashtag(oInstagram, sHashtag, iQuantidade = 2):
    print(f"Procurando posts recentes sobre a hashtag: {sHashtag}")

    try:
        aPosts = oInstagram.hashtag_medias_top(sHashtag, iQuantidade)
        print(f"Encontrados {len(aPosts)} posts recentes sobre a hashtag: {sHashtag}")
        return aPosts
    except Exception as sErro:
        print(f"Erro ao buscar as hashtags: {sErro}")
    
    return None

def likePost(oInstagram, oPost):
    oDadosMedia = oPost.dict()

    try:
        oInstagram.media_like(oDadosMedia['id'])
        print(f"Curtido post")
    except Exception as sErro:
        print("Não foi possível curtir o post:", sErro)

def markPostAsRead(oInstagram, oPost, sHashtag):
    oDadosMedia = oPost.dict()      
    try:
        oInstagram.media_seen(oDadosMedia['id'])
        print(f"Marcado como lido post da hashtag {sHashtag}")
    except Exception as sErro:
        print("Não foi possível marcar o post como lido:", sErro)

def getFollowersFromUser(oInstagram, oPost, iLimite = 1):
    oDadosMedia = oPost.dict()
    sUsuario    = oDadosMedia['user']['pk']

    try:
        print("Buscando seguidores do usuário que postou a hashtag.")
        aSeguidores = oInstagram.user_followers(user_id=sUsuario, amount=iLimite)
        return aSeguidores
    except Exception as sErro:
        print("Errro ao buscar os seguidores do usuário que postou a hashtag.")
    
def commentOnPost(oInstagram, oPost):
    try:
        if not oPost.comments_disabled :
            sLegenda = oPost.caption_text

            oIa = InteligenciaArtificial.InteligenciaArtificial()
            sComentario = oIa.getComentario(sLegenda)

            print(f"Adicionando um comentário em um post. Comentário: {sComentario.content}")
        
            oDadosMedia  = oPost.dict()
            oInstagram.media_comment(oDadosMedia['id'], sComentario.content)
    except Exception as sErro:
        print("Não foi possível comentar o post:", sErro)

def likeAComentary(oInstagram, oPost):
    try:
        print("Curtindo um comentário em um post")
        
    except Exception as sErro:
        print(f"Erro ao curtir um comentário. Erro:{sErro}")

def seguirUsuario(oInstagram, iUsuario) :
    try:
        print(f'Seguindo usuário')
        oInstagram.user_follow(iUsuario)
    except Exception as sErro:
        print(f"Falha ao seguir usuário. Erro: ", sErro)

    return oInstagram

def aStoriesFromUser(oInstagram, iUsuario) :
    try:
        print(f"Buscando stories")
        return oInstagram.user_stories(iUsuario)
    except Exception as sErro :
        print(f"Erro os buscar stories. Erro: {sErro}")

def curtirStory(oInstagram, iId) :
    try:
        oInstagram.story_like(iId)
        print("Curtindo o story")
    except Exception as sErro:
        print(f"Erro ao curtir story: {sErro}")

def aguardarUmInstante(iMinimo = 5, iMaximo = 30):
    intervalo = random.uniform(iMinimo, iMaximo)
    print(f'Aguardando {intervalo} segundos')
    time.sleep(intervalo)

def salvar_ler_texto_arquivo(texto, caminho_arquivo):
    try:
        # Tenta abrir o arquivo para leitura
        with open(caminho_arquivo, 'r') as arquivo:
            # Lê o conteúdo atual do arquivo
            conteudo_atual = arquivo.read()

            # Verifica se o conteúdo é igual ao texto passado
            if conteudo_atual == texto:
                return True  # Texto igual, nada a fazer, retorna True
            else:
                # Texto diferente, retorna false 
                return False  # Texto diferente, retorna False
                with open(caminho_arquivo, 'w') as arquivo:
                    arquivo.write(texto)
            
    except FileNotFoundError:
        # Se o arquivo não existir, cria o arquivo e escreve o texto
        with open(caminho_arquivo, 'w') as arquivo:
            arquivo.write(texto)
        return True  # Arquivo criado, retorna True

def getDatabaseInfo() :
    try:
        # Abre o arquivo para leitura
        with open(f"data/database", 'r') as arquivo:
            # Carrega o conteúdo JSON do arquivo
            return json.load(arquivo)

    except Exception as e:
        # Trata erros durante a leitura do arquivo
        print(f"Erro ao ler o arquivo JSON: {e}")

ARQUIVO_LOGIN  = "infologin.txt"
AHASHTAGS      = ["coach", "beer", "empreendedorismo", "bora", "carro"] # Isso aqui deve virar config
APERFIISSEGUIR = ["treteifamosos", "marirobattini", "__anapaulla__a", "henriquerappiao", "joelf241"] # isso aqui vai virar config
ACOES          = ['curtirStory', 'seguir', 'comentar', 'curtirPost']

iLimiteSeguirHora     = 30
iLimiteCurtirHora     = 50
iLimiteComentarioHora = 50
iLimiteMensagemHora   = 20

oLayoutConfiguracao = LayoutInstaEngaged.InterfaceInstagram()


'''
daqui pra baixo foi pra banha
'''
exit()

oConexao = conectar_mysql(
    banco_dados = '', 
    host        = '', 
    usuario     = '', 
    senha       = ''
)

sClienteAcesso      = 'kelvin'
sClienteAcessoSenha = 'kelvin'

oRetorno = realizar_consulta(
    oConexao, f"""
        SELECT CASE inetipo_plano 
                  WHEN 1 THEN (inedata_contratacao + INTERVAL 1 MONTH > NOW())
                  WHEN 2 THEN (inedata_contratacao + INTERVAL 3 MONTH > NOW())
                  WHEN 3 THEN (inedata_contratacao + INTERVAL 6 MONTH > NOW())
                  WHEN 4 THEN (inedata_contratacao + INTERVAL 12 MONTH > NOW())
                  ELSE 0
               END AS plano_valido
          FROM InstaEngaged   
         WHERE inecliente_acesso = '{sClienteAcesso}'
           AND inecliente_acesso_senha = '{sClienteAcesso}'
    """
    )

print(oRetorno[0])

#raise SystemExit


oInstagram, bLoginRealizado = doLogin()

if(bLoginRealizado):
    print("Login realizado. Hora: ", datetime.datetime.now())

    
    for sPerfil in APERFIISSEGUIR :
        print("-----------------------------------------")
        print(f"Interagindo com seguidores do perfil: {sPerfil}")
        print("-----------------------------------------")
        
        try :
            
            oDadosPerfilBase     = oInstagram.user_info_by_username(sPerfil)

            print(oDadosPerfilBase)

            if (oDadosPerfilBase.is_private) :
                continue
            
            aSeguidoresInteragir = oInstagram.user_followers(oDadosPerfilBase.pk, False, 20)
            
            aSeguidoresInteragir = list(aSeguidoresInteragir.keys())
            random.shuffle(aSeguidoresInteragir)

            for iIdPerfil in aSeguidoresInteragir:
                oDadosPerfilInteragir = oInstagram.user_info(iIdPerfil)
                print(f"Perfil a interagir: @{oDadosPerfilInteragir.username}")

                aStories = aStoriesFromUser(oInstagram, iIdPerfil)
                
                for i, story in enumerate(aStories) :
                    curtirStory(oInstagram, story.id)
                    aguardarUmInstante(2, 5)
                
                oPostsPerfilInteragir = oInstagram.user_medias(user_id = iIdPerfil, amount = 2)

                for i, oPost in enumerate(oPostsPerfilInteragir) :
                    if(iLimiteCurtirHora > 0) :
                        likePost(oInstagram, oPost)
                        iLimiteCurtirHora -= 1
                    aguardarUmInstante()

                    iValor = random.choice([0, 1])
                    print(iValor)
                    if(iValor == 1 and iLimiteComentarioHora > 0) :
                        commentOnPost(oInstagram, oPost)
                        iLimiteComentarioHora -= 1

                    if(random.choice([1,1]) == 1) :
                        if(iLimiteSeguirHora > 0):
                            seguirUsuario(oInstagram, iIdPerfil)
                            iLimiteSeguirHora -= 1
                    
                    aguardarUmInstante()
        except Exception as sErro :
            print ('Erro ao buscar dados do perfil: ', sPerfil)
    
 
    for sHashTag in AHASHTAGS:
        print("-----------------------------------------")
        print(f"Interagindo com seguidores da hashtag: {sHashTag}")
        print("-----------------------------------------")

        aPostsHashTag = getPrincipaisPostsBasedOnHashtag(oInstagram, sHashTag, 20)

        sAcao = random.choice(ACOES)
        print(f"Ação a ser realizada: {sAcao}")

        for i, oPost in enumerate(aPostsHashTag): #para cada post da hashtag
            
            if sAcao == 'curtirStory' :
                aStories = aStoriesFromUser(oInstagram, oPost.user.pk)
                for i, story in enumerate(aStories) :
                    curtirStory(oInstagram, story.id)
                    aguardarUmInstante(2, 3)
                    
                    if iLimiteSeguirHora > 0 :
                        seguirUsuario(oInstagram, oPost.user)
                        iLimiteSeguirHora -= 1

            if sAcao == 'seguir' :
                oDicionarioSeguidores = getFollowersFromUser(oInstagram, oPost, 3) #seguidores da hashtag
            
                for i, iIndica in enumerate(oDicionarioSeguidores):
                    oUsuario = oDicionarioSeguidores[iIndica] #Usuários segudores do usuário do post
                    if iLimiteSeguirHora > 0 :
                        seguirUsuario(oInstagram, oUsuario)
                        iLimiteSeguirHora -= 1
                    aguardarUmInstante()

                    aStories = aStoriesFromUser(oInstagram, oUsuario)
                    for i, story in enumerate(aStories) :
                        curtirStory(oInstagram, story.id)
                        aguardarUmInstante()

            if sAcao == 'comentar' :
                if iLimiteComentarioHora > 0 :
                    commentOnPost(oInstagram, oPost)
                    iLimiteComentarioHora -= 1
                aguardarUmInstante()

            if sAcao == 'curtirPost' :
                if(iLimiteCurtirHora > 0) : 
                    likePost(oInstagram, oPost)
                    iLimiteCurtirHora -= 1
                aguardarUmInstante()

print("Execução encerrada!")