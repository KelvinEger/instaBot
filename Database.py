import mysql.connector

class Database: 

    sHost    = None
    sUsuario = None
    sSenha   = None
    sBanco   = None
    oConexao = None
    sErro    = None

    def __init__(self, sHost, sUsuario, sSenha, sBanco):
        self.setHost(sHost)
        self.setUsuario(sUsuario)
        self.setSenha(sSenha)
        self.setBanco(sBanco)
        
    def conecta(self):
        try:
            oConexao = mysql.connector.connect(
                host=self.sHost,
                user=self.sUsuario,
                password=self.sSenha,
                database=self.sBanco
            )
            print("Conexão ao banco de dados MySQL bem-sucedida.")
            self.oConexao = oConexao

        except Exception as e:
            print(f"Erro ao conectar ao banco de dados MySQL: {e}")

    def consulta(self, sSql) :
        try:
            cursor = self.oConexao.cursor()
            cursor.execute(sSql)
            resultado = cursor.fetchone()
            cursor.close()
            return resultado

        except Exception as e:
            print(f"Erro ao realizar a consulta: {e}")
            return None

    def setHost(self, sHost):
        self.sHost = sHost

    def setUsuario(self, sUsuario):
        self.sUsuario = sUsuario

    def setSenha(self, sSenha):
        self.sSenha = sSenha

    def setBanco(self, sBanco):
        self.sBanco = sBanco

    def setErro(self, sErro):
        self.setErro = sErro

    def getErro(self):
        return self.sErro
    
    def getConexao(self):
        return self.oConexao