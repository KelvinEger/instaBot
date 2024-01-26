from turtle import onclick
import InstaEngaged
import json, os
import tkinter as tk
from tkinter import ttk

class InterfaceInstagram:

    oDadosSalvos       = None
    iLimiteDiarioSeguir = 30 # isso aqui deve virar config de tela
    iLimiteDiarioCurtir = 30 # isso aqui deve virar config de tela
    aMensagemConsole    = []

    def __init__(self):
        self.buscarDadosSalvos()
        self.iniciaTela()
        

    def buscarDadosSalvos(self):
        try:
            with open(f"data/credential_instaEngaged", 'r') as arquivo:
                conteudo_json = json.load(arquivo)
                print(conteudo_json)
                self.oDadosSalvos = conteudo_json

        except FileNotFoundError:
            print('Não existem dados salvos.')
            self.adicionarTextoConsole('Não existem dados salvos.')
        except Exception as sErro:
            print(f"Erro ao ler o arquivo JSON: {sErro}")

    def iniciaTela(self):
        print("Iniciando criação da tela")
        self.criaTela()
        self.configuraTela()
        self.setEstilo()
        self.montar()
        self.setValoresCampos()

        # Iniciar o loop principal
        self.executaTela()

    def executaTela(self) :
        self.janela.mainloop()
        self.janela.after(3000, self.printConsole)

    def criaTela(self) :
        self.janela = tk.Tk()
        self.janela.title("Configurações do Instagram")

    def configuraTela(self): 
        self.janela.state('zoomed')          # Maximizar a janela no Windows
        self.janela.configure(bg='#343a40')  # Cor de fundo (tema escuro)

        # Centralizar a janela na tela
        largura_janela = 800
        altura_janela = 600
        largura_tela = self.janela.winfo_screenwidth()
        altura_tela = self.janela.winfo_screenheight()
        x_pos = largura_tela // 2 - largura_janela // 2
        y_pos = altura_tela // 2 - altura_janela // 2

        self.janela.geometry(f"{largura_janela}x{altura_janela}+{x_pos}+{y_pos}")

    def setEstilo(self) :
        # Aplicar estilo para o tema escuro (bootstrap-like)
        estilo = ttk.Style()
        estilo.theme_use('clam')
        estilo.configure('TLabel', foreground='lightblue', background='#343a40')
        estilo.configure('TButton', foreground='lightblue', background='#007bff', padding=(5, 5))
        estilo.configure('Dark.TCheckbutton', background='#343a40', foreground='lightblue', focuscolor='#343a40')

        estilo.configure("Div.TFrame", background='#2c3338', borderwidth=2, relief="solid", bordercolor='#4e5964', padding=(10, 10), sticky='nsew')

    def onclickLimpar(self):
        self.adicionarTextoConsole('Removendo dados de conta')
        self.removerArquivo('credential_instaEngaged')
        
        self.campo_id_acesso.config(state="",style="") 
        self.campo_senha.config(state="",style="")
        self.campo_usuario_instagram.config(state="",style="")
        self.campo_senha_instagram.config(state="",style="")

    def onclickConfirmar(self):
        self.janela.after(200, self.doInteract)

    def doInteract(self) :
        if(self.dadosMinimosInformados()) :
            oInteracaoInsta = InstaEngaged.Instagram(self)
            
            if (oInteracaoInsta.bContaAtiva) :
                if(oInteracaoInsta.doLogin(self.campo_usuario_instagram.get(), self.campo_senha_instagram.get())):
                    self.adicionarTextoConsole (
                        f"Configurações:\n"
                        f"ID de Acesso InstaEngaged: {self.campo_id_acesso.get()}\n"
                        f"Usuário Instagram: {self.campo_usuario_instagram.get()}\n"
                        f"Perifs para buscar seguidores para interagir: {self.campo_perfis.get()}\n"
                        f"Hashtags para buscar seguidores: {self.campo_hashtags.get()}\n"
                        f"Comentários: {self.campo_comentarios.get()}\n"
                        f"Curtidas em Posts: {self.var_curtidas_posts.get()}\n"
                        f"Curtidas de Storys: {self.var_curtidas_storys.get()}\n"
                        f"Seguir: {self.var_seguir.get()}\n"
                        f"Comentar: {self.var_comentarios.get()}\n"
                        f"_____________________________________________________\n\n"
                    )
                    self.salvaDadosConta()

                    oInteracaoInsta.setPerfis(self.campo_perfis.get())
                    oInteracaoInsta.setHashtags(self.campo_hashtags.get())
                    
                    self.janela.after(1000, self.printConsole)
                    
                    oInteracaoInsta.interagir()

        else :
            self.adicionarTextoConsole('''
                Informações mínimas necessárias não informadas. \n
                Por favor, preencha as informações para que seja possível
            ''')

    def montar(self):
        '''
            Cria a tela
            @todo - Refatorar isso aqui
        '''
        r = 0  # Linha inicial

        # Contêiner com destaque nas bordas
        cont_div = ttk.Frame(self.janela, style="Div.TFrame")
        cont_div.grid(row=r, column=0, padx=20, pady=20, sticky='nsew')

        # Ajustar linhas e colunas do contêiner
        cont_div.rowconfigure(0, weight=0)
        cont_div.rowconfigure(1, weight=0)
        cont_div.rowconfigure(2, weight=0)
        cont_div.rowconfigure(3, weight=0)
        cont_div.rowconfigure(4, weight=0)
        cont_div.rowconfigure(5, weight=0)
        cont_div.rowconfigure(6, weight=0)
        cont_div.rowconfigure(7, weight=0)
        cont_div.columnconfigure(0, weight=1)
        cont_div.columnconfigure(1, weight=1)
        cont_div.columnconfigure(2, weight=1)
        cont_div.columnconfigure(3, weight=1)
        cont_div.columnconfigure(4, weight=1)

        # Fieldset para Informações da Conta
        fieldset_conta = ttk.Frame(cont_div, style="Div.TFrame")
        fieldset_conta.grid(row=r, column=0, columnspan=4, padx=10, pady=10, sticky='nsew')

        r += 1
        ttk.Label(fieldset_conta, text="ID de Acesso:", foreground='white', background='#343a40', anchor='e').grid(row=r, column=0, padx=10, pady=5, sticky='nse')
        self.campo_id_acesso = ttk.Entry(fieldset_conta)
        self.campo_id_acesso.grid(row=r, column=1, padx=10, pady=5, sticky='nsw')

        r += 1
        ttk.Label(fieldset_conta, text="Senha:", foreground='white', background='#343a40', anchor='e').grid(row=r, column=0, padx=10, pady=5, sticky='nse')
        self.campo_senha = ttk.Entry(fieldset_conta, show='*')
        self.campo_senha.grid(row=r, column=1, padx=10, pady=5, sticky='nsw')

        # Fieldset para Informações da Conta
        fieldset_informacoes_instagram = ttk.Frame(cont_div, style="Div.TFrame")
        fieldset_informacoes_instagram.grid(row=r, column=0, columnspan=4, padx=10, pady=10, sticky='nsew')

        r += 1
        ttk.Label(fieldset_informacoes_instagram, text="Usuário Instagram:", foreground='white', background='#343a40', anchor='e').grid(row=r, column=0, padx=10, pady=5, sticky='nse')
        self.campo_usuario_instagram = ttk.Entry(fieldset_informacoes_instagram)
        self.campo_usuario_instagram.grid(row=r, column=1, padx=10, pady=5, sticky='nsw')

        r += 1
        ttk.Label(fieldset_informacoes_instagram, text="Senha Instagram:", foreground='white', background='#343a40', anchor='e').grid(row=r, column=0, padx=10, pady=5, sticky='nse')
        self.campo_senha_instagram = ttk.Entry(fieldset_informacoes_instagram, show='*')
        self.campo_senha_instagram.grid(row=r, column=1, padx=10, pady=5, sticky='nsw')

        # Fieldset para Outros Campos
        fieldset_outros = ttk.Frame(cont_div, style="Div.TFrame")
        fieldset_outros.grid(row=r, column=0, columnspan=4, padx=10, pady=10, sticky='nsew')

        r += 1
        ttk.Label(fieldset_outros, text="Arrobas (separadas por vírgula):", foreground='white', background='#343a40', anchor='e').grid(row=r, column=0, padx=10, pady=5, sticky='nse')
        self.campo_perfis = ttk.Entry(fieldset_outros)
        self.campo_perfis.grid(row=r, column=1, padx=10, pady=5, sticky='nsw')

        r += 1
        ttk.Label(fieldset_outros, text="Hashtags (separadas por vírgula):", foreground='white', background='#343a40', anchor='e').grid(row=r, column=0, padx=10, pady=5, sticky='nse')
        self.campo_hashtags = ttk.Entry(fieldset_outros)
        self.campo_hashtags.grid(row=r, column=1, padx=10, pady=5, sticky='nsw')

        r += 1
        ttk.Label(fieldset_outros, text="Comentários:", foreground='white', background='#343a40', anchor='e').grid(row=r, column=0, padx=10, pady=5, sticky='nse')
        self.campo_comentarios = ttk.Entry(fieldset_outros)
        self.campo_comentarios.grid(row=r, column=1, padx=10, pady=5, sticky='nsw')

        r += 1
        ttk.Label(fieldset_outros, text="Ativar/Desativar:", foreground='white', background='#343a40', anchor='e').grid(row=r, column=0, padx=10, pady=5, sticky='nse')

        #r += 1
        self.var_curtidas_posts = tk.BooleanVar()
        self.var_curtidas_storys = tk.BooleanVar()
        self.var_seguir = tk.BooleanVar()
        self.var_comentarios = tk.BooleanVar()

        ttk.Checkbutton(fieldset_outros, text="Curtir Posts", variable=self.var_curtidas_posts, onvalue=True, offvalue=False, style="Dark.TCheckbutton").grid(  row=r, column=1, padx=10, pady=5, sticky='nsw')
        ttk.Checkbutton(fieldset_outros, text="Curtir Storys", variable=self.var_curtidas_storys, onvalue=True, offvalue=False, style="Dark.TCheckbutton").grid(row=r, column=2, padx=10, pady=5, sticky='nsw')
        ttk.Checkbutton(fieldset_outros, text="Seguir", variable=self.var_seguir, onvalue=True, offvalue=False, style="Dark.TCheckbutton").grid(                row=r, column=3, padx=10, pady=5, sticky='nsw')
        ttk.Checkbutton(fieldset_outros, text="Comentar", variable=self.var_comentarios, onvalue=True, offvalue=False, style="Dark.TCheckbutton").grid(         row=r, column=4, padx=10, pady=5, sticky='nsw')

        # Botão Confirmar
        r += 1
        botao_confirmar = ttk.Button(cont_div, text="Confirmar", command=self.onclickConfirmar)
        botao_confirmar.grid(row=r, column=1, columnspan=1, pady=30, sticky='nsew')

        botao_limpar = ttk.Button(cont_div, text="Limpar", command=self.onclickLimpar)
        botao_limpar.grid(row=r, column=2, columnspan=1, pady=30, sticky='nsew')

        # Caixa de texto para logs
        r += 1
        self.log_text = tk.Text(cont_div, height=30, state=tk.DISABLED, wrap="word", bg='#2c3338', fg='white', relief='solid', borderwidth=2, font=('Ubuntu', 10), highlightcolor='red')
        self.log_text.grid(row=r, column=0, columnspan=4, padx=10, pady=5, sticky='nsew')

        # Adicionar barra de rolagem
        scrollbar = ttk.Scrollbar(cont_div, command=self.log_text.yview)
        scrollbar.grid(row=r, column=5, sticky='ns')
        self.log_text.config(yscrollcommand=scrollbar.set)

        # Ajustar a geometria do contêiner
        self.janela.grid_rowconfigure(0, weight=1)
        self.janela.grid_columnconfigure(0, weight=1)       

    def adicionarTextoConsole(self, sTexto):
        self.aMensagemConsole.append(sTexto)
        # Adicionar logs na caixa de texto

    def printConsole(self):
        for i, sMensagem in enumerate(self.aMensagemConsole) :
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"{sMensagem} \n")
            self.log_text.yview(tk.END)  # Rolar para o final
            self.log_text.config(state=tk.DISABLED)
            self.aMensagemConsole.pop(i)

        self.janela.after(1000, self.executaTela)

    def salvaDadosConta(self):
        sConteudo = self.getStringJsonSalvar()

        self.oDadosSalvos = sConteudo
        self.escreverConteudoArquivo(sConteudo)
        
    def escreverConteudoArquivo(self, sConteudo) :
        try:
            with open(f"data/credential_instaEngaged", 'w') as arquivo:
                json.dump(sConteudo, arquivo, indent=3)
                print(f"Salvo dados de conta")
        except Exception as e:
            print(f"Erro ao criar o arquivo JSON: {e}")

    def removerArquivo(self, sNomeArquivo) : 
        try:
            os.remove(f'data/{sNomeArquivo}')
            print(f"O arquivo {sNomeArquivo} foi excluído com sucesso.")
        except FileNotFoundError:
            print(f"O arquivo {sNomeArquivo} não foi encontrado.")
        except Exception as e:
            print(f"Ocorreu um erro ao excluir o arquivo: {e}")

    def getStringJsonSalvar(self) :
        return {
            "idAcesso": self.campo_id_acesso.get(), 
            "senhaAcesso": self.campo_senha.get(), 
            "usuarioInstagram": self.campo_usuario_instagram.get(),
            "senhaInstagram": self.campo_senha_instagram.get(),
            "sArrobas": self.campo_perfis.get(),
            "sHashTags": self.campo_hashtags.get(),
            "sComentarios": self.campo_comentarios.get(),
            "bCurtidas": self.var_curtidas_posts.get(), 
            "bCurtidasStorys": self.var_curtidas_storys.get(),
            "bSeguir": self.var_seguir.get(),
            "bComentar": self.var_comentarios.get()
        }

    def setValoresCampos(self):
        if(self.oDadosSalvos) :
            if(self.oDadosSalvos['idAcesso'] ) :
                self.campo_id_acesso.insert(0, self.oDadosSalvos['idAcesso'])
                self.campo_id_acesso.config(state="disabled",style="CampoDesabilitado.TEntry")

            if(self.oDadosSalvos['senhaAcesso'] ) :
                self.campo_senha.insert(0, self.oDadosSalvos['senhaAcesso'])
                self.campo_senha.config(state="disabled",style="CampoDesabilitado.TEntry")

            if(self.oDadosSalvos['usuarioInstagram'] ) :
                self.campo_usuario_instagram.insert(0, self.oDadosSalvos['usuarioInstagram'])
                self.campo_usuario_instagram.config(state="disabled",style="CampoDesabilitado.TEntry")

            if(self.oDadosSalvos['senhaInstagram'] ) :
                self.campo_senha_instagram.insert(0, self.oDadosSalvos['senhaInstagram'])
                self.campo_senha_instagram.config(state="disabled",style="CampoDesabilitado.TEntry")

            self.campo_perfis.insert(0, self.oDadosSalvos['sArrobas'])
            self.campo_hashtags.insert(0, self.oDadosSalvos['sHashTags'])
            self.campo_comentarios.insert(0, self.oDadosSalvos['sComentarios'])
            self.var_curtidas_storys.set(self.oDadosSalvos['bCurtidasStorys'])
            self.var_curtidas_posts.set(self.oDadosSalvos['bCurtidas'])
            self.var_seguir.set(self.oDadosSalvos['bSeguir'])
            self.var_comentarios.set(self.oDadosSalvos['bComentar'])

    def dadosMinimosInformados(self):
        return (
            self.campo_usuario_instagram.get() 
            and self.campo_senha_instagram.get()
            and self.campo_id_acesso.get()
            and self.campo_senha.get()
            and (self.campo_hashtags or self.campo_perfis)
        )    

a = InterfaceInstagram()
a.adicionarTextoConsole('FINALIZADO')
print('____________Fim________________')