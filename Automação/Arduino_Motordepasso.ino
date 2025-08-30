//definimos aqui os pinos conectados na ESP32 e a quantidade de passos do motor que completa uma revolução completa.
const int dirPin = 22;
const int stepPin = 23;
const int passosPorVolta = 200;
const int chaveFim = 25; //aqui definimos os dois mini switches 1 no fim e outro no inicio.
const int chaveInicio = 26;
#define dir_Avanco  HIGH //HIGH ----->
#define dir_Retorno  LOW //LOW <-----
/*=========---------==========-----------=========---------------==============---------------===========------------------------===============
Você poderá ignorar este bloco sem perda alguma de significado ou conteúdo.
Este bloco é apenas para adicionarmos em nosso projeto duas chaves fim de cursos (mini switch) que irá inverter o movimento e parar o nosso trilho.

//utlizaremos o método enum, pois tornará o código mais legível, seguro e de melhor manutenção.
//É interessante utilizar este método pois não há possibilidade das duas chaves estarem ativadas simultaneamentes.
//Então, criaremos "estados" em que nosso trilho estará e o arduino irá verificar milhares de vezes em qual estado ele está.*/


enum Estado{
	avancando, retornando
};
Estado estadoAtual= avancando;
//Aqui é como se estivessemos utilizando um array, mas sem números.  Então temos um tipo (Estado) criando uma nova variavel, que receberá um valor.

//void é como um trabalhador, que executa uma tarefa mas não retorna nenhuma variável, apenas executa uma determinada tarefa.
// setup() é a configuração de nosso microcontrolador, irá ser acionado apenas uma vez e para. Não fica em Loop.
void setup (){
	Serial.begin(115200); //executa a comunição serial com velocidade boudrate de 115200.
	pinMode(21, OUTPUT);
	pinMode(stepPin, OUTPUT);
	pinMode(dirPin, OUTPUT); // aqui definimos step e dir como saídas e o digitalWrite irá escrever se terá valor LOW (0V) ou HIGH (5V).
	pinMode(chaveFim, INPUT_PULLUP);
	pinMode(chaveInicio, INPUT_PULLUP); //Aqui estamos definindo nosso mini-switch para entrada (input) e funcionará como um interruptor (PULLUP) que irá trocar para HIGH ou LOW quando ativado.
	digitalWrite(dirPin, HIGH); //define a direção horário de antihorário.      HIGH ------>      LOW <-------
	digitalWrite(21, LOW);//Define o driver como habilitado.

	Serial.println("Estado atual: Avancando");

}
void loop(){

	switch(estadoAtual){
		case avancando:
		if (digitalRead(chaveFim)==LOW){
			delay(50);
			Serial.println("Voltando");
			digitalWrite(dirPin, dir_Retorno);

			estadoAtual=retornando;
		}
		else{
		//como é executado milhares de vezes, pode ter nenhum comando a ser feito, executando o if e causando erros, por isso fazemos: 
		if (Serial.available() > 0 ){
			char comando = Serial.read();   //Irá ler comando após comando (SE TIVER) e executará o codido do If
			//agora definiremos um comando, para quando lido, comece o movimento de fato.
			if (comando=='P') {
			//Irá girar o motor, que está com um driver de motor inteligente, que irá dar a ordem e fornecer corrente automaticamente de forma certa as bobinas do motor para dar um passo.
				for (int i=0; i< passosPorVolta;i++){
					bool movimentoCompleto = true;//atribuimos o valor true para uma variavel do passo do motor.
					//Vamos integrar ao sistema a chave fim de curso, importante para que não danifique o equipamento. (Portanto, a chave vai ser checada a cada passo).
					if (digitalRead(chaveFim) == LOW) { //se chavefim estive pressionada:
					delay(50);
					Serial.println("Voltando");//escreve no monitor serial, que aparecerá no prompt.
					digitalWrite(dirPin, dir_Retorno);//fará o motor inverter sua direção de rotação.
					estadoAtual = retornando;
					movimentoCompleto = false;
					 break;
					}
					//motor dá um passo: 
					digitalWrite(stepPin, HIGH);
					delayMicroseconds(20000); //quanto tempo manterá o sinal de tensão em ALTA, (reconhece inicio do pulso) (quanto menor, mais rápido será o passo, mais veloz o motor e menor o torque)
					digitalWrite(stepPin, LOW); 
					delayMicroseconds(20000); //analago ao delay anterior.
				}
				Serial.println("OK");//irá escrever "OK" no monitor serial, que será lido pelo python e dará inicio a detecção pelo PM100D

			}
			}

		}
	break;    //sai da estrutura switch após ler o valor desejado.

	case retornando:
	if (digitalRead(chaveInicio)==LOW){
		delay(50);
		Serial.println("INICIO");
		estadoAtual=avancando;
		digitalWrite(dirPin,dir_Avanco);
	}
	else{
		//Se não tiver ainda acionado o switch de inicio, continue dando passos:
		digitalWrite(stepPin,HIGH);
		delayMicroseconds(4000);
		digitalWrite(stepPin,LOW);
		delayMicroseconds (4000);
	}
	break;
}
}