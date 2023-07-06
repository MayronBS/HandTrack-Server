import PySimpleGUI as sg
from servidor import HandTrackServer


class MenuScreen:

    def __init__(self):
        sg.change_look_and_feel('Default1')
        self.run: bool =True
        layout = [

            [sg.Text('Porta:'), sg.Spin([i for i in range(10000, 55600)], initial_value=55555, key='porta', size=(5, 0),
                                        auto_size_text=False)],
            [sg.Text('Confiança de detecção:'),
             sg.Spin([i for i in range(1, 9)], initial_value=6, key='detec', size=(2, 0))],
            [sg.Text('Confiança de rastreio:'),
             sg.Spin([i for i in range(1, 9)], initial_value=1, key='track', size=(2, 0))],
            [sg.Checkbox('Desenhar contornos:', default=True, key='drawhands')],
            [sg.Button('Start', key='_START_')]
        ]

        self.janela = sg.Window("Hand Track", element_padding=12).layout(layout)

    def initScreen(self, hts: HandTrackServer):
        self.event, self.values = self.janela.read()
        if self.event == sg.WIN_CLOSED:
            self.run = False
            hts.sk.close()
            self.janela.close()
            return
        elif self.event == '_START_':
            hts.setDetecConfidence(int(self.values['detec']))
            hts.setTrackcConfidence(int(self.values['track']))
            hts.drawHands = self.values['drawhands']
            hts.port = int(self.values['porta'])
            hts.run = True
            hts.runServer()
            return


screen = MenuScreen()
hts = HandTrackServer()
while screen.run:
    screen.initScreen(hts)
