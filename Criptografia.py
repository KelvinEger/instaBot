from cryptography.fernet import Fernet

class CriptografiaSimetrica:
    def __init__(self, chave=None):
        if chave:
            # Verifica se a chave fornecida é válida
            self.validar_chave(chave)
            self.chave = chave
        else:
            # Gera uma nova chave se nenhuma for fornecida
            self.chave = Fernet.generate_key()

        # Cria uma instância do objeto Fernet usando a chave
        self.fernet = Fernet(self.chave)

    def validar_chave(self, chave):
        try:
            # Tenta decodificar a chave para garantir que seja válida
            Fernet(chave)
        except ValueError as e:
            raise ValueError("Chave inválida") from e

    def criptografar(self, mensagem):
        # Converte a mensagem para bytes
        mensagem_bytes = mensagem.encode('utf-8')

        # Usa o objeto Fernet para criptografar a mensagem
        mensagem_criptografada = self.fernet.encrypt(mensagem_bytes)

        return mensagem_criptografada

    def descriptografar(self, mensagem_criptografada):
        # Usa o objeto Fernet para descriptografar a mensagem
        mensagem_bytes = self.fernet.decrypt(mensagem_criptografada)

        # Converte os bytes de volta para a mensagem original
        mensagem_original = mensagem_bytes.decode('utf-8')

        return mensagem_original

# Exemplo de uso:
chave_secreta = Fernet.generate_key().decode('utf-8')  # Converte a chave gerada para string
criptografia = CriptografiaSimetrica(chave_secreta)

mensagem_original = "n1EHD@F8V4!R"

# Criptografa a mensagem
mensagem_criptografada = criptografia.criptografar(mensagem_original)
print("Mensagem Criptografada:", mensagem_criptografada)

# Descriptografa a mensagem
mensagem_descriptografada = criptografia.descriptografar(mensagem_criptografada)
print("Mensagem Descriptografada:", mensagem_descriptografada)
