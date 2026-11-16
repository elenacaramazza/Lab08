import copy
from operator import attrgetter

from database.distributore_DAO import DistributoreDAO
from model.distributore_DTO import Distributore
from model.prezzo_DTO import Prezzo

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None
        self.load_distributori()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        # TODO
        #In questa funzione devo estrarre la lista di prezzi(oggetti Prezzo(DTO)) di un distributore
        result=[]
        for distributore in self._distributori: #distributore è l'oggetto Distributore
            tutti_prezzi=distributore.get_prezzi()

            prezzi_mese=[]
            for prezzo in tutti_prezzi: #prezzo è l'oggetto Prezzo
                if prezzo.data.month ==mese:
                    prezzi_mese.append(prezzo.prezzo_litro) #Mi serve solo fare la media sul prezzo al litro

            #Calcolo la media aritmetica evitando la divisione per zero
            if len(prezzi_mese)>0:
                media= sum(prezzi_mese)/len(prezzi_mese)
                result.append((distributore.nome, media))

        return result

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)
        print(prezzi_settimana)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        # TODO
        if giorno >7: #Condizione di terminazione della ricorsione
            #(Salvo il risultato se è la prima settimana che completo oppure migliora il record)
            if self.__costo_ottimo == -1 or  costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo=costo_corrente
                self.__sequenza_ottima =copy.deepcopy(sequenza_parziale)
            return

        for id_distributore,lista_prezzi in prezzi_settimana.items():
            #Calcolo del costo parziale
            costo_carburante=lista_prezzi[giorno-1]*100
            if ultimo_distributore is not None and id_distributore!=ultimo_distributore:
                costo_spostamento=5
            else:
                costo_spostamento=0
            nuovo_costo=costo_carburante + costo_spostamento + costo_corrente

            #Filtro
            if self.__costo_ottimo == -1 or nuovo_costo < self.__costo_ottimo:
                sequenza_parziale.append(id_distributore)
                #Ricorro
                self.__ricorsione(sequenza_parziale,giorno+1,id_distributore,nuovo_costo,prezzi_settimana)
                #Backtracking
                sequenza_parziale.pop()

    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        # TODO
        result = {}
        for distributore in self._distributori:
            tutti_prezzi = distributore.get_prezzi()

            tutti_prezzi.sort(key=attrgetter('data'))

            prezzi_prima_settimana_mese= []
            for prezzo in tutti_prezzi:
                if prezzo.data.month==mese and 1<= prezzo.data.day <=7 :
                    prezzi_prima_settimana_mese.append(prezzo.prezzo_litro)

            result[distributore.id] = prezzi_prima_settimana_mese

        return result