# -*- coding: utf-8
from ..data import BoletoData, custom_property


### CAUTION - NÃO TESTADO ###

class BoletoHsbc(object):
    '''
        Implementação do boleto do HSBC
        Para o HSBC é necessário passar se o boleto irá ser com registro ou não
        atráves do parametro 'com_registro'
        Utiliza carteira CNR - para boletos sem registro
        Utiliza carteira CSB - para boletos com registro

        eg::
            boleto = BoletoHsbc(com_registro=True)
            boleto2 = BoletoHsbc(com_registro=False)

        :param com_registro: define a emissão com registro.Default: False
    '''

    def __new__(cls, com_registro=False):
        if com_registro:
            boleto = BoletoHsbcComRegistro()
        else:
            boleto = BoletoHsbcSemRegistro()

        boleto.codigo_banco = "399"
        boleto.logo_image = "logo_bancohsbc.jpg"

        return boleto


class BoletoHsbcSemRegistro(BoletoData):
    '''
        Implementação da geração de boletos do HSBC para
        carteira CNR (sem registro)
    '''
    numero_documento = custom_property('numero_documento', 13)

    def __init__(self):
        super(BoletoHsbcSemRegistro, self).__init__()
        self.carteira = 'CNR'

    @property
    def dv_nosso_numero(self):
        # Primeiro DV
        dv = str(self.modulo11(self.nosso_numero))
        # Preencher tipo do identificador
        # 4 = boleto com vencimento
        # 5 = boleto sem vencimento
        if self.data_vencimento:
            dv += "4"
        else:
            dv += "5"
        # Segundo DV
        nosso_numero_parcial = self.nosso_numero + dv

        soma_atributos = int(nosso_numero_parcial) + int(self.conta_cedente)
        soma_atributos += int(self.data_vencimento.strftime('%d%m%y'))
        soma_atributos = str(soma_atributos)
        dv += str(self.modulo11(str(soma_atributos)))
        return dv

    def format_nosso_numero(self):

        return "%s%s" % (self.nosso_numero, self.dv_nosso_numero)

    @property
    def data_vencimento_juliano(self):
        data_vencimento = str(self.data_vencimento.timetuple().tm_yday)
        data_vencimento += str(self.data_vencimento.year)[-1:]
        return data_vencimento.zfill(4)

    @property
    def campo_livre(self):
        content = "%7s%13s%4s2" % (self.conta_cedente,
                                   self.nosso_numero,
                                   self.data_vencimento_juliano)
        return content


class BoletoHsbcComRegistro(BoletoData):
    '''
        Implementação da geração de boletos do HSBC para
        carteira CSB (com registro)
    '''
    # Nosso numero (sem dv) sao 10 digitos
    nosso_numero = custom_property('nosso_numero', 10)

    def __init__(self):
        super(BoletoHsbcComRegistro, self).__init__()
        self.carteira = 'CSB'
        self.especie_documento = 'PD'

    @property
    def dv_nosso_numero(self):
        resto = self.modulo11(self.nosso_numero, 7, 1)
        if resto == 0 or resto == 1:
            return 0
        else:
            return 11 - resto

    @property
    def campo_livre(self):
        content = "%10s%1s%4s%7s001" % (self.nosso_numero,
                                        self.dv_nosso_numero,
                                        self.agencia_cedente.split('-')[0],
                                        self.conta_cedente.split('-')[0])
        return content
