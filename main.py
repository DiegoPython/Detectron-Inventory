from Detector import *

def main():
    detector = Detector(model_type="LVIS")
    # detector.onCamera()
    detector.onImage("./test/apples_a2.jpeg")


if __name__ == "__main__":
    main()
