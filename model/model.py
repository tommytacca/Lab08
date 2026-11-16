from database.distributore_DAO import DistributoreDAO
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

    def get_prezzo_medio(self, mese: int):

        risultato = []

        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()
            prezzi_mese = []

            for prezzo in prezzi:
                if prezzo.data.month == mese:
                    prezzi_mese.append(prezzo.prezzo_litro)

            media_prezzi = sum(prezzi_mese) / len(prezzi_mese)

            risultato.append((distributore.nome, media_prezzi))

        return risultato
    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """

        if giorno == 8:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale.copy()
            return
        for id_distributore in prezzi_settimana:

            prezzo = prezzi_settimana[id_distributore][giorno - 1]
            costo = prezzo * 100

            if ultimo_distributore is not None and id_distributore != ultimo_distributore:
                costo += 5

            sequenza_parziale.append(id_distributore)

            # Ricorsione
            self.__ricorsione(
                sequenza_parziale,
                giorno + 1,
                id_distributore,
                costo_corrente + costo,
                prezzi_settimana
            )

            # Backtracking
            sequenza_parziale.pop()
    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        prezzi_settimana = {}

        for distributore in self._distributori:
            prezzi = distributore.get_prezzi()
            prezzi_giorni = []

            for prezzo in prezzi:
                if prezzo.data.month == mese and prezzo.data.day <= 7:
                    prezzi_giorni.append(prezzo.prezzo_litro)

            prezzi_settimana[distributore.id] = prezzi_giorni

        return prezzi_settimana