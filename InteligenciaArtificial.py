from openai import OpenAI

class InteligenciaArtificial () : 
	OPENAI_API_KEY    = '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'
	MODEL_API         = 'gpt-3.5-turbo'
	PROFISSIONAL_CHAT = 'Você é um usuário do instagram, onde quando comenta, seus comentários são relevantes e amistosos aos donos do post que você comenta. Você não deve responder nada, se não o comentário'
	
	oApi = None;
		
	def __init__(self) :
		self.oApi = OpenAI(api_key= self.OPENAI_API_KEY)

	def getComentario(self, sLegenda) :
		oRetorno = self.oApi.chat.completions.create(
			model= self.MODEL_API,
			messages=[
				{
					"role": "system", 
					"content": self.PROFISSIONAL_CHAT
				},
				{"role": "user", "content": f"Crie um comentário simples, de no máximo duas ou três palabras, podendo conter ou ser apenas emoji, para o seguinte texto de legenda: {sLegenda}"}
			]
		)

		return oRetorno.choices[0].message.content