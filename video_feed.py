import cv2
import time
import serial
import serial.tools.list_ports
import numpy as np

def take_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("Ошибка: Не найдено последовательных портов.")
        return None
    print(f"Найден последовательный порт: {ports[0].device}")
    return ports[0].device


def take_photo():
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise Exception("Не удалось открыть USB-камеру")

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        time.sleep(0.1)
        ret, frame = cap.read()

        if not ret:
            raise Exception("Не удалось прочитать кадр с камеры")

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cap.release()

        return image
    except Exception as e:
        print(f"Ошибка при захвате изображения: {e}")
        return None


def save_photo(im, image_name):
    try:
        cv2.imwrite(image_name, im)
        print(f"Изображение сохранено в {image_name}")
    except Exception as e:
        print(f"Ошибка при сохранении изображения: {e}")

now_in_parking = set()

def process_parking_cell_data(qr_value):
    car1 = 'машина1'
    car2 = 'машина2'
    car3 = 'машина3'
    car4 = 'машина4'
    car5 = 'машина5'
    car6 = 'машина6'
    parking = {
        car1: ['0', '90'],
        car2: ['0', '180'],
        car3: ['1', '90'],
        car4: ['1', '180'],
        car5: ['2', '90'],
        car6: ['2', '180']
    }

    if qr_value not in parking:
        print(f"Ошибка: Неизвестное значение QR-кода: {qr_value}")
        return None

    message = parking[qr_value].copy()
    message = '.'.join(message)
    if qr_value in now_in_parking:
        message += '+return'
        now_in_parking.remove(qr_value)
        print(message)
    else:
        message += '+insert'
        now_in_parking.add(qr_value)
        print(message)

    return message


def scan_qrcode(image):
    try:
        qrDecoder = cv2.QRCodeDetector()
        data, _, _ = qrDecoder.detectAndDecode(image)
        return data
    except Exception as e:
        print(f"Ошибка при сканировании QR-кода: {e}")
        return ""


if __name__ == '__main__':
    serial_port = take_port()
    if not serial_port:
        exit()

    while True:
        im = take_photo()
        if im is None:
            time.sleep(1)
            continue
        data = scan_qrcode(im)
        if data:
            try:
                ser = serial.Serial(serial_port, 9600)
                start_time = time.time()
                while not ser.is_open and time.time() - start_time < 5:
                    time.sleep(0.1)
                if not ser.is_open:
                    raise serial.SerialException("Таймаут ожидания открытия последовательного порта")

                message = process_parking_cell_data(data)
                if message:
                    ser.write(message.encode('utf-8'))
                    print(f"Отправлено сообщение: {message}")
                else:
                    print("Сообщение не отправлено из-за ошибки обработки")

                ser.close()
                data = ""
            except serial.SerialException as e:
                print(f"Ошибка связи по последовательному порту: {e}")
            except Exception as e:
                print(f"Произошла непредвиденная ошибка: {e}")

        time.sleep(2)
