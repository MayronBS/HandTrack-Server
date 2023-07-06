import mediapipe
import cv2
import time
import socket
import PySimpleGUI as sg


class HandTrackServer:
    def __init__(self):
        self.HOST = ''
        self.port = 55555
        self.camWidth, self.camHeight = 640, 480
        self.marginSide, self.marginTop, self.marginDown = 110, 50, 150
        self.run: bool = True
        self.detecConfidence = 0.5
        self.trackConfidence = 0.1
        self.drawHands: bool = True
        self.sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def runServer(self):
        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        drawingModule = mediapipe.solutions.drawing_utils
        handsModule = mediapipe.solutions.hands
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sk = sk
        try:
            self.sk.bind((self.HOST, self.port))
            print('servidor local iniciado na porta: ', self.port)
            sg.popup_no_buttons('servidor local iniciado! Esperando conexão...')
        except:
            self.sk.close()
            print('erro ao iniciar servidor!')
            sg.popup_no_buttons('erro ao iniciar servidor!')
            return
        self.sk.listen(2)

        with handsModule.Hands(static_image_mode=False, min_detection_confidence=self.detecConfidence,
                               min_tracking_confidence=self.trackConfidence,
                               max_num_hands=1) as hands:
            while self.run:
                print('esperando conexão...')
                conn, endereco = self.sk.accept()
                print('conectado!')

                while self.run:
                    ret, frame = cap.read()
                    frame1 = cv2.resize(frame, (self.camWidth, self.camHeight))
                    results = hands.process(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))
                    coordList = []

                    if results.multi_hand_landmarks != None:
                        for handLandmarks in results.multi_hand_landmarks:
                            if self.drawHands:
                                drawingModule.draw_landmarks(frame1, handLandmarks, handsModule.HAND_CONNECTIONS)
                            for point in handsModule.HandLandmark:
                                normalizedLandmark = handLandmarks.landmark[point]
                                coordX, coordY = int(normalizedLandmark.x * self.camWidth), int(
                                    normalizedLandmark.y * self.camHeight)
                                coordList.append([int(point), coordX, coordY])

                        coords = str(coordList)
                        try:
                            conn.send(coords.encode())
                        except:
                            conn.close()
                            break

                    cv2.imshow("Frame", frame1)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        cv2.destroyAllWindows()
                        conn.close()
                        self.sk.detach()
                        self.run = False
            conn.close()
        self.sk.close()

    def setDetecConfidence(self, value: int):
        if value > 0:
            self.detecConfidence = value / 10

    def setTrackcConfidence(self, value: int):
        if value > 0:
            self.trackConfidence = value / 10

# cv2.rectangle(frame1, (marginSide, marginTop), (camWidth - marginSide, camHeight - marginDown), (255, 0, 0), 1)